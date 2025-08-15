# Noah Meissner 13.08.2025

'''
    This script calls the Multi Agent System
'''

from foodrec.agents.mulit_agent import MultiAgent
from foodrec.config.structure.dataset_enum import ModelEnum
from foodrec.tools.conversation_manager import ConversationSession, record
from foodrec.agents.mulit_agent import MultiAgent
from foodrec.config.structure.dataset_enum import ModelEnum
from foodrec.utils.data_preperation.check_elastic import check_Elastic

def run_query(prompt: str, chat_id: str = "chat-2025-08-11-noah",user_id:int = 1, biase: bool=False, model:ModelEnum = ModelEnum.Gemini) -> str:
    check_Elastic(biase=biase)
    with ConversationSession(chat_id):
        record("user", prompt)
        M = MultiAgent(user_id=user_id,biase=biase, model=model)
        try:
            answer = M.run(prompt)
            record("assistant", answer, meta={"source": "MultiAgent", "model": str(ModelEnum.Gemini)})
            return answer
        finally:
            if hasattr(M, "close"):
                try:
                    M.close()
                except Exception as e:
                    record("warn", f"MultiAgent.close failed: {e}")


