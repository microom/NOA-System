# NOA SYSTEM - DEVLOG

NOA Systemを作っていく途中で、何を考え、何を試し、何が分かったのかを残していく開発日記です。

完成したものだけではなく、遠回りしたこと、うまくいかなかったこと、設計を変えた理由も含めて記録していきます。

Devlogの番号はIssue番号とは切り離した、公開記事としての通し番号です。表示上は`#1`、`#42`のようにゼロ埋めせず、ファイル名では`0001`、`0042`のように4桁で揃えます。

---

## Entries

### [ 2026.09.09 ]

**NEW!** [#11 — カートリッジは、そんなに素直じゃない](0011-when-the-cartridge-fights-back.md)

特殊チップ搭載SFCカートリッジを実機で次々に読み、SA-1 / S-DD1 / SPC7110などの違い、物理端子のcontact bounce、Headerだけでは分からないROM sizeに向き合った話。

[#10 — カートリッジから、ゲームが読めた日](0010-read-the-cartridge.md)

RetroFreak Cartridge AdapterをWindowsからread-onlyで制御し、実物のSFCカートリッジをdumpしてHash一致・DatabaseのKnown判定までつないだ話。

### [ 2026.09.08 ]

[#9 — ゲームの名前を、ちゃんと書けるようにする](0009-true-type-text.md)

実Libraryの本物のタイトルを正しく表示するため、開発用BitmapFontを卒業してM PLUS 2 / UTF-8対応のTrueType描画基盤へ移行した話。

[#8 — 嘘だったゲーム棚を、本物にする](0008-the-shelf-stops-lying.md)

DummyだったGame Listを実Library DBへつなぎ、実ROMをImportして一覧・選択・削除・再Import・PLAYまで人間が触れる「本物のゲーム棚」に変えた話。

[#7 — ROMが分かると、ゲーム棚になる](0007-understand-the-rom.md)

実ROM 25本を使ってIdentity照合を試し、MAMEとNo-Introの情報モデルの違いを踏まえながら、Known / Unknownを含めて「手元のゲームを理解できるLibrary」へ進んだ話。

[#6 — 作りながら、設計書も育てる](0006-grow-the-design-docs.md)

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
Last Updated : 2026.09.09
```

[← Back to NOA System](../README.md)
