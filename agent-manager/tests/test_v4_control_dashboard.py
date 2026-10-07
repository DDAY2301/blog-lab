import asyncio

from manager.service_v3 import control


def test_control_dashboard_keeps_linebreak_regex_escaped():
    response = asyncio.run(control())
    html = response.body.decode("utf-8")
    assert r".split(/\r?\n/)" in html
    bad = ".split(/" + chr(13) + "?" + chr(10) + "/)"
    assert bad not in html
