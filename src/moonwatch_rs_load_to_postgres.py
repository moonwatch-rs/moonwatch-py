import json
import sys
from pathlib import Path
import subprocess

import polars as pl


class Main:
    def __init__(self, postgresql_uri: str):
        self.postgresql_uri = postgresql_uri
        self.root_dir = Path.home().joinpath(".moonwatch-rs")
        self.output_dir = self.get_moonwatch_output_directory()

    def get_moonwatch_output_directory(self) -> Path:
        main_config_path = self.root_dir.joinpath("main_config.json")
        main_config = json.loads(main_config_path.read_text())
        return self.root_dir.joinpath(main_config["pipelineOutputDirectory"]).resolve()

    def run_moonwatch_pipeline(self) -> None:
        cmd = [
            str(self.root_dir.joinpath("moonwatch_rs.exe")),
            "pipeline"
        ]
        subprocess.check_call(cmd)

    def get_active_event_df(self) -> pl.DataFrame:
        return (
            pl.read_parquet(self.output_dir.joinpath("active_events.parquet"))
            .filter(pl.col("ignore").not_())
            .with_columns(pl.col("duration").dt.total_seconds())
            .drop(["idleFor", "ignore", "tags"])
        )

    def get_unlock_events_df(self) -> pl.DataFrame:
        return pl.read_parquet(self.output_dir.joinpath("unlock_events.parquet"))

    def write_to_db(self) -> None:
        print("Writing active events")
        self.get_active_event_df().write_database(
            table_name="active_event",
            connection=self.postgresql_uri,
            engine="adbc",
            if_table_exists="replace"
        )

        print("Writing unlock events")
        self.get_unlock_events_df().write_database(
            table_name="unlock_event",
            connection=self.postgresql_uri,
            engine="adbc",
            if_table_exists="replace"
        )

    def run(self) -> None:
        self.run_moonwatch_pipeline()
        self.write_to_db()

if __name__ == "__main__":
    Main(sys.argv[1]).run()
