import polars as pl

from moonwatch.models.config.PostprocessingConfig import PostprocessingConfigActiveEventAddTagAction
from moonwatch.postprocessing.active_event_actions.base import ActiveEventActionExecutor


class ActiveEventAddTagActionExecutor(ActiveEventActionExecutor):
    def __init__(self, action: PostprocessingConfigActiveEventAddTagAction) -> None:
        self.action = action

    def run(self, df: pl.DataFrame) -> pl.DataFrame:
        expr = self.get_predicate(self.action.when, self.action.exclude)
        expr = expr.and_(pl.col("tags").list.contains(self.action.tag).not_())
        return df.with_columns(
            pl.when(expr)
            .then(pl.col("tags").list.concat(pl.lit(self.action.tag)))
            .otherwise(pl.col("tags"))
            .alias("tags")
        )
