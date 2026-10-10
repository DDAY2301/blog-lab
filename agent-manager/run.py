from __future__ import annotations
import uvicorn
from manager.settings_v3 import SettingsV3
if __name__=="__main__":
    s=SettingsV3()
    uvicorn.run("manager.service_v3:app",host=s.host,port=s.port,reload=False)
