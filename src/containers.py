from typing import Callable
from dependency_injector import containers, providers

from src.clients import JiraClient
from src.managers import ReportManager
from src.handlers import ScreenOutputHandler, CSVOutputHandler
from src.crawlers import ProjectCrawler
from src.utils import CustomLogger
 
 
class Container(containers.DeclarativeContainer):
    config = providers.Configuration(yaml_files=["config.yml"])
    logger = providers.Factory(CustomLogger, config=config.logging).delegate()

    jira_client = providers.Singleton(
        JiraClient,
        config=config.jira,
        logger=logger.provided.call(JiraClient)
    )

    project_crawler = providers.Singleton(
        ProjectCrawler,
        jira_client=jira_client,
        logger=logger.provided.call(ProjectCrawler)
    )

    screen_output_handler_factory = providers.Factory(
        ScreenOutputHandler,
        logger=logger.provided.call(ScreenOutputHandler)
    ).delegate()

    csv_output_handler_factory = providers.Factory(
        CSVOutputHandler,
        logger=logger.provided.call(CSVOutputHandler)
    ).delegate()

    report_manager = providers.Singleton(
        ReportManager,
        project_crawler=project_crawler,
        screen_output_handler_factory=screen_output_handler_factory,
        csv_output_handler_factory=csv_output_handler_factory,
        logger=logger.provided.call(ReportManager)
    )
