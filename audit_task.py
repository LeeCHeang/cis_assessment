from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict

@dataclass
class AuditTask:
    # id: str
    # title: str
    # check_type: str
    # target: str
    # parameters: Union[Dict, List]
    # algorithm: str
    # expected_value: str
    id: str
    level: str
    profile: List[str]
    domain: str
    title: str
    check_type: str
    target: str
    parameters: Union[Dict, List]
    algorithm: str
    expected_value: str

    status: str = "PENDING"
    actual_output: Optional[str] = None
    final_result: Optional[str] = None # PASS / FAIL / ERROR