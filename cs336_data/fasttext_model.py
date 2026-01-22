# pyright: reportGeneralTypeIssues=false
# pyright: reportUnknownVariableType=false

from typing import final

from fasttext import load_model


@final
class FastTextModel:
    def __init__(self, path: str) -> None:
        self.model = load_model(path)

    def predict(self, text: str) -> tuple[str, float]:
        labels, scores = self.model.predict(text, k=1)
        label: str = labels[0]
        score: float = scores.item()
        return label, score
