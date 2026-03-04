# src/chat_history.py

class ChatHistory:
    """
    Gère la mémoire court-terme de la conversation
    Évite les répétitions de questions
    """
    
    def __init__(self, system_prompt):
        self.messages = [{"role": "system", "content": system_prompt}]
    
    def add_message(self, role, content):
        """Ajoute un message à l'historique"""
        self.messages.append({"role": role, "content": content})
    
    def get_messages(self):
        """Retourne tous les messages pour le LLM"""
        return self.messages
    
    def get_text(self):
        """Retourne la conversation en texte lisible"""
        text = ""
        for msg in self.messages[1:]:  # Skip system
            prefix = "🤖" if msg['role'] == 'assistant' else "👤"
            text += f"{prefix} : {msg['content']}\n\n"
        return text.strip()