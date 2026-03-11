指定された記事ファイルをContentfulにドラフトとして公開、または既存のドラフトを更新します。

ファイルパス: $ARGUMENTS

# 重要: セキュリティに関する注意

**`.env` ファイルを直接読まないこと。** すべてのContentful API操作は `scripts/contentful.py` を通じて行う。このスクリプトが内部で `.env` を読み込むため、CMAトークンがLLMのコンテキストに入ることはない。

# 前提チェック（記事の処理前に必ず実行）

## Step 1: 環境チェック

```bash
python3 scripts/contentful.py setup --check
```

- `{"ok": true}` が返れば次のステップへ
- `{"ok": false, "has_token": false}` の場合:
  - ユーザーに以下を案内して処理を中断する:
    1. https://app.contentful.com/account/profile/cma_tokens にアクセス
    2. CMAトークンを生成
    3. プロジェクトルートに `.env` ファイルを作成し `CONTENTFUL_CMA_TOKEN=your-token-here` を記入
- `{"ok": false, "has_token": true, "has_config": false}` の場合:
  - Step 2 のContentful設定の自動生成へ進む

## Step 2: Contentful設定の自動生成（configがない場合のみ）

以下のコマンドを順に実行し、ユーザーに選択してもらう:

1. **Space一覧の取得**:
   ```bash
   python3 scripts/contentful.py setup --list-spaces
   ```
   複数ある場合はユーザーに選択してもらう。

2. **Content Type一覧の取得**:
   ```bash
   python3 scripts/contentful.py setup --list-content-types --space-id {selected_space_id}
   ```
   ブログ記事用のContent Type（通常 `blogPost`）を特定する。

3. **Author一覧の取得**:
   ```bash
   python3 scripts/contentful.py setup --list-authors --space-id {selected_space_id}
   ```
   ユーザーに選択してもらう。

4. **設定の保存**:
   ```bash
   python3 scripts/contentful.py setup --save --space-id {id} --author-id {id} --content-type-id {id}
   ```

# 記事の公開手順

1. 指定されたファイルを読み込み、YAML frontmatter（title, slug, tags, articleId, publishedAt）と本文を確認する
2. frontmatter に `articleId` があるかどうかで **新規作成** か **更新** かを判定する

## 新規作成フロー（articleId なし）

1. 内容をユーザーに表示し、公開してよいか確認する
2. 記事本文から1-2文の概要文（excerpt）を生成し、AskUserQuestion でユーザーに提示する。ユーザーは承認、編集、または自分で書き直すことができる
3. 承認された excerpt を使って、スクリプトでドラフトエントリを作成する:
   ```bash
   python3 scripts/contentful.py create <article-file> --excerpt "承認されたexcerpt"
   ```
4. 成功したら、レスポンスJSONから取得した `entry_id` を記事ファイルの frontmatter に `articleId` として書き戻す
5. frontmatter に `publishedAt` がなければ、現在の日時（ISO 8601形式、例: `2026-03-05T12:00:00+09:00`）を `publishedAt` として追記する。既に `publishedAt` がある場合は変更しない

## 更新フロー（articleId あり）

1. スクリプトで既存エントリの全データを取得する:
   ```bash
   python3 scripts/contentful.py get <article-file>
   ```
2. ローカルで変更されたフィールド（title, slug, content, tags）と、Contentful上の現在の値を比較し、差分をユーザーに表示する
3. 既存エントリの excerpt を確認し、AskUserQuestion でユーザーに以下を選択してもらう:
   - 現在の excerpt をそのまま使う（現在の値を表示する）
   - 更新された記事内容から新しい excerpt を再生成する
   - 自分で書き直す
   再生成を選んだ場合は、生成結果を提示して承認を得る
4. 以下の警告を表示する:

   > **注意**: Contentful上で直接編集した内容（thumbnail, categories等）はそのまま保持されます。ローカルで管理しているフィールド（title, slug, content, tags, excerpt）のみが更新されます。

5. ユーザーの確認が取れたら、スクリプトで更新する:
   ```bash
   python3 scripts/contentful.py update <article-file> --excerpt "確定したexcerpt"
   ```

# 成功時

## 新規作成の場合
- レスポンスJSONに含まれるContentfulのエントリURLを表示する
- 記事ファイルの frontmatter に `articleId: {entry_id}` を追記する
- frontmatter に `publishedAt` がなければ、現在の日時（ISO 8601形式、例: `2026-03-05T12:00:00+09:00`）を追記する

## 更新の場合
- レスポンスJSONに含まれるContentfulのエントリURLを表示する
- 更新完了のメッセージを表示

# エラー時

- スクリプトのstderrに出力されたエラーJSONを解析し、原因と修正方法を提案する
- 409 Conflict の場合: 他の誰かが同時に編集した可能性がある旨を伝え、再取得してリトライするか確認する
