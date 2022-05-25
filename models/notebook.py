from dataclasses import dataclass
from datetime import datetime


@dataclass
class Notebook:
    id: str
    name: str
    is_default: bool
    last_modified_date_time: datetime
    sections_url: str
