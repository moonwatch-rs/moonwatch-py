from datetime import timedelta
import operator
from functools import reduce

import polars as pl

from moonwatch.models.config.PostprocessingConfig import PostprocessingConfigActiveEventPredicate


class ActiveEventPredicate:
    def __init__(self, config: PostprocessingConfigActiveEventPredicate) -> None:
        self.config = config

    def into_expr(self) -> pl.Expr:
        operands = []

        if (value := self.config.name) is not None:
            operands.append(pl.col("name").str.contains(value).fill_null(False))
        if (value := self.config.category) is not None:
            operands.append(pl.col("category") == value)
        if (value := self.config.processPath) is not None:
            operands.append(pl.col("processPath").str.contains(value).fill_null(False))
        if (value := self.config.processName) is not None:
            operands.append(pl.col("processName").str.contains(value).fill_null(False))
        if (value := self.config.applicationLabel) is not None:
            operands.append(pl.col("applicationLabel").str.contains(value).fill_null(False))
        if (value := self.config.applicationId) is not None:
            operands.append(pl.col("applicationId") == value)
        if (value := self.config.hasTag) is not None:
            operands.append(pl.col("tags").list.contains(value))
        if (value_bool := self.config.isMobile) is not None:
            operands.append(pl.col("isMobile") == value_bool)
        if (value_int := self.config.idleForGreaterThanSec) is not None:
            operands.append(pl.col("idleFor") > timedelta(seconds=value_int))

        match self.config.logic:
            case "and":
                return reduce(operator.and_, operands, pl.lit(True))
            case "or":
                return reduce(operator.or_, operands, pl.lit(False))
            case _:
                raise NotImplementedError(f"Unknown logic: {self.config.logic}")
