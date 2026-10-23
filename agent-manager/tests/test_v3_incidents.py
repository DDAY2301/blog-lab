from manager.db_v3 import StoreV3
from manager.incidents_v3 import IncidentEngineV3
def test_incident_dedupe(tmp_path):
    st=StoreV3(tmp_path/"a.db"); inc=IncidentEngineV3(st)
    a=inc.raise_or_update("x","same","P2",["a"]); b=inc.raise_or_update("x","same","P1",["b"])
    row=st.query("SELECT * FROM incidents")[0]
    assert a["id"]==b["id"] and row["occurrence_count"]==2 and row["severity"]=="P1"
