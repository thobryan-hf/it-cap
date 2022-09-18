import collections
import datetime

from entities import JiraEpic, JiraTask
from typing import Any, Optional, List, Dict
from src.clients import JiraClient, Project
from src.utils import CustomLogger
from src.exceptions import ProjectNotFound


class ProjectCrawler:
    def __init__(self, jira_client: JiraClient, logger: CustomLogger) -> None:
        self._jira_client = jira_client
        self._logger = logger()
        self._project: Optional[Project] = None

    def group_tasks_by_assignee(self, tasks: List[JiraTask]) -> Dict[str, List[JiraTask]]:
        self._logger.info('Grouping Tasks by Asignee')
        grouped_tasks = collections.defaultdict(list)
        for task in tasks:
            if task.issue_type == 'Task':
                grouped_tasks[task.assignee].append(task)
        return grouped_tasks

    def get_project_lead(self) -> str:
        return self._project.lead.displayName

    def crawl_report(self, project_key: str, start_date: datetime.date, end_date: datetime.date) -> Optional[Any]:
        self._logger.info('Crawling Report')
        try:
            self._project = self._jira_client.get_project(project_key=project_key)
        except ProjectNotFound as e:
            raise e

        epics: List[JiraEpic] = self._jira_client.get_capitalizable_epics(project_key=project_key)

        tasks: List[JiraTask] = []
        for epic in epics:
            task = self._jira_client.get_tasks(
                project_key=project_key,
                start_date=start_date,
                end_date=end_date,
                epic=epic
            )
            tasks.extend(task)

        # TODO this class might be outside the crawler
        grouped_tasks = self.group_tasks_by_assignee(tasks=tasks)
        # TODO: Need to finalise the total per epic/assignee
        pass
