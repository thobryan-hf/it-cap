import datetime
from typing import Tuple
from src.crawlers import ProjectCrawler


class ReportManager:
    def __init__(self, project_crawler: ProjectCrawler) -> None:
        self._project_crawler = project_crawler

    def get_report(self, project_key: str, start_date: datetime.date, end_date: datetime.date) -> None:
        report = self._project_crawler.crawl_report(project_key=project_key, start_date=start_date, end_date=end_date)
        if report:
            print('REPORT')
