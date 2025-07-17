import sqlite3

from janome.tokenizer import Tokenizer


def read_sangetsuki() -> list[str]:
    """
    Read the text of 'sangetsuki.txt' and return it as a list of strings.
    """
    with open("sangetsuki.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f]


# Janomeのトークナイザーを準備
tokenizer = Tokenizer()


def wakachi(text: str) -> str:
    """
    テキストを分かち書きし、スペース区切りの文字列を返す関数
    """
    # NOTE: linterが 'token.surface' でエラーを報告する場合がありますが、
    # janome.tokenizer.Token の仕様であり、動作上は問題ありません。
    return " ".join(token.surface for token in tokenizer.tokenize(text))


# 2. データベースに接続し、FTS5仮想テーブルを作成
# :memory:でインメモリデータベースを使用。ファイルパスを指定すれば永続化も可能。
conn = sqlite3.connect(":memory:")
c = conn.cursor()

# FTS5テーブルを作成。'content_wakati'カラムに分かち書きしたテキストを格納する。
# 'tokenize = "unicode61 remove_diacritics 0"' は非ASCII文字を扱うための
# 一般的な設定です。
c.execute(
    """
CREATE VIRTUAL TABLE articles USING fts5(
    title,
    body,
    content_wakati,
    tokenize = "unicode61 remove_diacritics 0"
);
"""
)

# 3. 検索対象のデータを準備
docs = [
    {
        "title": "SQLiteの全文検索",
        "body": "SQLiteにはFTS5という強力な全文検索モジュールがあります。",
    },
    {
        "title": "Janomeについて",
        "body": "Janomeは純粋なPythonで実装された日本語形態素解析ライブラリです。",
    },
    {
        "title": "Pythonプログラミング",
        "body": "Pythonはシンプルで学びやすいプログラミング言語です。ライブラリも豊富です。",
    },
]

# 4. データを分かち書きしてFTS5テーブルに挿入
for doc in docs:
    # bodyを分かち書きする
    wakati_text = wakachi(doc["body"])
    c.execute(
        "INSERT INTO articles (title, body, content_wakati) VALUES (?, ?, ?)",
        (doc["title"], doc["body"], wakati_text),
    )

conn.commit()

# 5. 全文検索を実行
search_query = "Python ライブラリ"
# 検索クエリも分かち書きする
wakati_query = wakachi(search_query)

print(f"検索クエリ: '{search_query}' (分かち書き: '{wakati_query}')")
print("-" * 20)

# 'content_wakati'カラムを対象に検索
c.execute(
    "SELECT title, body FROM articles WHERE content_wakati MATCH ?",
    (wakati_query,),
)

# 6. 検索結果を表示
for row in c.fetchall():
    print(f"Title: {row[0]}")
    print(f"Body: {row[1]}\n")

# 7. 接続を閉じる
conn.close()
