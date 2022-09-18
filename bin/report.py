from dependency_injector.wiring import Provide, inject
from src.containers import Container
from src.clients import JiraClient

@inject
def main(jira_client: JiraClient = Provide[Container.jira_client]) -> None:
    jira_client.test()


def run() -> None:
    container = Container()
    container.wire(modules=[__name__])
    main()

if __name__ == "__main__":
    run()
