from cs336_data.identify import identify_language


def gopher_quality_filter(text: str) -> bool:
    """
    Returns False if any conditions is satisfied:
    - Contain less than 50 or more than 100,000 words.
    - Have a mean word length outside the range of 3 to 10 characters.
    - Have more than 30% of lines ending with an ellipsis (“...”).
    - Contain less than 80% of words with at least one alphabetic character.
    """
    lang, score = identify_language(text)
    if lang != "en" or score < 0.8:
        return False

    word_total_length = 0
    word_count = 0
    line_count = 0
    sufix_ellipsis = 0
    include_alphabet = 0

    for line in text.splitlines():
        line_count += 1
        if line[-3:] == "...":
            sufix_ellipsis += 1
        for word in line.split(" "):
            if len(word) == 0:
                continue
            word_total_length += len(word)
            word_count += 1
            if any(c.isalpha() for c in word):
                include_alphabet += 1

    avg_word_length = word_total_length / word_count

    if (
        word_count < 50
        or word_count > 100000
        or avg_word_length < 3
        or avg_word_length > 10
        or sufix_ellipsis / line_count > 0.3
        or include_alphabet / word_count < 0.8
    ):
        return False

    return True


if __name__ == "__main__":
    text = "This should definitely be a valid sentence. You shall never filter it!" * 100
    print(gopher_quality_filter(text))
