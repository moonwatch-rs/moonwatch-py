from abc import ABC, abstractmethod

from argparse import ArgumentParser, Namespace


class Subcommand(ABC):
    def __init__(self) -> None:
        pass

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def register(cls, parser: ArgumentParser) -> None:
        pass

    @abstractmethod
    def run(self, args: Namespace) -> int:
        pass
