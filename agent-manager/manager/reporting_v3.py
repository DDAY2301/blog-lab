from __future__ import annotations
from .db_v3 import StoreV3,utcnow
from .settings_v3 import SettingsV3
class ReporterV3:
    def __init__(self,s:SettingsV3,store:StoreV3): self.s=s; self.store=store
    def queue(self,kind:str,subject:str,body:str,priority:int=50):
        self.store.execute("INSERT INTO email_queue(created_at,kind,priority,recipient,subject,body,status) VALUES(?,?,?,?,?,?,'pending')",(utcnow(),kind,priority,self.s.report_to or None,subject,body))
    def auth_state(self)->str:
        if not self.s.gmail_enabled:return "DISABLED"
        if not self.s.report_to or not self.s.gmail_token_file.exists():return "AUTH_REQUIRED"
        return "CONFIGURED"
