import collections
import datetime

from typing import List, Dict

from src.crawlers import ProjectCrawler
from src.entities import JiraTask, ReportedEpic
from src.handlers import ScreenOutputHandler, CSVOutputHandler

from src.utils import CustomLogger


class ReportManager:
    def __init__(self,
                 project_crawler:
                 ProjectCrawler,
                 screen_output_handler_factory: ScreenOutputHandler,
                 csv_output_handler_factory: CSVOutputHandler,
                 logger: CustomLogger) -> None:
        self._project_crawler = project_crawler
        self._screen_output_handler_factory = screen_output_handler_factory
        self._csv_output_handler_factory = csv_output_handler_factory
        self._logger = logger()

    def group_tasks_by_assignee(self, tasks: List[JiraTask]) -> Dict[str, List[JiraTask]]:
        self._logger.info('Grouping Tasks by Assignee')
        grouped_tasks = collections.defaultdict(list)
        for task in tasks:
            if task.issue_type in ['Task', 'Story']:
                grouped_tasks[task.assignee].append(task)
        return grouped_tasks

    def group_epics_by_assignee(self, grouped_tasks: Dict[str, List[JiraTask]]) -> Dict[str, List[ReportedEpic]]:
        self._logger.info('Calculating Total per Epic')
        grouped_epics = collections.defaultdict(list)
        for assignee, tasks in grouped_tasks.items():
            epics_by_key = dict()
            for task in tasks:
                if epics_by_key.get(task.epic.key, None):
                    epics_by_key[task.epic.key].tasks.append(task)
                else:
                    epics_by_key[task.epic.key] = ReportedEpic(
                        key=task.epic.key,
                        summary=task.epic.summary,
                        project_name=task.epic.project_name,
                        benefit=task.epic.benefit,
                        created=task.epic.created,
                        updated=task.epic.updated,
                        resolved=task.epic.resolved,
                        tasks=[task]
                    )
            sorted_epics = sorted(epics_by_key.values(),
                                  key=lambda e: (e.time_spent(), e.story_points()),
                                  reverse=True)
            grouped_epics[assignee].extend(sorted_epics)
        return grouped_epics

    def get_report(self,
                   project_key: str,
                   start_date: datetime.date,
                   end_date: datetime.date,
                   output_format: str,
                   story_points: bool) -> None:
        tasks = self._project_crawler.crawl_tasks(project_key=project_key, start_date=start_date, end_date=end_date)

        grouped_tasks = self.group_tasks_by_assignee(tasks=tasks)
        grouped_epics = self.group_epics_by_assignee(grouped_tasks=grouped_tasks)

        handler = getattr(self, f'_{output_format}_output_handler_factory')(grouped_epics=grouped_epics,
                                                                            story_points=story_points)

        handler.build()
        handler.output()
