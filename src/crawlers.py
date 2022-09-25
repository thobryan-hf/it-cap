import collections
import datetime

from src.entities import JiraEpic, JiraTask
from typing import Optional, List
from src.clients import JiraClient, Project
from src.utils import CustomLogger
from src.exceptions import ProjectNotFound


class ProjectCrawler:
    def __init__(self, jira_client: JiraClient, logger: CustomLogger) -> None:
        self._jira_client = jira_client
        self._logger = logger()
        self._project: Optional[Project] = None

    def get_project_lead(self) -> str:
        return self._project.lead.displayName

    def crawl_tasks(self, project_key: str, start_date: datetime.date, end_date: datetime.date) -> List[JiraTask]:
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
        return tasks
