import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from command import infer_mode

def test_infer_article(): assert infer_mode("Objavi članek o novem projektu") == "article"
def test_infer_control(): assert infer_mode("Ustavi objavljanje") == "control"
def test_infer_site(): assert infer_mode("Dodaj novo rubriko Projekti v meni") == "site"


def test_infer_schedule_control():
    assert infer_mode("sedaj pa nazaj na termine objav kot na začetku samostojna objava trikrat na dan") == "control"

def test_infer_automatic_schedule_control():
    assert infer_mode("Vrni samodejno objavljanje 3x na dan") == "control"


def test_infer_design_site():
    assert infer_mode("dodaj in polepšaj izgled strani") == "site"
