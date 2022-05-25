from dataclasses import dataclass
from datetime import datetime


@dataclass
class Section:
    id: str
    name: str
    is_default: bool
    last_modified_date_time: datetime
    pages_url: str
