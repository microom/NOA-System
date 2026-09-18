# NOA SYSTEM - DEVLOG

NOA Systemを作っていく途中で、何を考え、何を試し、何が分かったのかを残していく開発日記です。

完成したものだけではなく、遠回りしたこと、うまくいかなかったこと、設計を変えた理由も含めて記録していきます。

Devlogの番号はIssue番号とは切り離した、公開記事としての通し番号です。表示上は`#1`、`#42`のようにゼロ埋めせず、ファイル名では`0001`、`0042`のように4桁で揃えます。

---

## Entries

### [ 2026.09.12 ]

**NEW!** [#29 — 古い続きを、勝手に戻さない](0029-dont-restore-the-old-future.md)

Persistent Saveが更新されたのに古いAutoSnapを自動Resumeすると、新しいSaveを古いSnapshot由来の状態へ巻き戻しかねない問題に対し、Save内容のidentityをAutoSnap metadataへ記録して不一致時は安全にAuto Resumeをskipするようにした話。

[#28 — 作るための道具も、NOAの中へ](0028-tools-for-building.md)

SRAM検証でAutoSnapの便利さが逆に切り分けを難しくしたことからDeveloper Debug Menuを作り、さらに開発中の証拠や景色をNOA自身で残せるManual Screenshotへ広がった話。速く実装するだけでなく、速く確かめ、途中の姿も残せる環境を作り始めた。

[#27 — 壊す前に、地図を描く](0027-draw-the-map-first.md)

Mega DriveのSave騒動をきっかけに、実装を先へ進める前にMD / SFC / PCE / FC・NES / GBAのphysical cartridgeをResearchし直した話。分からないことを推測で埋めず、「ここまでは触ってよい」「ここからはまだ触らない」を地図として残す開発へ変わっていった。

[#26 — 実物のカートリッジが、NOAへ渡ってきた](0026-cartridge-crosses-over.md)

Mega Driveの実カートリッジからROMとSaveを読み出し、既知ROMのHash一致、Sonic 3のFRAM、Shining Force IIのSRAMまでNOAへつないだ話。そして実ROM Importのワクワクから、既存環境の不満を直してもらう側ではなく、自分で理想の環境を作ろうとNOAを始めた原点へ戻った話。

### [ 2026.09.11 ]

[#25 — 二台目で、設計が試された](0025-second-system.md)

Mega Driveを二台目のSystemとして追加し、NOA Systemが初めて横方向へ広がった話。既存のSave State / AutoSnap / Preview / Overlayがほぼそのまま使えた一方、Save RAMではSecond Systemだからこそ共通層の誤った前提も見つかり、実機・調査・修正を往復しながら設計を確かめた。

[#24 — 最後にいた景色を、残す](0024-last-scene.md)

AutoSnapへ最後のgame frameをPreviewとして結びつけ、Game Detailで「どこにいたか」が見えるようになった話。そして一枚の画像から、動画や自動Screenshotによる「遊んでいた時間のログ」へ想像が伸び始めた話。

### [ 2026.09.10 ]

[#23 — 画面にも、理由を持たせる](0023-ui-with-intent.md)

機能を先に作るため長く我慢していたUIへ、dark navyの空気、静かなtransition、SystemをまたぐLibrary、意味を持つPLAY / RESUMEなど、NOA Systemの考え方を少しずつ手触りとして入れ始めた話。

[#22 — 終わるときに、続きを残す](0022-save-without-asking.md)

Session終了時に現在の状態をAutoSnapとして自動保存し、複数世代を安全に残せるようにした話。そして便利なはずの仕組みに、早くも少しだけ違和感を覚え始めた話。

[#21 — ただ遊ぶだけじゃない](0021-more-than-playing.md)

プレイ中にOverlay / System Menuを呼び出し、Save State / Load State / Reset / Exitをゲームパッドから扱えるようにして、NOA Systemが「ゲームを動かす箱」から少しずつ「らしいゲーム機」へ変わり始めた話。

[#20 — 保存した瞬間へ、戻る](0020-back-to-that-moment.md)

前回保存できるようになったManual Save Stateを、安全なidentity / compatibility確認を通して実際にLoadし、保存した瞬間へ戻れるところまでつないだ話。

[#19 — その瞬間を、丸ごと保存する](0019-save-the-moment.md)

ゲーム内のSRAMとは別に、プレイ中のエミュレーション状態をManual Save Stateとして安全に永続化する基盤を作った話。保存はできた。でも、この時点ではまだロードできない。

### [ 2026.09.09 ]

[#18 — やっぱり、コントローラーで遊びたい](0018-play-with-a-controller.md)

物理Gamepadの違いをLogical Padで吸収し、SFCのゲーム操作だけでなくGame List → Game Detail → PLAYまでコントローラーだけで辿れるようにした話。

[#17 — 遊んだ続きを、カートリッジへ返す](0017-write-the-future-back.md)

NOA Systemで遊んだSaveを実SFCカートリッジへ安全に書き戻し、backupとbyte-exact verifyを通したうえで、別の実機でもその続きを読めるところまで確認した話。

[#16 — カートリッジの続きから、遊ぶ](0016-save-from-cartridge.md)

実カートリッジからROMだけでなくSRAMも読み出し、Sutte HakkunやChrono Triggerで実機のセーブデータをNOA Systemへ持ってきて、その続きから遊べるようにした話。

[#15 — 「固まった？」を、なくす](0015-dump-is-alive.md)

カートリッジdumpをbackground化して読み出し進捗を見えるようにし、実機計測で速度の律速も調べた結果、無理な高速化より「ちゃんと待てる」UXを選んだ話。

[#14 — 無いなら、別の道で動かす](0014-cx4-without-external-firmware.md)

外部CX4 firmwareが無くても、既存Core自身が持つHLEへ必要なときだけfallbackし、Rockman X2を実際のgameplayまで動かせるようにした話。

[#13 — ROMだけでは、ゲームは動かない](0013-rom-is-not-enough.md)

正しいRockman X2のROMまで辿り着いた先でCX4の別firmwareが必要と分かり、無理な物理抽出を止めて安全なFirmware Resolver / resolved viewを作った話。

[#12 — カートリッジを挿したら、ゲームになる](0012-cartridge-to-play.md)

実カートリッジからDump → Identity → Import → Library → 自動選択 → PLAYまでを一本につなぎ、前回残ったRockman X2 / CX4のROM dump問題も解いた話。

[#11 — カートリッジは、そんなに素直じゃない](0011-when-the-cartridge-fights-back.md)

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
Last Updated : 2026.09.18
```

[← Back to NOA System](../README.md)
