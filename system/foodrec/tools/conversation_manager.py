# Noah Meissner 11.08.2025

"""
    This manager is responsible for saving the chat for evaluation purposes
"""

from foodrec.config.structure.paths import CONVERSATION
import os
import json

class ConversationManager:

    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.conversation = []

    def add_message(self, message: dict = {}):
        self.conversation.append(message)
    
    def save_conversation(self):
        file_path = os.path.join(CONVERSATION, f"{self.chat_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.conversation, f, ensure_ascii=False, indent=4)
            print(f"✅ Conversation successfully saved to {file_path}")



