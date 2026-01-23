from cs336_data.assets import assets
from cs336_data.dedup import exact_line_deduplication


def main():
    root_dir = assets.project_root
    input_files = [(root_dir / "assets/warcs/lines.txt").as_posix()]
    output_directory = (root_dir / "assets/dedup").as_posix()
    exact_line_deduplication(input_files, output_directory)


if __name__ == "__main__":
    main()
