from cs336_data.assets import assets
from cs336_data.fasttext_model import FastTextModel


def identify_language(text: str, model: FastTextModel | None = None) -> tuple[str, float]:
    if model is None:
        model = FastTextModel(assets.get_language_classifier_path().as_posix())
    text = text.replace("\n", " ")
    label, score = model.predict(text)
    return label, score


if __name__ == "__main__":
    model = FastTextModel(assets.get_language_classifier_path().as_posix())
    print(identify_language("These models were trained on UTF-8 data, and therefore expect UTF-8 as input.", model))
    print(identify_language("这些模型是在 UTF-8 数据上训练的，因此期望输入为 UTF-8 格式。", model))
