import io
import re
import zipfile

import pytest
import requests

from warabi.tokenizer.janome_tokenizer import JanomeTokenizer
from warabi.tokenizer.sudachi_tokenizer import SudachiTokenizer


def get_aozora_text(zip_url: str) -> str:
    """
    extracts the text content from a zip file URL of Aozora Bunko.
    """
    response = requests.get(zip_url)
    response.raise_for_status()

    zip_file = zipfile.ZipFile(io.BytesIO(response.content))

    text_filename = [
        name for name in zip_file.namelist() if name.endswith(".txt")
    ][0]

    with zip_file.open(text_filename, "r") as f:
        binary_content = f.read()
        text = binary_content.decode("shift_jis", errors="ignore")

    text = re.split(
        r"-------------------------------------------------------", text
    )[-1]
    text = re.split(r"底本：", text)[0]

    text = re.sub(r"《.+?》", "", text)
    text = re.sub(r"［＃.+?］", "", text)

    return text.replace(" ", "").replace("　", "").replace("｜", "").strip()


@pytest.fixture(scope="module")
def japanese_1k_text():
    """
    Fixture to provide a short Japanese text for testing tokenization.
    """
    return get_aozora_text(
        "https://www.aozora.gr.jp/cards/000035/files/1567_ruby_4948.zip"
    )[:1000]


@pytest.mark.parametrize("tokenizer", [JanomeTokenizer, SudachiTokenizer])
def test_performance_tokenize_japanese_1k_text(
    tokenizer,
    japanese_1k_text,
    benchmark,
):
    t = tokenizer()

    def performance_tokenize():
        return [t for t in t.tokenize(japanese_1k_text)]

    benchmark(performance_tokenize)
