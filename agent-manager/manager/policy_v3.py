from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
class Decision(str,Enum): ALLOW="ALLOW"; DENY="DENY"; REQUIRE_REVIEW="REQUIRE_REVIEW"; REQUIRE_USER="REQUIRE_USER"
@dataclass
class PolicyResult: decision:Decision; risk:str; reason:str
DESTRUCTIVE={"delete_database","drop_table","rotate_credentials","change_permissions","payment_change"}
LOW={"restart_worker","retry_job","clear_stale_cache","reconnect_local_service"}
def evaluate(action:str,*,touches_auth=False,touches_payment=False,destructive=False)->PolicyResult:
    a=action.lower().strip()
    if destructive or a in DESTRUCTIVE: return PolicyResult(Decision.REQUIRE_USER,"critical","Destructive/auth/payment-sensitive operation requires explicit human approval.")
    if touches_auth or touches_payment: return PolicyResult(Decision.REQUIRE_USER,"high","Authentication/payment scope requires explicit human approval.")
    if a in LOW: return PolicyResult(Decision.ALLOW,"low","Reversible runtime recovery action.")
    if "source" in a or "patch" in a or "deploy" in a: return PolicyResult(Decision.REQUIRE_REVIEW,"medium","Source/deployment changes require sandbox tests and independent review.")
    return PolicyResult(Decision.REQUIRE_REVIEW,"medium","Unknown action defaults to review.")
