# agents/core/memory_manager.py

class SessionMemory:
    def __init__(self):
        self.last_intent = None
        self.last_email_results = None
        self.last_selected_email = None
        self.last_document_source = None
        self.last_reminder_action = None

    def set_intent(self, intent):
        self.last_intent = intent

    def set_email_results(self, results):
        self.last_email_results = results

    def set_selected_email(self, email):
        self.last_selected_email = email

    def set_document_source(self, source):
        self.last_document_source = source

    def set_reminder_action(self, action):
        self.last_reminder_action = action


# global session memory object
session_memory = SessionMemory()