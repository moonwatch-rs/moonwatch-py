from argparse import Namespace, ArgumentParser
from pathlib import Path

from moonwatch.cli.base import Subcommand
from moonwatch.models.spec_generator import SpecGenerator


class SpecGeneratorSubcommand(Subcommand):
    @classmethod
    def get_name(cls) -> str:
        return "spec_generator"

    @classmethod
    def register(cls, parser: ArgumentParser) -> None:
        parser.add_argument("output_dir", type=Path, nargs="?", default=".")

    def run(self, args: Namespace) -> int:
        output_dir: Path = args.output_dir
        SpecGenerator(output_dir).run()
        return 0
