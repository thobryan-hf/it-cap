from typing import Callable
from dependency_injector import containers, providers

from src.clients import JiraClient
from src.managers import ReportManager
from src.utils import CustomLogger
 
 
class Container(containers.DeclarativeContainer):
    config = providers.Configuration(yaml_files=["config.yml"])
    logger = providers.Factory(CustomLogger, config=config.logging).delegate()
    

    jira_client = providers.Singleton(
        JiraClient,
        config=config.jira,
        logger=logger.provided.call(JiraClient)
    )

    report_manager = providers.Singleton(
        ReportManager,
        jira_client=jira_client
    )
