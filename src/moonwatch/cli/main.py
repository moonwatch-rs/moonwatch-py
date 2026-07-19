from argparse import ArgumentParser

from moonwatch.cli.base import Subcommand
from moonwatch.cli.spec_generator import SpecGeneratorSubcommand


class MoonwatchCLI:
    SUBCOMMANDS: list[type[Subcommand]] = [
        SpecGeneratorSubcommand,
    ]

    def __init__(self) -> None:
        self.parser = ArgumentParser()
        subparsers = self.parser.add_subparsers(dest="command", title="subcommands")
        for cls in self.SUBCOMMANDS:
            subparser = subparsers.add_parser(cls.get_name())
            cls.register(subparser)

    def run(self, argv: list[str]) -> int:
        args = self.parser.parse_args(argv)
        command = args.command
        for cls in self.SUBCOMMANDS:
            if cls.get_name() == command:
                return cls().run(args)
        else:
            raise NotImplementedError(f"Unexpected subcommand: {command}")
