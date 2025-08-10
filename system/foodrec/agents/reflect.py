# 13.06.2025 @Noah Meissner

"""
Agent responsible for judging the corectness of the answer given by the Manager
Criticies the Manager or says its enough
"""
from foodrec.agents.agent import Agent
from typing import Set
from foodrec.agents.agent_state import AgentState
import json
from foodrec.config.prompts.load_prompt import get_prompt, PromptEnum
from foodrec.utils.multi_agent.get_model import get_model
from foodrec.utils.multi_agent.output import output_reflector


class ReflectorAgent(Agent):
    """Agent zur Reflexion und Qualitätsbewertung"""
    
    def __init__(self):
        super().__init__("Reflector")
    
    def _define_requirements(self) -> Set[str]:
        return {}
    
    def _define_provides(self) -> Set[str]:
        return {"feedback", "is_final"}
    

    def _create_reflection_prompt(self, state:AgentState) -> str:
        candidate_answer = state.get("candidate_answer", "")
        run_count = state.run_count
        user_query = state.query
        analysis_data = state.analysis_data
        search_results = state.item_analysis
        context_info = []
        if user_query:
            context_info.append(f"Original user query: {user_query}")
        if analysis_data:
            context_info.append(f"User analysis data: {json.dumps(analysis_data, indent=2)}")
        if search_results:
            context_info.append(f"Available search results: {search_results}")
        
        context_section = "\n".join(context_info) if context_info else "No additional context available."
        prompt = get_prompt(PromptEnum.REFLECTOR,state.biase)
        prompt = prompt.replace("$context_section$", str(context_section))
        prompt = prompt.replace("$run_count$", str(run_count))
        prompt = prompt.replace("$candidate_answer$",str(candidate_answer))
        return prompt
    
    def _parse_llm_response(self, response: str) -> tuple[bool, bool, str]:
        """Parsed die JSON-Antwort vom LLM und extrahiert Entscheidung und Feedback"""
        
        try:
            # Versuche JSON zu parsen
            # Manchmal fügt das LLM zusätzlichen Text hinzu, also extrahiere nur den JSON-Teil
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                
                decision = result.get("DECISION", "ACCEPT").upper()
                reasoning = result.get("REASONING", "")
                feedback = result.get("FEEDBACK", "")

                # Kombiniere Reasoning und Feedback für vollständiges Feedback
                combined_feedback = f"{reasoning}"
                if feedback and feedback != reasoning:
                    combined_feedback += f" | Suggestions: {feedback}"
                
                is_final = (decision == "ACCEPT")
                should_continue = (decision == "REJECT")  # Continue if rejected
                return is_final, should_continue, combined_feedback
                
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"❗️ JSON parsing failed: {e}")
            
            if "ACCEPT" in response.upper():
                is_final = True
                should_continue = False
                feedback = "Answer accepted (❗️ JSON parsing failed, used text fallback)"
            elif "REJECT" in response.upper():
                is_final = False  
                should_continue = True
                feedback = "Answer rejected (❗️ JSON parsing failed, used text fallback)"
            else:
                # Default fallback
                is_final = True
                should_continue = False
                feedback = "❗️ Could not parse LLM response, defaulting to accept"
            
        return is_final, should_continue, feedback

    def _execute_logic(self, state: AgentState) -> AgentState:
        run_count = state.get("run_count", 1)
        candidate_answer = state.get("candidate_answer", "")
        
        prompt = self._create_reflection_prompt(state)
        model = get_model(state.model)
        try:
            llm_response = model(prompt)
            is_final, should_continue, feedback = self._parse_llm_response(llm_response)
            
            # Sicherheitscheck: Nach 8 Iterationen immer akzeptieren
            if run_count >= 8:
                is_final = True
                should_continue = False
                if should_continue:  # Falls LLM noch reject wollte
                    feedback += " (Accepting due to maximum iterations reached)"
            
        except Exception as e:
            print(f"{self.name}: Error calling LLM: {e}")
            is_final = run_count >= 3 or len(candidate_answer) > 50
            should_continue = not is_final
            feedback = f"❗️ LLM evaluation failed, using fallback logic. Final: {is_final}"
        
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
        state.feedback = feedback
        state.messages = state.get("messages", []) + [
            f"{self.name}: {decision_status} - {feedback}"
        ]
        state.last_completed_agent = "reflector"
        output_reflector(is_final==is_final,should_continue=should_continue, feedback=feedback)
        return state

