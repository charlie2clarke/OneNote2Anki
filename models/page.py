from datetime import datetime
from dataclasses import dataclass


@dataclass
class Page:
    id: str
    title: str
    last_modified_date_time: datetime