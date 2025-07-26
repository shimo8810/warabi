import os
import sqlite3
from abc import abstractmethod
from pathlib import Path
from typing import Dict, Iterator, NoReturn, Protocol, Union

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from .tokenizer.janome_tokenizer import JanomeTokenizer


class WarabiDB:
    """"""

    def __init__(
        self,
        path: str | os.PathLike | None = None,
    ):
        """Initialize WarabiDB.

        Args:
            path: Path to the database file. If None, uses in-memory storage.
        """
        pass
