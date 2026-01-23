from collections import defaultdict
from pathlib import Path

import xxhash


def exact_line_deduplication(input_files: list[str], output_directory: str):
    freq_table: defaultdict[bytes, int] = defaultdict(int)

    for input_file in input_files:
        input_file = Path(input_file)
        with open(input_file) as in_f:
            for line in in_f.readlines():
                line = line.rstrip()
                if not line:
                    continue
                freq_table[hash128(line)] += 1

    for input_file in input_files:
        input_file = Path(input_file)
        output_file = Path(output_directory).joinpath(input_file.name)
        with input_file.open("r", encoding="utf-8") as in_f, output_file.open("w", encoding="utf-8") as out_f:
            for line in in_f.readlines():
                line = line.rstrip()
                if not line:
                    continue
                hash = hash128(line)
                if freq_table[hash] == 1:
                    _ = out_f.write(line + "\n")


def hash128(x: bytes | str):
    if isinstance(x, str):
        x = x.encode()
    return xxhash.xxh3_128(x).digest()
