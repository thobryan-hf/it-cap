import logging

from typing import Dict

from src.utils import CustomLogger

class JiraClient:
    def __init__(self, config: Dict[str, str], logger: CustomLogger) -> None:
        self._config = config
        self._logger = logger()

    def test(self) -> None:
        self._logger.info(f'Test')
