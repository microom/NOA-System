# NOA SYSTEM - DEVLOG

```text
========================================
        NOA SYSTEM - DEVLOG
========================================
```

NOA Systemを作っていく途中で、何を考え、何を試し、何が分かったのかを残していく開発日記です。

完成したものだけではなく、遠回りしたこと、うまくいかなかったこと、設計を変えた理由も含めて記録していきます。

Devlogの番号はIssue番号とは切り離した、公開記事としての通し番号です。表示上は`#1`、`#42`のようにゼロ埋めせず、ファイル名では`0001`、`0042`のように4桁で揃えます。

---

## Entries

### [ 2026.09.08 ]

**NEW!** [#6 — 作りながら、設計書も育てる](0006-grow-the-design-docs.md)

実装が先へ進んだことで生まれた設計文書とのズレを整理し、AIと一緒に作るために「設計書も実装と一緒に育てる」形へ変わった話。

### [ 2026.09.07 ]

[#5 — 消しても困らないROM Database](0005-rebuildable-rom-database.md)

保存したMAME Source SnapshotをParse / Normalizeし、3710 Software / 4292 ROMのSQLiteを何度でも再生成できるpipelineへつないだ話。

[#4 — データベースより先に、その故郷を保存する](0004-preserve-the-source-before-the-database.md)

ROM Databaseを作る前に、MAME 0.289の一次資料と出典・ライセンス・SHA-256を固定し、あとから同じDatabaseを再現できる土台を作った話。

[#3 — ゲームが残るなら、遊んだ時間も残したい](0003-keep-the-time-we-played.md)

SFCのSRAMをNOA System自身のSave領域へ保存し、F-Zeroで既存Saveと新規Saveの両方が再起動後も戻ってくるところまでを通した話。

[#2 — 初めて本物のゲームが動いた日](0002-first-real-game.md)

Dummy Sessionの向こう側へ初めて実ゲームをつなぎ、ImportからPLAY、実ゲーム起動、ExitしてGame Detailへ戻るところまでを通した話。

[#1 — エミュレータより先に、ゲーム機の一周を作る](0001-first-vertical-slice.md)

最初のVertical Sliceとして、Libraryからゲームを選び、PLAYし、Sessionを終えて元のGame Detailへ戻るところまでを先に作った話。

---

```text
Last Updated : 2026.09.08
```

[← Back to NOA System](../README.md)
