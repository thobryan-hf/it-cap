import argparse
import datetime

from dependency_injector.wiring import Provide, inject
from src.containers import Container
from src.managers import ReportManager
from src.utils import ParseUtils


@inject
def main(project_key: str,
         start_date: datetime.date,
         end_date: datetime.date,
         output_format: str,
         story_points: bool,
         report_manager: ReportManager = Provide[Container.report_manager]) -> None:
    report_manager.get_report(project_key=project_key,
                              start_date=start_date,
                              end_date=end_date,
                              output_format=output_format,
                              story_points=story_points)


def run() -> None:
    parser = argparse.ArgumentParser(description='HelloFresh IT Cap Script')
    parser.add_argument('--project',
                        dest='project_key',
                        required=True,
                        type=str.upper,
                        help='Jira Project Key')
    parser.add_argument('--period',
                        required=True,
                        type=ParseUtils.parse_dates,
                        help='Month and year to calculate IT Cap. eg 09/2022')
    parser.add_argument('--output',
                        required=False,
                        type=str.lower,
                        dest='output_format',
                        default='screen',
                        choices=['screen', 'csv'],
                        help='Output format of the report')
    parser.add_argument('--story-points',
                        dest='story_points',
                        action='store_true',
                        default=False,
                        help='Use story points instead of spent time')
    args = parser.parse_args()
    container = Container()
    container.wire(modules=[__name__])
    start_date, end_date = args.period
    main(project_key=args.project_key,
         start_date=start_date,
         end_date=end_date,
         output_format=args.output_format,
         story_points=args.story_points)


if __name__ == "__main__":
    run()
