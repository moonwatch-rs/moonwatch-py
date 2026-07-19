from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Self

import polars as pl

from moonwatch.common import PathOrStr
from moonwatch.config import MoonwatchConfig
from moonwatch.logs import MoonwatchLogDataframeParser
from moonwatch.models.config.PostprocessingConfig import PostprocessingConfig
from moonwatch.postprocessing.active_event_actions.base import ActiveEventActionExecutor
from moonwatch.postprocessing.one_hot_encoder import OneHotEncoder
from moonwatch.postprocessing.split_long_duration import SplitLongDuration


class MoonwatchPostproWorkflow:
    def __init__(self, parser: MoonwatchLogDataframeParser, config: PostprocessingConfig) -> None:
        self.parser = parser
        self.config = config
        self.active_window_event_df: pl.DataFrame | None = None

    @classmethod
    def from_main_config(cls, config: MoonwatchConfig) -> Self:
        return cls(
            parser=MoonwatchLogDataframeParser(config.iter_logs()),
            config=config.postprocessing_config,
        )

    def run(self) -> "MoonwatchPostproWorkflowOutput":
        # 1) unify desktop and mobile active events into one table
        active_event_df = self.parser.unified_active_event_df

        # 2) run user-defined actions
        for action in self.config.activeEventActions:
            executor = ActiveEventActionExecutor.from_action(action)
            active_event_df = executor.run(active_event_df)

        # 3) split tags array into separate boolean columns
        active_event_df = OneHotEncoder("tags").run(active_event_df)

        # 4) split long events to enforce maximum duration
        if (max_duration_sec := self.config.activeEventMaxDurationSec) is not None:
            if max_duration_sec <= 0:
                raise ValueError("Maximum duration must be a positive number of seconds")

            desktop_events = active_event_df.filter(pl.col("isMobile").not_())
            mobile_events = active_event_df.filter(pl.col("isMobile"))
            mobile_events = SplitLongDuration(
                duration_column_name="duration",
                timestamp_column_name="time",
                max_duration=timedelta(seconds=max_duration_sec)
            ).run(mobile_events)
            active_event_df = pl.concat([desktop_events, mobile_events])

        # 5) sort by time
        active_event_df = active_event_df.sort(pl.col("time"))

        return MoonwatchPostproWorkflowOutput(
            active_event_df=active_event_df,
        )


@dataclass
class MoonwatchPostproWorkflowOutput:
    active_event_df: pl.DataFrame

    def write_active_event_df_parquet(self, path: PathOrStr) -> None:
        df = (
            self.active_event_df
            .filter(pl.col("ignore").not_())
            .drop("idleFor")
            .with_columns(
                pl.col("duration").dt.total_seconds()
            )
        )
        df.write_parquet(Path(path))
