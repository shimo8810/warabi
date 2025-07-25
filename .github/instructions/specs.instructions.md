---
applyTo: '**'
---

# 仕様
- このライブラリは日本語全文検索ライブラリです｡
- janomeとsqlite3 FTS のラッパーです｡
- janomeは日本語の形態素解析ライブラリです｡
- sqlite3 FTSはSQLiteの全文検索機能です｡
- 軽量さシンプルさを重視しています｡
- 大量のデータを扱うことは想定していません｡
- 大量のユーザのデータを扱うことは想定していません｡

## 要件定義

### プロジェクト概要
`janome` と `sqlite3 FTS` を利用した、軽量でシンプルな日本語全文検索ライブラリを開発する。小規模なデータセットを対象とし、導入と利用の容易さを重視する。

### 機能要件
| ID | 機能名 | 概要 |
| :--- | :--- | :--- |
| FR-01 | インデックス作成 | 日本語テキストを受け取り、検索用のインデックスを構築する。ドキュメントには一意のIDを紐付けることができる。 |
| FR-02 | ドキュメント更新 | 指定したIDのドキュメントを新しい内容で更新する。 |
| FR-03 | ドキュメント削除 | 指定したIDのドキュメントをインデックスから削除する。 |
| FR-04 | 全文検索 | 日本語の検索クエリでインデックスを検索し、一致したドキュメントのIDリストを返す。 |
| FR-05 | データ永続化 | インデックスデータをSQLiteファイルとして永続化、またはインメモリで動作させることができる。 |

### 非機能要件
| ID | 種別 | 内容 |
| :--- | :--- | :--- |
| NFR-01 | パフォーマンス | 小規模データ（数万件程度）において、検索が現実的な時間（1秒未満）で応答すること。 |
| NFR-02 | 使いやすさ | シンプルなAPIを提供し、数行のコードで検索機能を利用可能にする。 |
| NFR-03 | 依存性 | 外部ライブラリの依存は `janome` のみとし、Pythonの標準ライブラリ `sqlite3` を活用する。 |
| NFR-04 | ポータビリティ | 生成されたSQLiteファイルは、単一ファイルとして容易にバックアップや移動が可能であること。 |