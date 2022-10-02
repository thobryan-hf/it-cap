import csv

from src.utils import CustomLogger
from prettytable import PrettyTable

from typing import Dict, List

from src.entities import ReportedEpic

REPORT_FIELDS = ['Assignee', 'Epic Key', 'Epic Name', 'Benefit', 'Days Spent']
DETAILED_REPORT_FIELDS = ['Assignee', 'Epic Key', 'Task Key', 'Task Type', 'Task Name', 'Days Spent', 'Updated',
                          'Resolved']


class OutputHandler:
    def __init__(self, grouped_epics: Dict[str, List[ReportedEpic]], story_points: bool, logger: CustomLogger) -> None:
        self._report_rows: List[List[str]] = [REPORT_FIELDS]
        self._detailed_report_rows: List[List[str]] = [DETAILED_REPORT_FIELDS]
        self._grouped_epics = grouped_epics
        self._story_points = story_points
        self._logger = logger()

    def build(self) -> None:
        self._logger.info('Building rows...')

        for assignee, epics in self._grouped_epics.items():
            for epic in epics:
                self._report_rows.append([
                    assignee,
                    epic.key,
                    epic.summary,
                    ','.join(epic.benefit),
                    epic.story_points() if self._story_points else epic.time_spent()
                ])
                for task in epic.tasks:
                    self._detailed_report_rows.append([
                        assignee,
                        epic.key,
                        task.key,
                        task.issue_type,
                        task.summary,
                        task.story_points if self._story_points else task.days_spent(),
                        task.updated,
                        task.resolved
                    ])


class ScreenOutputHandler(OutputHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def output(self) -> None:
        self._logger.info('Printing reports on the screen')
        report_table = PrettyTable()
        report_table.field_names = self._report_rows[0]
        report_table.add_rows(self._report_rows[1:])
        print('Epics Report')
        print(report_table)

        detailed_report_table = PrettyTable()
        detailed_report_table.field_names = self._detailed_report_rows[0]
        detailed_report_table.add_rows(self._detailed_report_rows[1:])
        print('Tasks Report')
        print(detailed_report_table)


class CSVOutputHandler(OutputHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def output(self) -> None:
        self._logger.info('Writing report to csv')
        with open('report.csv', 'w') as csvfile:
            report_writer = csv.writer(csvfile, dialect='excel')
            report_writer.writerows(self._report_rows)

        with open('detailed_report.csv', 'w') as csvfile:
            report_writer = csv.writer(csvfile, dialect='excel')
            report_writer.writerows(self._detailed_report_rows)
