from pathlib import Path
from typing import Any, Literal

from fasttext import load_model  # pyright: ignore[reportUnknownVariableType]

from cs336_data.identify import remove_label_prefix
from cs336_data.utils import hatespeech_model_path, nsfw_model_path, project_root

_root_dir = Path(project_root())
_hatespeech_model_path = _root_dir.joinpath("data/jigsaw_fasttext_bigrams_hatespeech_final.bin").as_posix()
_nsfw_model_path = _root_dir.joinpath("data/jigsaw_fasttext_bigrams_nsfw_final.bin").as_posix()


def classify_nsfw(text: str, model: Any = None) -> tuple[Literal["nsfw", "non-nsfw"], float]:  # pyright: ignore[reportExplicitAny, reportAny]
    if model is None:
        model = load_model(_nsfw_model_path)
    label, score = model.predict(text)  # pyright: ignore[reportAny]
    label: str = remove_label_prefix(label[0])
    score: float = score.item()  # pyright: ignore[reportUnknownVariableType, reportAttributeAccessIssue]
    return label, score  # pyright: ignore[reportUnknownVariableType, reportReturnType]


def classify_toxic_speech(text: str, model: Any = None) -> tuple[Literal["toxic", "non-toxic"], float]:  # pyright: ignore[reportAny, reportExplicitAny]
    if model is None:
        model = load_model(_hatespeech_model_path)
    label, score = model.predict(text)  # pyright: ignore[reportAny]
    label: str = remove_label_prefix(label[0])
    score: float = score.item()  # pyright: ignore[reportUnknownVariableType, reportAttributeAccessIssue]
    return label, score  # pyright: ignore[reportUnknownVariableType, reportReturnType]


if __name__ == "__main__":
    # Seems like the model cannot correctly process non-english text
    normal_text = "What a nice day! u wanna hang out right now?"
    nsfw_text = "I know you like it, you little whore. Enjoy daddy's huge wood, bitch."
    # nsfw_text = "女人精品毛片,99久久精品无码一区二区毛片,被老外的又粗又大日出了水,一边吃奶一边哭乱抻又乱扭"
    toxic_text = "You are so stupid! It's a waste of time talking with you. Get the fuck out of here."

    nsfw_model = load_model(nsfw_model_path())
    toxic_model = load_model(hatespeech_model_path())

    for text in [normal_text, nsfw_text, toxic_text]:
        print(classify_nsfw(text, nsfw_model))
        print(classify_toxic_speech(text, toxic_model))
