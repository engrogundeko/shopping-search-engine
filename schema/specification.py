from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SpecificationsSchema:
    key_features: Optional[list[str]] = field(default_factory=list)
    box_contents: Optional[list[str]] = field(default_factory=list)
    color: Optional[str]  = ""
    weight: Optional[str]  = ""
    dimensions: Optional[str]  = ""
    material: Optional[str] = ""
    features: Optional[list[str]] = field(default_factory=list)
    brand: Optional[str] = ""
    specifications: Optional[dict] = field(default_factory=dict)
    html_content: str | None = ""
