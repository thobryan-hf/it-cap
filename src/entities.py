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
    summary: str
    issue_type: str
    time_spent: str
    assignee: str
    updated: datetime
    resolved: datetime
    epic: JiraEpic

    def days_spent(self) -> float:
        return int(self.time_spent) / 28800


@dataclass
class ReportedEpic:
    key: str
    summary: str
    project_name: str
    benefit: List[str]
    created: datetime
    updated: datetime
    resolved: Optional[datetime]
    tasks: List[JiraTask]

    def time_spent(self) -> float:
        total = 0
        for task in self.tasks:
            total += task.days_spent()
        return total
