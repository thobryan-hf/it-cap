import argparse

from dependency_injector.wiring import Provide, inject
from src.containers import Container
from src.clients import JiraClient

@inject
def main(project_key: str, period: str, output_format: str, jira_client: JiraClient = Provide[Container.jira_client]) -> None:
    jira_client.test()

def run() -> None:
    parser = argparse.ArgumentParser(description='HelloFresh IT Cap Script')
    parser.add_argument('--project', dest='project_key', required=True, type=str.upper, help='Jira Project Key')
    parser.add_argument('--period', required=True, help='Month and year to calculate IT Cap. eg 09/2022')
    parser.add_argument('--output', required=False, dest='output_format', default='screen', choices=['screen', 'csv'])
    args = parser.parse_args()
    container = Container()
    container.wire(modules=[__name__])
    main(project_key=args.project_key, period=args.period, output_format=args.output_format)

if __name__ == "__main__":
    run()
