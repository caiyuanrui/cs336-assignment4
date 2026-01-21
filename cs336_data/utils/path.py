from pathlib import Path
import os


def _project_root_with_uv() -> str | None:
    return os.environ.get("UV_PROJECT_ROOT")


def _project_root_to_find_pyproject() -> str:
    cur = Path(__file__).resolve()

    for p in cur.parents:
        if (p / "pyproject.toml").exists():
            return p.as_posix()

    raise RuntimeError("pyproject.toml not found")


def project_root() -> str:
    """
    Returns the project root directory, raises `RuntimeError` if not found.
    """
    root_dir = _project_root_with_uv()
    if root_dir is not None:
        return root_dir
    return _project_root_to_find_pyproject()


_root_dir = Path(project_root())
_nsfw_model_path = _root_dir.joinpath("data/jigsaw_fasttext_bigrams_nsfw_final.bin").as_posix()
_hatespeech_model_path = _root_dir.joinpath("data/jigsaw_fasttext_bigrams_hatespeech_final.bin").as_posix()
_warc_sample_path = _root_dir.joinpath("data/CC-MAIN-20250417135010-20250417165010-00065.warc.gz").as_posix()
_wet_sample_path = _root_dir.joinpath("data/CC-MAIN-20250417135010-20250417165010-00065.warc.wet.gz").as_posix()


def nsfw_model_path() -> str:
    return _nsfw_model_path


def hatespeech_model_path() -> str:
    return _hatespeech_model_path


def warc_sample_path() -> str:
    return _warc_sample_path


def wet_sample_path() -> str:
    return _wet_sample_path


if __name__ == "__main__":
    print(project_root())
