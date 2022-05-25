from datetime import datetime
from dataclasses import dataclass


@dataclass
class Page:
    id: str
    name: str
    is_default: bool
    last_modified_date_time: datetime
    notebook_id: str
    section_id: str
    content: str