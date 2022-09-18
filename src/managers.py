import imp
from src.clients import JiraClient

class ReportManager:
    def __init__(self, jira_client: JiraClient) -> None:
        self.jira_client = jira_client

    def get_report(self) -> None:
        self.jira_client.test()
