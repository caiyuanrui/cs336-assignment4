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


if __name__ == "__main__":
    print(project_root())
