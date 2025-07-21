from .full_text_search import FullTextSearcher
from .tokenizer import Tokenizer


class DB:
    def __init__(
        self,
        fts: FullTextSearcher,
        tokenizer: Tokenizer,
    ):
        self.fts = fts
        self.tokenizer = tokenizer
