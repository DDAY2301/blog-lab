from __future__ import annotations
import argparse,time
from datetime import datetime,timezone
from .db_v3 import StoreV3
from .settings_v3 import SettingsV3
class GuardianV3:
    def __init__(self,s:SettingsV3,store:StoreV3): self.s=s; self.store=store
    def manager_fresh(self,max_age:int=100)->bool:
        rows=self.store.query("SELECT ts FROM heartbeats WHERE component='manager'")
        if not rows:return False
        try: return (datetime.now(timezone.utc)-datetime.fromisoformat(rows[0]["ts"])).total_seconds()<=max_age
        except Exception:return False
    def cycle(self)->dict:
        self.store.heartbeat("guardian","running"); ok=self.manager_fresh(max(90,self.s.monitor_interval*2+20))
        if not ok:self.store.event("MANAGER_UNRESPONSIVE","guardian","critical",{})
        return {"manager_heartbeat_fresh":ok}
def main():
    s=SettingsV3(); st=StoreV3(s.db_path); g=GuardianV3(s,st); p=argparse.ArgumentParser(); p.add_argument("--once",action="store_true"); a=p.parse_args()
    while True:
        print(g.cycle(),flush=True)
        if a.once:return
        time.sleep(s.heartbeat_interval)
if __name__=="__main__": main()
