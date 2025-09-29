# 13.06.2025 @Noah Meissner

"""
Agent responsible for judging the corectness of the answer given by the Manager
Criticies the Manager or says its enough
"""
from typing import Set
import json
from foodrec.agents.agent import Agent
from foodrec.agents.agent_state import AgentState
from foodrec.config.prompts.load_prompt import get_prompt, PromptEnum
from foodrec.utils.multi_agent.get_model import get_model
from foodrec.utils.multi_agent.output import output_reflector
from foodrec.agents.agent_names import AgentEnum, AgentReporter
from foodrec.tools.conversation_manager import record
from foodrec.utils.multi_agent.swap_recipe_list import get_list


class ReflectorAgent(Agent):
    """Agent responsible for reflecting on and scoring the Manager's answer.

    It decides whether to accept the candidate answer or request another iteration,
    and attaches feedback for further improvement if needed.
    """
    def __init__(self):
        super().__init__(AgentEnum.REFLECTOR.value)
        self.max_runs = 4

    def _define_requirements(self) -> Set[str]:
        return {}

    def _define_provides(self) -> Set[str]:
        return {"feedback", "is_final"}

    def create_context_section(self, state: AgentState) -> str:
        """Creates a context section for the prompt including user query,
          analysis data, and search results.
        """
        user_query = state.query
        analysis_data = state.analysis_data
        search_results = get_list(state=state)
        context_info = []
        if user_query:
            context_info.append(f"Original user query: {user_query}")
        if analysis_data:
            context_info.append(f"User analysis data: {json.dumps(analysis_data, indent=2)}")
        if search_results:
            context_info.append(f"Recommended Recipes: {search_results}")
        context_section = (
            "\n".join(context_info)
            if context_info
            else "No additional context available."
        )
        return context_section


    def _create_reflection_prompt(self, state:AgentState) -> str:
        """Creates the prompt for the reflector agent."""
        context_section = self.create_context_section(state)
        prompt = get_prompt(PromptEnum.REFLECTOR,state.biase)
        prompt = prompt.replace("$context_section$", str(context_section))
        prompt = prompt.replace("$run_count$", str(state.run_count))
        prompt = prompt.replace("$candidate_answer$",str(state.candidate_answer))
        record(AgentReporter.REFLECTOR_Prompt.name, prompt)
        return prompt

    def parse_json(self, response: str) -> dict:
        """Extracts JSON object from LLM response string."""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                return result
        except (json.JSONDecodeError, ValueError) as exception:
            print(f"❗️ JSON parsing failed: {exception}")
        is_final = False
        feedback = "❗️ Could not parse LLM response, defaulting to reject"
        if "ACCEPT" in response.upper():
            is_final = True
            feedback = "Answer accepted (JSON parsing failed, used text fallback)"
        elif "REJECT" in response.upper():
            is_final = False
            feedback = "Answer rejected (JSON parsing failed, used text fallback)"
        else:
            is_final = True
            feedback = "Could not parse LLM response, defaulting to accept"
        return {"DECISION": "ACCEPT" if is_final else "REJECT",
                    "REASONING": "Fallback due to parsing error",
                    "FEEDBACK": feedback}


    def _parse_llm_response(self, response: str) -> tuple[bool, bool, str]:
        result = self.parse_json(response)
        decision = result.get("DECISION", "ACCEPT").upper()
        reasoning = result.get("REASONING", "")
        feedback = result.get("FEEDBACK", "")

        if feedback is None:
            feedback = "No Feedback"

        should_continue = decision == "REJECT"
        is_final = not should_continue
        record(AgentReporter.REFLECTOR.name,
                feedback,
                  {'decision': decision, 'reasoning': reasoning, 'feedback':feedback})
        return is_final, should_continue, feedback


    def _execute_logic(self, state: AgentState) -> AgentState:
        run_count = state.run_count
        candidate_answer = state.get("candidate_answer", "")
        if isinstance(state.item_analysis, str):
            is_final = False
            should_continue = True
            feedback = state.item_analysis
            if state.run_count >= self.max_runs:
                is_final = True
                should_continue = False
                feedback += " (Accepting due to maximum iterations reached)"

        else:
            prompt = self._create_reflection_prompt(state)
            model = get_model(state.model)
            try:
                llm_response = model(prompt)
                is_final, should_continue, feedback = self._parse_llm_response(llm_response)
                print(f"is_final {is_final}")
                if run_count >= self.max_runs:
                    is_final = True
                    if not should_continue:
                        should_continue = False
                        feedback += " (Accepting due to maximum iterations reached)"

            except Exception as exception: # pylint: disable=broad-exception-caught
                print(f"{self.name}: Error calling LLM: {exception}")
                is_final = run_count >= self.max_runs or len(candidate_answer) > 50
                should_continue = not is_final
                feedback = f"❗️ LLM evaluation failed, using fallback logic. Final: {is_final}"
            print(f"is_final {is_final}")
            print(f"run_count {run_count}")

        state.is_final = is_final
        state.reflection_feedback = {
            "should_continue": should_continue,
            "feedback": feedback,
            "decision": "REJECT" if should_continue else "ACCEPT",
            "run_count": run_count
        }

        state.reflector_accepted = is_final
        decision_status = "ACCEPTED" if is_final else "REJECTED"
        state.run_count = run_count+1
        state.is_final = is_final
        state.feedback = feedback
        state.messages = state.get("messages", []) + [
            (self.name, f"{decision_status} - {feedback}")
        ]
        state.last_completed_agent = "reflector"
        output_reflector(is_final=is_final,should_continue=should_continue, feedback=feedback)
        return state
