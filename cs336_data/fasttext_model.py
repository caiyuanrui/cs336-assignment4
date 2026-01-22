# pyright: reportGeneralTypeIssues=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# pyright: reportMissingParameterType=false

from typing import final

from fasttext import load_model


@final
class FastTextModel:
    def __init__(self, path: str | None = None, model=None) -> None:
        if path is not None:
            self.model = load_model(path)
        elif model is not None:
            self.model = model

    def predict(self, text: str) -> tuple[str, float]:
        labels, scores = self.model.predict(text, k=1)
        label: str = labels[0]
        score: float = scores.item()
        return label, score
