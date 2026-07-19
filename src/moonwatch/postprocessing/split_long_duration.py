from datetime import timedelta

import polars as pl


class SplitLongDuration:
    def __init__(
            self,
            duration_column_name: str,
            timestamp_column_name: str,
            max_duration: timedelta
    ) -> None:
        self.duration = duration_column_name
        self.timestamp = timestamp_column_name
        self.max_duration = max_duration

    def run(self, df: pl.DataFrame) -> pl.DataFrame:
        limit_ns = (self.max_duration // timedelta(microseconds=1)) * 1000
        dur_unit = df.schema[self.duration].time_unit  # type: ignore[attr-defined]

        return (
            df
            .with_columns(_dur_ns=pl.col(self.duration).dt.total_nanoseconds())
            # segments = ceil(dur / limit), but at least 1 (keeps zero/short rows intact)
            .with_columns(
                _n=pl.max_horizontal(
                    pl.lit(1),
                    (pl.col("_dur_ns") + limit_ns - 1) // limit_ns,
                )
            )
            .with_columns(_seg=pl.int_ranges(0, pl.col("_n")))
            .explode("_seg", empty_as_null=False)
            .with_columns(_off_ns=pl.col("_seg") * limit_ns)
            .with_columns(
                pl.col(self.timestamp) + pl.duration(nanoseconds=pl.col("_off_ns")),
                pl.duration(
                    nanoseconds=pl.min_horizontal(limit_ns, pl.col("_dur_ns") - pl.col("_off_ns"))
                ).cast(pl.Duration(dur_unit)).alias(self.duration),
            )
            .drop("_dur_ns", "_n", "_seg", "_off_ns")
        )
