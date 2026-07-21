import pytest

from moonwatch.config import MoonwatchConfig
from moonwatch.postprocessing.workflow import MoonwatchPostproWorkflow


# TODO actually verify results

@pytest.mark.parametrize("log_filename", ["config.yaml", "config_gzip.yaml"])
def test_postpro_workflow(log_filename, shared_datadir, tmp_path):
    config_path = shared_datadir.joinpath(log_filename)
    config = MoonwatchConfig(config_path)
    workflow = MoonwatchPostproWorkflow.from_main_config(config)

    output = workflow.run()
    assert len(output.active_event_df) > 0

    output_path = tmp_path.joinpath("test1.parquet")
    output.write_active_event_df_parquet(output_path)
    assert output_path.exists()

    output_path = tmp_path.joinpath("test2.parquet")
    output.write_unlock_event_df_parquet(output_path)
    assert output_path.exists()

    output_path = tmp_path.joinpath("test3.db")
    output.write_database(f"sqlite:///{output_path.as_posix()}")
    assert output_path.exists()
