from manager.policy_v3 import evaluate
def test_safe_restart_allowed(): assert evaluate("restart_worker").decision.value=="ALLOW"
def test_patch_requires_review(): assert evaluate("source_patch").decision.value=="REQUIRE_REVIEW"
def test_destructive_requires_user(): assert evaluate("delete_database").decision.value=="REQUIRE_USER"
