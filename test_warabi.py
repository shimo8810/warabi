#!/usr/bin/env python3
"""Test script for WarabiDB implementation."""

from src.warabi import WarabiDB


def main():
    # Initialize in-memory database
    db = WarabiDB()

    # Test documents
    documents = [
        {
            "title": "Python プログラミング",
            "content": "Pythonは高級プログラミング言語です。機械学習やデータ分析に広く使われています。",
            "category": "技術",
        },
        {
            "title": "機械学習入門",
            "content": "機械学習はAIの一分野で、データからパターンを学習します。深層学習も含まれます。",
            "category": "AI",
        },
        {
            "title": "データベース設計",
            "content": "データベースは情報を効率的に格納・検索するシステムです。SQLiteは軽量なDBMSです。",
            "category": "技術",
        },
        {
            "title": "Web開発",
            "content": "ウェブ開発にはHTMLやCSS、JavaScriptが使われます。Pythonでもウェブアプリが作れます。",
            "category": "技術",
        },
    ]

    # Insert documents
    print("=== ドキュメントの挿入 ===")
    doc_ids = []
    for doc in documents:
        doc_id = db.insert(doc)
        doc_ids.append(doc_id)
        print(f"ドキュメント ID {doc_id}: {doc['title']}")

    print()

    # Test search
    print("=== 検索テスト ===")
    search_queries = [
        "Python",
        "機械学習",
        "データベース",
        "プログラミング言語",
        "ウェブ開発",
    ]

    for query in search_queries:
        results = db.search(query)
        print(f"検索クエリ: '{query}' -> {len(results)}件の結果")
        for result in results:
            print(f"  - {result['title']}")
        print()

    # Test get all documents
    print("=== 全ドキュメント取得 ===")
    all_docs = db.all()
    print(f"総ドキュメント数: {len(all_docs)}")
    for doc in all_docs:
        print(f"  - {doc['title']}")
    print()

    # Test get by ID
    print("=== ID による取得 ===")
    doc = db.get(doc_ids[0])
    if doc:
        print(f"ID {doc_ids[0]}: {doc['title']}")
    print()

    # Test update
    print("=== ドキュメント更新 ===")
    updated_doc = {
        "title": "Python プログラミング（改訂版）",
        "content": "Pythonは高級プログラミング言語です。機械学習、データ分析、ウェブ開発に広く使われています。",
        "category": "技術",
        "updated": True,
    }
    success = db.update(doc_ids[0], updated_doc)
    print(f"更新結果: {success}")

    # Verify update
    updated = db.get(doc_ids[0])
    if updated:
        print(f"更新後: {updated['title']}")
    print()

    # Test iteration
    print("=== イテレーション ===")
    for i, doc in enumerate(db):
        print(f"{i + 1}. {doc['title']}")
    print()

    # Test remove
    print("=== ドキュメント削除 ===")
    removed = db.remove(doc_ids[-1])
    print(f"削除結果 (ID {doc_ids[-1]}): {removed}")

    # Verify removal
    remaining = db.all()
    print(f"削除後のドキュメント数: {len(remaining)}")
    print()

    # Test truncate
    print("=== 全削除 ===")
    db.truncate()
    all_after_truncate = db.all()
    print(f"全削除後のドキュメント数: {len(all_after_truncate)}")

    # Close database
    db.close()
    print("データベースを閉じました。")


if __name__ == "__main__":
    main()
