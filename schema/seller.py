from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SellerDetailSchema:
    seller_name: str =  ""
    seller_score: str = ""
    return_policy: Optional[str] = ""
    shipping_info: Optional[str] = ""
    performance_metrics: List[str] | None = field(default_factory=list)

