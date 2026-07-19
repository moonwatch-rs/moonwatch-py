import polars as pl


class OneHotEncoder:
    def __init__(self, column_name: str) -> None:
        self.column_name = column_name

    def run(self, df: pl.DataFrame) -> pl.DataFrame:
        values = (
            df.select(
                pl.col(self.column_name)
                .explode(empty_as_null=False)
                .unique()
                .drop_nulls()
                .sort()
            )
            .to_series()
            .to_list()
        )

        return (
            df.with_columns(
                pl.col(self.column_name)
                .list
                .contains(value)
                .fill_null(False)
                .alias(f"{self.column_name}.{value}")
                for value in values
            )
            .drop(self.column_name)
        )
