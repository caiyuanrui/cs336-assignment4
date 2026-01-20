from pathlib import Path

import fasttext


def replace_whitespaces(text: str, rep: str = " "):
    return rep.join(text.split())


def remove_label_prefix(label: str):
    assert label[:9] == "__label__"
    return label[9:]


def identify_language(text: str) -> tuple[str, float]:
    root_dir = Path(__file__).parent.parent
    model_path = root_dir.joinpath("data/lid.176.bin")

    model = fasttext.load_model(model_path.as_posix())

    text = replace_whitespaces(text)
    labels, probs = model.predict(text)  # noqa: F841  # pyright: ignore[reportUnknownVariableType]

    label: str = remove_label_prefix(labels[0])  # pyright: ignore[reportGeneralTypeIssues, reportUnknownArgumentType]
    prob: float = probs.item()  # pyright: ignore[reportUnknownVariableType]

    return label, prob  # pyright: ignore[reportUnknownVariableType]
