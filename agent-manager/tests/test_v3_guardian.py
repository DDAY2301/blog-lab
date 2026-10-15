from manager.db_v3 import StoreV3
from manager.guardian_v3 import GuardianV3
from manager.settings_v3 import SettingsV3
def test_guardian_fresh(tmp_path):
    s=SettingsV3(db_path=tmp_path/"a.db"); st=StoreV3(s.db_path); st.heartbeat("manager")
    assert GuardianV3(s,st).manager_fresh()
