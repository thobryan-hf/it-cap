from typing import List, Optional

from dataclasses import dataclass
from datetime import datetime


@dataclass
class JiraEpic:
    key: str
    issue_type: str
    summary: str
    reporter: str
    status: str
    category: str
    project_name: str
    benefit: List[str]
    created: datetime
    updated: datetime
    resolved: Optional[datetime]


@dataclass
class JiraTask:
    key: str
    issue_type: str
    time_spent: str
    assignee: str
    updated: datetime
    resolved: datetime
    epic: JiraEpic
