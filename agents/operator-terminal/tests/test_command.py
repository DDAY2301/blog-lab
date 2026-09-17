import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from command import infer_mode

def test_infer_article(): assert infer_mode("Objavi članek o novem projektu") == "article"
def test_infer_control(): assert infer_mode("Ustavi objavljanje") == "control"
def test_infer_site(): assert infer_mode("Dodaj novo rubriko Projekti v meni") == "site"
