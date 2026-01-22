from cs336_data.assets import assets
from cs336_data.fasttext_model import FastTextModel


def classify_nsfw(text: str, model: FastTextModel | None = None) -> tuple[str, float]:
    if model is None:
        model = FastTextModel(assets.get_nsfw_model_path().as_posix())
    label, score = model.predict(text)
    return label, score


def classify_toxic_speech(text: str, model: FastTextModel | None = None) -> tuple[str, float]:
    if model is None:
        model = FastTextModel(assets.get_toxic_model_path().as_posix())
    label, score = model.predict(text)
    return label, score


if __name__ == "__main__":
    # Seems like the model cannot correctly process non-english text
    normal_text = "What a nice day! u wanna hang out right now?"
    nsfw_text = "I know you like it, you little whore. Enjoy daddy's huge wood, bitch."
    toxic_text = "You are so stupid! It's a waste of time talking with you. Get the fuck out of here."

    nsfw_model = FastTextModel(assets.get_nsfw_model_path().as_posix())
    toxic_model = FastTextModel(assets.get_toxic_model_path().as_posix())

    for prompt, text in [("normal", normal_text), ("nsfw", nsfw_text), ("toxic", toxic_text)]:
        print(prompt, "classify_nsfw", classify_nsfw(text, nsfw_model))
        print(prompt, "classify_toxic", classify_toxic_speech(text, toxic_model))
