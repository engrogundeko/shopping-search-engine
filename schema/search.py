from dataclasses import dataclass
from typing import List, Dict

@dataclass
class TextSchema:
    text: str
    metadata: dict

@dataclass
class ContentSchema:
    contents: List[Dict[str, TextSchema]]

