from argparse import Namespace, ArgumentParser
from pathlib import Path
from datetime import datetime

from moonwatch.cli.base import Subcommand
from moonwatch.config import MoonwatchConfig
from moonwatch.postprocessing.workflow import MoonwatchPostproWorkflow


class PostproSQLSubcommand(Subcommand):
    @classmethod
    def get_name(cls) -> str:
        return "postpro_sql"

    @classmethod
    def register(cls, parser: ArgumentParser) -> None:
        parser.add_argument("--config", type=Path, nargs="?")
        parser.add_argument("connection", type=str)

    def run(self, args: Namespace) -> int:
        config_path: Path | None = args.config
        connection: str = args.connection

        config = MoonwatchConfig(config_path)
        print(f"Read config: {str(config.config_path)}")
        workflow = MoonwatchPostproWorkflow.from_main_config(config)
        print("Started postprocessing workflow...")
        t0 = datetime.now()
        output = workflow.run()
        print(f"Finished postprocessing workflow in: {datetime.now() - t0}")
        print(f"Event count breakdown: {len(output.active_event_df):,} active {len(output.unlock_event_df):,} unlock")
        print("Writing into SQL database...")
        output.write_database(connection)
        print("All done.")

        return 0
