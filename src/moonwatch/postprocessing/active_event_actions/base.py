from abc import ABC, abstractmethod

import polars as pl

from moonwatch.models.config.PostprocessingConfig import PostprocessingConfigActiveEventIgnoreAction, \
    PostprocessingConfigActiveEventAddTagAction, PostprocessingConfigActiveEventSetAttributeAction, \
    PostprocessingConfigActiveEventAction, PostprocessingConfigActiveEventPredicate
from moonwatch.postprocessing.active_event_predicate import ActiveEventPredicate


class ActiveEventActionExecutor(ABC):
    @classmethod
    def from_action(cls, action: PostprocessingConfigActiveEventAction) -> "ActiveEventActionExecutor":
        if isinstance(action, PostprocessingConfigActiveEventIgnoreAction):
            from .ignore_action import ActiveEventIgnoreActionExecutor
            return ActiveEventIgnoreActionExecutor(action)
        elif isinstance(action, PostprocessingConfigActiveEventAddTagAction):
            from .add_tag import ActiveEventAddTagActionExecutor
            return ActiveEventAddTagActionExecutor(action)
        elif isinstance(action, PostprocessingConfigActiveEventSetAttributeAction):
            from .set_attribute import ActiveEventSetAttributeActionExecutor
            return ActiveEventSetAttributeActionExecutor(action)
        else:
            raise NotImplementedError(f"Unsupported action: {action}")

    @abstractmethod
    def run(self, df: pl.DataFrame) -> pl.DataFrame:
        pass

    def get_predicate(
            self,
            when: PostprocessingConfigActiveEventPredicate,
            exclude: PostprocessingConfigActiveEventPredicate | None,
    ) -> pl.Expr:
        when_expr = ActiveEventPredicate(when).into_expr()
        if exclude is None:
            return when_expr
        else:
            exclude_expr = ActiveEventPredicate(exclude).into_expr()
            return when_expr.and_(exclude_expr.not_())
