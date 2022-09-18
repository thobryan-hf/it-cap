import datetime
import functools
import logging

from typing import Dict, Optional, List
import pendulum

from src.entities import JiraEpic, JiraTask
from src.utils import CustomLogger
from jira import JIRA, JIRAError, Project, Issue
from src.exceptions import ProjectNotFound


class JiraClient(JIRA):
    def __init__(self, config: Dict[str, str], logger: CustomLogger) -> None:
        self._config = config
        self._logger = logger()
        super().__init__(**self.get_credentials())

    def get_credentials(self):
        return dict(
            server=self._config.get('server'),
            basic_auth=(self._config.get('email'), self._config.get('token'))
        )

    @functools.cache
    def get_project(self, project_key: str) -> Optional[Project]:
        try:
            return self.project(id=project_key)
        except JIRAError as e:
            logging.error(e.text)
            raise ProjectNotFound(e.text)

    def extract_raw_epic(self, issue: Issue) -> JiraEpic:
        self._logger.debug(f'Extracting details from Epic {issue.key}')
        if isinstance(issue.fields.customfield_12221, list):
            benefit = [b.value for b in issue.fields.customfield_12221]
        else:
            benefit = []
        return JiraEpic(
            key=issue.key,
            issue_type=issue.fields.issuetype.name,
            summary=issue.fields.summary,
            reporter=issue.fields.reporter.displayName,
            status=issue.fields.status.name,
            category=issue.fields.project.projectCategory.description,
            benefit=benefit,
            project_name=issue.fields.project.name,
            created=pendulum.parse(issue.fields.created),
            updated=pendulum.parse(issue.fields.updated),
            resolved=pendulum.parse(issue.fields.resolutiondate) if issue.fields.resolutiondate else None
        )

    @functools.cache
    def get_capitalizable_epics(self, project_key: str) -> List[JiraEpic]:
        self._logger.info('Fetching Capitalizable Epics')
        jql_str = f'PROJECT IN ({project_key}) AND ISSUETYPE = "Epic" AND "Is Capitalizable?" = "Yes"'
        epics = [self.extract_raw_epic(issue=issue) for issue in self.search_issues(jql_str=jql_str)]
        self._logger.info(f'Found {len(epics)} epics under {project_key}')
        return epics

    def extract_raw_task(self, issue: Issue, epic: JiraEpic) -> JiraTask:
        self._logger.debug(f'Extracting details from Task {issue.key}')
        return JiraTask(
            key=issue.key,
            issue_type=issue.fields.issuetype.name,
            time_spent=issue.fields.aggregatetimespent,  # TODO Add calculation using Story Points too
            assignee=str(issue.fields.assignee),
            updated=pendulum.parse(issue.fields.updated),
            resolved=pendulum.parse(issue.fields.resolutiondate) if issue.fields.resolutiondate else None,
            epic=epic
        )

    def get_tasks(self,
                  project_key: str,
                  start_date: datetime.date,
                  end_date: datetime.date,
                  epic: JiraEpic) -> List[JiraTask]:
        self._logger.info(f'Fetching Tasks for Epic {epic.key}')
        jql_str = (
            f'PROJECT IN ("{project_key}") AND ("EPIC LINK" = "{epic.key}" OR parentEpic = "{epic.key}") '
            f'AND resolved >= "{start_date}" '
            f'AND resolved <= "{end_date}"'
        )
        tasks = [self.extract_raw_task(issue=issue, epic=epic) for issue in self.search_issues(jql_str=jql_str)]
        self._logger.info(f'Found {len(tasks)} tasks under {epic.key}')
        return tasks
