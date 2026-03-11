---
title: "Claude Codeのカスタムコマンドで技術ブログの執筆からContentfulへの投稿まで自動化してみた"
slug: "custom-commands-for-blogging-with-contentful"
tags:
  - Claude Code
  - Contentful
  - Automation
articleId: "6pglFwEnEUVs6jsgpsaYPu"
publishedAt: "2026-03-06T14:00:00+09:00"
---

## はじめに

技術ブログを書くとき、記事の執筆・フォルダ整理・CMS（Contentful）への投稿と、意外と手作業が多いです。

そこで、Claude Codeのカスタムコマンド機能を使い、スラッシュコマンドだけで記事の下書き作成からContentfulへのドラフト投稿までを完結させるツールを作ってみました。

本記事ではこのツールの仕組みと、使い始めるまでの手順を紹介します。ツールのソースコードと生成された記事の実例はGitHubリポジトリで公開しています。

https://github.com/oharu121/developersio-articles

作成した記事のイメージ：

![スクリーンショット 2026-03-06 15.06.21](https://devio2024-media.developers.io/image/upload/f_auto/q_auto/v1772777243/2026/03/06/u3leybek5kadrnrexyyw.png)

投稿した記事のイメージ（ドラフト）：

![スクリーンショット 2026-03-06 15.02.57](https://devio2024-media.developers.io/image/upload/f_auto/q_auto/v1772777313/2026/03/06/bsod0kk6swyafkiiofs5.png)

## 作ったもの

2つのカスタムコマンドを作成しました。

| コマンド | 機能 |
|---------|------|
| `/article <トピック>` | トピックを元に、ガイドラインに準拠した日本語の技術ブログ記事の下書きを生成 |
| `/publish <ファイルパス>` | 指定した記事ファイルをContentfulにドラフトとして投稿（更新にも対応） |

また、Contentful APIとの通信はすべてPython CLIスクリプト（`scripts/contentful.py`）で行っています。これにより、CMAトークンがLLMのコンテキストに入ることなく、安全にAPI操作を実行できます。

実際にこのツールで生成した記事の例もリポジトリに含まれています。

- [`macos/open-with-vscode-from-finder-right-click-menu.md`](https://github.com/oharu121/developersio-articles/blob/main/macos/open-with-vscode-from-finder-right-click-menu.md) — Finderの右クリックメニューにVS Codeを追加する手順記事

## 前提・環境

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)（CLI）がインストール済みであること
- Contentfulアカウントがあり、CMA（Content Management API）トークンを発行できること
- ブログのContent TypeがContentful上に定義済みであること

## セットアップ手順

### 1. リポジトリをクローン

```bash
git clone https://github.com/oharu121/developersio-articles.git
cd developersio-articles
```

クローンすると、`.claude/commands/` ディレクトリにあるコマンド定義ファイルがそのままClaude Codeのスラッシュコマンドとして使えるようになります。

### 2. .envファイルを作成

```bash
cp .env.example .env
```

`.env` を編集して `CONTENTFUL_CMA_TOKEN` にCMAトークンを設定します。CMAトークンは [Contentfulの設定画面](https://app.contentful.com/account/profile/cma_tokens) から生成できます。

![スクリーンショット 2026-03-05 10.41.20](https://devio2024-media.developers.io/image/upload/f_auto/q_auto/v1772777383/2026/03/06/ejsrojdvdlcedlrsji7a.png)

## /article コマンドの仕組み

### カスタムコマンドとは

Claude Codeでは、`.claude/commands/` ディレクトリにMarkdownファイルを配置すると、そのファイル名がスラッシュコマンドとして使えるようになります。`$ARGUMENTS` というプレースホルダーでユーザーの入力を受け取れます。

### /article の動作フロー

`/article AWS Lambdaでpython3.12ランタイムを試す` のようにトピックを渡すと、以下のフローが実行されます。

- **フォルダ選択** — プロジェクト内の既存フォルダを一覧表示し、トピックに関連するフォルダを提案。なければ新しいフォルダ名の候補を提示

![スクリーンショット 2026-03-05 10.24.19](https://devio2024-media.developers.io/image/upload/f_auto/q_auto/v1772778539/2026/03/06/m7vjdekurwua3xi7wa8z.png)

- **タグ提案** — トピックに基づいて関連タグの候補を提案し、ユーザーが選択・追加・修正

![スクリーンショット 2026-03-05 10.24.59](https://devio2024-media.developers.io/image/upload/f_auto/q_auto/v1772778567/2026/03/06/czsjrrthsuzvwtwrbl3m.png)

- **記事生成** — ガイドラインに準拠した日本語の技術ブログ記事をMarkdownで生成

![スクリーンショット 2026-03-06 15.06.21](https://devio2024-media.developers.io/image/upload/f_auto/q_auto/v1772778805/2026/03/06/h5850mjskdqglo56dw6x.png)

### 記事のフォーマット

生成される記事にはYAML frontmatterが含まれます。

```yaml
---
title: "日本語のタイトル"
slug: "english-kebab-case-slug"
tags:
  - tag1
  - tag2
---
```

- `title` — 日本語の記事タイトル
- `slug` — URL用の英語キー（ファイル名にも使用）
- `tags` — 記事に関連するタグのリスト
- `articleId` — Contentfulのエントリ ID（`/publish` 後に自動追記）

### メディアガイドラインの組み込み

`article.md` のコマンド定義に、メディアガイドラインを直接記載しています。これにより、Claude Codeが記事を生成する際に自動的にガイドラインを考慮してくれます。

含めているルール例：

- 「やってみた」視点で実体験ベースの記事にする
- ディス（他製品・サービスの批判）を避ける
- 憶測や伝聞ではなくソースに基づいた内容にする
- 生成AIへの丸投げはせず、あくまでアシスタントとして使う

コマンド定義の全文は [`.claude/commands/article.md`](https://github.com/oharu121/developersio-articles/blob/main/.claude/commands/article.md) で確認できます。

## /publish コマンドの仕組み

### 初回セットアップの自動化

`/publish` コマンドには、初回実行時の自動セットアップ機能を組み込んでいます。

**Step 1: 環境チェック**

```bash
python3 scripts/contentful.py setup --check
```

スクリプトが `.env` のCMAトークンと設定ファイルの存在を確認します。トークンが未設定の場合は、取得方法をユーザーに案内して処理を中断します。

**Step 2: Contentful設定の自動生成**

`.claude/contentful-config.json` が存在しない場合、スクリプトのセットアップコマンドでContentful APIから自動的に設定を検出します。

```bash
python3 scripts/contentful.py setup --list-spaces
python3 scripts/contentful.py setup --list-content-types --space-id {id}
python3 scripts/contentful.py setup --list-authors --space-id {id}
python3 scripts/contentful.py setup --save --space-id {id} --author-id {id}
```

各コマンドはJSON形式で結果を返し、LLM側がユーザーに選択肢を提示します。2回目以降は設定ファイルを読み込むだけでスキップされます。

### 新規投稿フロー

```
/publish macos/open-with-vscode-from-finder-right-click-menu.md
```

のように記事ファイルのパスを渡すと、以下が実行されます。

- 記事ファイルを読み込み、frontmatterからメタ情報を抽出
- 投稿内容をユーザーに表示して確認を取る
- LLMが記事本文からexcerpt（概要文）を生成し、ユーザーに確認

![スクリーンショット 2026-03-06 15.01.38](https://devio2024-media.developers.io/image/upload/f_auto/q_auto/v1772777551/2026/03/06/jy1dumls1g5wizryutnj.png)

-  成功時はContentfulのエントリURLを表示し、`articleId` をfrontmatterに書き戻す

![スクリーンショット 2026-03-06 15.02.37](https://devio2024-media.developers.io/image/upload/f_auto/q_auto/v1772777563/2026/03/06/fxga1ozw9p4fuppzrwhd.png)

Contentful CMAでは、エントリを作成するとデフォルトでドラフト状態になります。公開（Publish）するには別途APIを呼ぶ必要があるため、誤って公開してしまう心配はありません。

### 更新フロー

frontmatterに `articleId` がある記事に対して `/publish` を実行すると、新規作成ではなく更新が行われます。

ここで重要なのは、Contentful CMAの更新API（`PUT`）は**全フィールドの送信が必要**という点です。送信しなかったフィールドは削除されます。つまり、Contentful上で直接設定したサムネイルやカテゴリなどが消えてしまう可能性があります。

そこで、更新時はスクリプト内で「fetch-merge-put」パターンを実装しています。

- LLMがローカルの内容とContentful上の値を比較し、差分をユーザーに表示
- excerptの扱いをユーザーに確認（現在のまま / 再生成 / 書き直し）
- 更新を実行

スクリプト内部では、ローカルで管理しているフィールド（title, slug, content, tags, excerpt）のみ上書きし、Contentful上で直接設定したフィールド（thumbnail, categories等）はそのまま保持します。`X-Contentful-Version` ヘッダーによる楽観的ロックも実装しています。

### CMAトークンに関する注意点

Contentful CMAトークンはスペースレベルのアクセスキーであり、特定のユーザーに紐付いていません。つまり、トークンがあれば誰の名前でも記事を投稿できてしまいます。Author Profileはエントリ内のリンクフィールドに過ぎず、認証とは関係ありません。

そのため：

- トークンは `.env` に保管し、`.gitignore` で除外する
- `contentful-config.json` に自分のAuthor IDを設定する（初回セットアップで自動設定）
- トークンの共有・コミットは絶対に避ける
- **LLMにトークンを読ませない** — API操作はPythonスクリプト経由で行い、トークンがLLMのコンテキストに入らないようにする

コマンド定義の全文は [`.claude/commands/publish.md`](https://github.com/oharu121/developersio-articles/blob/main/.claude/commands/publish.md)、Pythonスクリプトは [`scripts/contentful.py`](https://github.com/oharu121/developersio-articles/blob/main/scripts/contentful.py) で確認できます。

## プロジェクト構成

```
developersio-articles/
├── .claude/
│   ├── commands/
│   │   ├── article.md          # /article コマンド定義
│   │   ├── publish.md          # /publish コマンド定義
│   │   └── release.md          # /release コマンド定義
│   └── contentful-config.json  # Contentful接続設定（自動生成、gitignore対象）
├── scripts/
│   └── contentful.py           # Contentful API操作用CLIスクリプト
├── .env                        # CMAトークン（gitignore対象）
├── .env.example                # テンプレート
├── .gitignore
├── .plans/                     # リリース計画書
├── README.md
└── <カテゴリフォルダ>/
    └── <slug>.md               # 記事ファイル
```

## 使い方の例

### 記事を書く

```
/article AWS LambdaでPython 3.12ランタイムを試してみた
```

フォルダ選択 → タグ選択 → 記事生成 の対話フローが始まります。

### 記事を投稿する

```
/publish aws-lambda/try-aws-lambda-python312.md
```

内容確認 → Contentfulにドラフト投稿 → エントリURLが表示されます。

### 記事を更新する

記事を編集した後、同じコマンドで更新できます。

```
/publish aws-lambda/try-aws-lambda-python312.md
```

frontmatterの `articleId` を見て自動的に更新フローが実行されます。Contentful上で設定したサムネイルなどはそのまま保持されます。

## まとめ

Claude Codeのカスタムコマンド機能を使うことで、技術ブログの執筆ワークフローをかなりシンプルにできました。

ポイントをまとめると：

- **カスタムコマンドはMarkdownファイル1つで定義できる** — 外部スクリプトやパッケージ不要
- **ガイドラインをコマンドに直接組み込める** — 記事品質を自動的に担保
- **Contentful APIとの連携も可能** — CMAトークンさえあれば、ドラフト投稿・更新まで自動化できる
- **認証情報の安全な取り扱い** — API操作をPythonスクリプトに委譲し、CMAトークンがLLMのコンテキストに入らない設計
- **初回セットアップの自動化** — 設定が存在しなければAPIから検出・生成する仕組みにより、他のメンバーも簡単に使い始められる
- **更新時のデータ保護** — fetch-merge-putパターンでContentful上のフィールドを壊さない

ソースコードと生成例はすべて [GitHub リポジトリ](https://github.com/oharu121/developersio-articles) で公開しています。カスタムコマンドの定義ファイルは単なるMarkdownなので、自分のプロジェクトに合わせてカスタマイズしたり、ブログ以外の用途（ドキュメント生成、コードレビュー、デプロイ手順など）にも応用できます。
