from pathlib import Path
import gzip

data_dir = Path(__file__).resolve().parent
input_dir = data_dir.joinpath("log")
output_dir = data_dir.joinpath("log_gzip")

output_dir.mkdir()

for input_path in input_dir.glob("*.jsonl"):
    output_path = output_dir.joinpath(input_path.name + ".gz")
    with input_path.open("rb") as in_fp, gzip.open(output_path, "wb") as out_fp:
        out_fp.write(in_fp.read())
