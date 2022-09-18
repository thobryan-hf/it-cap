from dependency_injector import containers, providers

from src.clients import JiraClient
 
 
class Container(containers.DeclarativeContainer):
    config = providers.Configuration(yaml_files=["config.yml"])

    jira_client = providers.Singleton(
        JiraClient,
        config=config.jira
    )
