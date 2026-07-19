import polars as pl

from moonwatch.models.config.PostprocessingConfig import PostprocessingConfigActiveEventIgnoreAction
from moonwatch.postprocessing.active_event_actions.base import ActiveEventActionExecutor


class ActiveEventIgnoreActionExecutor(ActiveEventActionExecutor):
    def __init__(self, action: PostprocessingConfigActiveEventIgnoreAction) -> None:
        self.action = action

    def run(self, df: pl.DataFrame) -> pl.DataFrame:
        expr = self.get_predicate(self.action.when, self.action.exclude)
        return df.with_columns(
            pl.when(expr)
            .then(pl.lit(True))
            .otherwise(pl.col("ignore"))
            .alias("ignore")
        )
