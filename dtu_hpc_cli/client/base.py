import abc


class Client(abc.ABC):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    @abc.abstractmethod
    def run(self, command: str, cwd: str | None = None, ssh_timeout: float = 0.25) -> str:
        pass

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def remove(self, path: str):
        pass

    @abc.abstractmethod
    def save(self, path: str, contents: str):
        pass
