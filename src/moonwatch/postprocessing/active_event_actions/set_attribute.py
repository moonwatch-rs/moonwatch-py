import polars as pl

from moonwatch.models.config.PostprocessingConfig import PostprocessingConfigActiveEventSetAttributeAction
from moonwatch.postprocessing.active_event_actions.base import ActiveEventActionExecutor


class ActiveEventSetAttributeActionExecutor(ActiveEventActionExecutor):
    def __init__(self, action: PostprocessingConfigActiveEventSetAttributeAction) -> None:
        self.action = action

    def run(self, df: pl.DataFrame) -> pl.DataFrame:
        expr = self.get_predicate(self.action.when, self.action.exclude)
        return df.with_columns(
            pl.when(expr)
            .then(pl.lit(self.action.value))
            .otherwise(pl.col(self.action.attribute))
            .alias(self.action.attribute)
        )
