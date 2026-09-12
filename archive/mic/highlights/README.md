# About mic / Highlights 素材アーカイブ

micのX投稿を、ECHOが後から`docs/about-mic.md`のHighlightsとして編集できる形で保存する場所です。

## Codexへの依頼

次回からは、対象URLを添えて次のように依頼します。

```text
このX投稿をAbout micのHighlight素材として取り込んでください。
<Xの投稿URL>
```

## 保存形式

投稿ごとに`YYYY-MM-DD-短い英語slug`という名前のディレクトリを作ります。

```text
archive/mic/highlights/<entry>/
├── post.md
├── source.json
├── image_01.jpg
├── image_02.jpg
└── ...
```

- `post.md`: 人が読むための投稿本文と出典情報
- `source.json`: ECHOやツールが処理するための構造化データ
- `image_XX.*`: 投稿に添付された画像を表示順に保存したもの

## 取り込みルール

1. 投稿本文、改行、絵文字、ハッシュタグは可能な限り原文のまま保存する。
2. 元URL、投稿ID、投稿者、ハンドル、投稿日時を保存する。日時はISO 8601形式も残す。
3. 画像はスクリーンショットではなく、Xが配信する最も高解像度の添付画像を優先する。
4. 画像は投稿上の表示順に`image_01`、`image_02`のように命名し、実際の形式と拡張子を一致させる。
5. 取得できない情報は推測せず、`null`にするか作業結果で報告する。
6. 同じ投稿IDまたはURLのentryが存在する場合は重複作成しない。
7. Cookie、トークン、署名付きURL、一時URL、ローカルパスなどを保存しない。
8. この取り込みでは`docs/about-mic.md`、`Assets/about/highlights/`、README、Devlog、ECHO's Logを編集しない。
9. 取得後に本文、画像数、画像形式、画像サイズ、Git差分を確認してからコミットする。

このディレクトリは元素材の保管場所です。Highlightsへの採用、要約、カード画像の作成、公開ページへの配置はECHOが別の作業として行います。
