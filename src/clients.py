class JiraClient:
    def __init__(self, config) -> None:
        self._config = config

    def test(self) -> None:
        print(self._config)
