import os
from pathlib import Path


class AssetManager:
    def __init__(self):
        project_root = os.environ.get("UV_PROJECT_ROOT")
        if project_root is None:
            cur = Path(__file__).resolve()
            for p in cur.parents:
                if (p / "pyproject.toml").exists():
                    project_root = p
                    break

        if project_root is None:
            raise RuntimeError("pyproject.toml not found")

        self.project_root: Path = Path(project_root)

        self.base_dir: Path = Path(os.getenv("CS336_ASSETS", self.project_root / "assets"))

        self._models: dict[str, str] = {
            "toxic": "dolma_fasttext_hatespeech_jigsaw_model.bin",
            "nsfw": "dolma_fasttext_nsfw_jigsaw_model.bin",
            "langid": "lid.176.bin",
        }

    def get_model_path(self, model_name: str):
        if model_name not in self._models:
            raise KeyError(f"model {model_name} is not defined in AssetManager")
        path = self.base_dir / "models" / self._models[model_name]
        if not path.exists():
            print(f"⚠️ Warning: cannot find the model: {path}")
            print(f"CUrrent Base Dir: {self.base_dir}")
        return path

    def get_toxic_model_path(self):
        return self.get_model_path("toxic")

    def get_nsfw_model_path(self):
        return self.get_model_path("nsfw")

    def get_language_classifier_path(self):
        """
        The model requires UTF-8 data.
        """
        return self.get_model_path("langid")

    def get_warc_path(self):
        path = self.base_dir / "warcs/CC-MAIN-20250417135010-20250417165010-00065.warc.gz"
        if not path.exists():
            print(f"⚠️ Warning: cannot find the warc file: {path}")
            print(f"CUrrent Base Dir: {self.base_dir}")
        return path

    def get_wet_path(self):
        path = self.base_dir / "warcs/CC-MAIN-20250417135010-20250417165010-00065.warc.wet.gz"
        if not path.exists():
            print(f"⚠️ Warning: cannot find the wet file: {path}")
            print(f"CUrrent Base Dir: {self.base_dir}")
        return path


assets = AssetManager()
