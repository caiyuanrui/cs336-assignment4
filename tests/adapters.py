from __future__ import annotations

import os
from typing import Any

from cs336_data.assets import assets
from cs336_data.classify import classify_nsfw, classify_toxic_speech
from cs336_data.extract import extract_text_from_html_bytes
from cs336_data.fasttext_model import FastTextModel
from cs336_data.identify import identify_language
from cs336_data.maskpii import mask_emails, mask_ipv4s, mask_phone_numbers


def run_extract_text_from_html_bytes(html_bytes: bytes) -> str | None:
    return extract_text_from_html_bytes(html_bytes)


def run_identify_language(text: str) -> tuple[str, float]:
    model = FastTextModel(assets.get_language_classifier_path().as_posix())
    return identify_language(text, model)


def run_mask_emails(text: str) -> tuple[str, int]:
    return mask_emails(text)


def run_mask_phone_numbers(text: str) -> tuple[str, int]:
    return mask_phone_numbers(text)


def run_mask_ips(text: str) -> tuple[str, int]:
    return mask_ipv4s(text)


def run_classify_nsfw(text: str) -> tuple[Any, float]:
    return classify_nsfw(text)


def run_classify_toxic_speech(text: str) -> tuple[Any, float]:
    return classify_toxic_speech(text)


def run_classify_quality(text: str) -> tuple[Any, float]:
    raise NotImplementedError


def run_gopher_quality_filter(text: str) -> bool:
    from cs336_data.qualify import gopher_quality_filter

    return gopher_quality_filter(text)


def run_exact_line_deduplication(input_files: list[os.PathLike], output_directory: os.PathLike):
    raise NotImplementedError


def run_minhash_deduplication(
    input_files: list[os.PathLike],
    num_hashes: int,
    num_bands: int,
    ngrams: int,
    jaccard_threshold: float,
    output_directory: os.PathLike,
):
    raise NotImplementedError
