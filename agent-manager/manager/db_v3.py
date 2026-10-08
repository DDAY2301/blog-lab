from __future__ import annotations
import json, sqlite3, threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA="""
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS agents(id TEXT PRIMARY KEY,name TEXT NOT NULL,kind TEXT NOT NULL,root TEXT,status TEXT NOT NULL,health INTEGER NOT NULL DEFAULT 0,metadata TEXT NOT NULL DEFAULT '{}',first_seen TEXT NOT NULL,last_seen TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS dependencies(parent_id TEXT NOT NULL,child_id TEXT NOT NULL,relation TEXT NOT NULL,PRIMARY KEY(parent_id,child_id,relation));
CREATE TABLE IF NOT EXISTS heartbeats(component TEXT PRIMARY KEY,ts TEXT NOT NULL,status TEXT NOT NULL,loop_id TEXT);
CREATE TABLE IF NOT EXISTS incidents(id TEXT PRIMARY KEY,fingerprint TEXT NOT NULL UNIQUE,severity TEXT NOT NULL,status TEXT NOT NULL,component TEXT NOT NULL,title TEXT NOT NULL,evidence TEXT NOT NULL DEFAULT '[]',occurrence_count INTEGER NOT NULL DEFAULT 1,first_seen TEXT NOT NULL,last_seen TEXT NOT NULL,resolved_at TEXT);
CREATE TABLE IF NOT EXISTS incident_events(id INTEGER PRIMARY KEY AUTOINCREMENT,incident_id TEXT NOT NULL,ts TEXT NOT NULL,state TEXT NOT NULL,payload TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,ts TEXT NOT NULL,type TEXT NOT NULL,source TEXT NOT NULL,severity TEXT NOT NULL,payload TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS actions(id INTEGER PRIMARY KEY AUTOINCREMENT,ts TEXT NOT NULL,actor TEXT NOT NULL,action TEXT NOT NULL,target TEXT,result TEXT NOT NULL,payload TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS email_queue(id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT NOT NULL,kind TEXT NOT NULL,priority INTEGER NOT NULL,recipient TEXT,subject TEXT NOT NULL,body TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending',attempts INTEGER NOT NULL DEFAULT 0,last_error TEXT);
CREATE TABLE IF NOT EXISTS lessons(id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT NOT NULL,pattern TEXT NOT NULL,successful_recovery TEXT,avoid TEXT,confidence REAL NOT NULL DEFAULT 0.5,last_verified TEXT);
CREATE TABLE IF NOT EXISTS managed_target_status(target_id TEXT PRIMARY KEY,name TEXT NOT NULL,kind TEXT NOT NULL,ok INTEGER NOT NULL DEFAULT 0,last_check TEXT NOT NULL,details TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT NOT NULL,severity TEXT NOT NULL,source TEXT NOT NULL,title TEXT NOT NULL,body TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'new');
CREATE TABLE IF NOT EXISTS mail_commands(message_id TEXT PRIMARY KEY,thread_id TEXT,sender TEXT NOT NULL,subject TEXT NOT NULL,target TEXT NOT NULL,command_text TEXT NOT NULL,status TEXT NOT NULL,received_at TEXT NOT NULL,processed_at TEXT,result TEXT,error TEXT,reply_message_id TEXT);
"""
def utcnow()->str: return datetime.now(timezone.utc).isoformat()

class StoreV3:
    def __init__(self,path:Path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self._lock=threading.RLock(); self.init()
    @contextmanager
    def conn(self):
        with self._lock:
            con=sqlite3.connect(self.path,timeout=30); con.row_factory=sqlite3.Row
            try: yield con; con.commit()
            finally: con.close()
    def init(self):
        with self.conn() as c: c.executescript(SCHEMA)
    def execute(self,sql:str,params:tuple=()):
        with self.conn() as c: c.execute(sql,params)
    def query(self,sql:str,params:tuple=())->list[dict[str,Any]]:
        with self.conn() as c: return [dict(r) for r in c.execute(sql,params).fetchall()]
    def heartbeat(self,component:str,status:str="running",loop_id:str=""):
        self.execute("INSERT INTO heartbeats(component,ts,status,loop_id) VALUES(?,?,?,?) ON CONFLICT(component) DO UPDATE SET ts=excluded.ts,status=excluded.status,loop_id=excluded.loop_id",(component,utcnow(),status,loop_id))
    def event(self,typ:str,source:str,severity:str="info",payload:dict|None=None):
        self.execute("INSERT INTO events(ts,type,source,severity,payload) VALUES(?,?,?,?,?)",(utcnow(),typ,source,severity,json.dumps(payload or {},ensure_ascii=False)))
    def action(self,actor:str,action:str,target:str|None,result:str,payload:dict|None=None):
        self.execute("INSERT INTO actions(ts,actor,action,target,result,payload) VALUES(?,?,?,?,?,?)",(utcnow(),actor,action,target,result,json.dumps(payload or {},ensure_ascii=False)))
