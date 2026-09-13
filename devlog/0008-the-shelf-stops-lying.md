# #8 — 嘘だったゲーム棚を、本物にする

最初のVertical Sliceを作った頃から、画面にはゲームの一覧がありました。

タイトルを選び、Game Detailへ入り、PLAYする。

見た目だけなら、もうゲーム機らしい。

でも、その棚に並んでいたゲームは開発用のdummy dataでした。

前回まででROMを識別してLibraryへ登録するところまではできたので、今回はついに、その実LibraryをFrontendへつなぎます。

**画面にゲーム棚がある、ではなく、本当に自分のLibraryがそこにある。**

そんな回です。

---

## 起動したら、Libraryにあるものだけを出す

まず通常起動時にdummy Gameを自動生成する処理を外しました。

これ以降、Game Listに表示される正解はLibrary Databaseです。

```text
Libraryが空
  → 空のゲーム棚

Import済みGameがある
  → そのGameだけを表示
```

何もないときに賑やかに見せるための仮データは、もう通常のFrontendには混ざりません。

Game ListはDatabaseからGameを読み出し、選択したGameからGame Detailへ進みます。

そしてPLAYするときは、GameそのものをROM fileだと決めつけず、紐づいているMediaをDatabaseから解決してSessionへ渡します。

前回決めたGameとMediaの分離が、そのまま画面までつながりました。

---

## 25本並んでも、全部触れるようにする

この時点では完成版のShelf UIを作るつもりはありませんでした。

ArtworkもGridも検索もまだ先です。

ただ、実ROMをまとめてImportしたとき、画面に収まらないGameへ到達できないのでは検証になりません。

そこで選択位置に追従する、ごく簡単なviewportを追加しました。

```text
Game List
  ↓
Up / Downで選択
  ↓
画面外へ出たら表示範囲も追従
```

選択Indexは先頭と末尾を越えず、Libraryが空でも安全に扱います。

これは製品版UIではなく、あくまで今ある本物のLibraryを人間が触れるようにするための足場です。

実データでは、revision違いの2本が別々のGameとして並ぶこと、canonical titleがそのまま表示されること、Databaseに一致しない自作ROMも仮の名前で棚に並ぶことを確認しました。

再起動しても同じGame一覧が戻ってきます。

Frontend側の一時的な状態ではなく、Libraryそのものが棚の正体になりました。

---

## テストで通るだけでは、人間が触れない

最初の実装はここまでで一度レビューを通りました。

でも改めて見ると、Acceptance Suiteでは確認できても、実際の開発中に人間が気軽に「ROMを入れて、棚を見て、遊んでみる」ための操作が足りませんでした。

そこで、完成版UIとは別に3つの開発用操作を用意しました。

```text
I = Import One
A = Import All
D = Delete Selected Game
```

`I` は入力元から1本だけImportし、そのGame Detailへ移動します。

`A` は候補をまとめてImportし、Game Listへ反映します。途中の1本が失敗しても残りは続行し、成功・重複・失敗を集計します。

Bulk Import自体は特定の開発用folderに依存させず、将来USBやNAS、既存ROM collectionなど別の入力元にも使える境界にしました。

元fileをImport後に消費するか残すかもpolicyとして分離しています。

そして `D` は、選択中のGameとMedia、NOA Systemが管理しているROM fileを削除し、もう一度Importを試せるようにするための開発用操作です。

この `D` が、思った以上に大きな話になりました。

---

## 「削除できる」より「余計なものを絶対に消さない」

ファイルを読む機能なら、失敗しても多くの場合はエラーで済みます。

削除は違います。

間違ったpathを消したら元には戻せません。

だから今回のDeleteでは、何を消せるかより先に、**何を絶対に消してはいけないか**を決めました。

対象にできるのは、NOA Systemが管理しているROM領域の通常fileだけです。

管理領域外、`..`で外へ抜けるpath、疑わしいfilesystem linkなどは削除を拒否します。

Mediaが複数ある場合も、1件でも安全性を確認できなければ全部を止めます。

さらに、検証したpathと実際に削除するpathがズレないよう、解決済みのpathそのものを削除対象として保持するようにしました。

DBを消したあとにROM fileのcleanupだけ失敗した場合も、成功したふりをせずwarningとして見えるようにしています。

---

## Windowsのjunctionで、もう一段深くなる

それでもレビューは終わりませんでした。

Windows上でsymlink / junctionを実際に試したところ、開発環境では標準のfilesystem APIだけではNTFS junctionを期待通り検知できないケースが見つかりました。

見た目ではLibrary管理領域内にあるpathでも、junctionの先が別の場所なら、OSが実際に操作するfileはまったく別物になり得ます。

そこでWindows側ではreparse pointをPlatform層で明示的に検出し、filesystem linkを経由する削除そのものを拒否することにしました。

Windows固有の処理をcoreへ直接持ち込まず、Platform側の判定をcoreへ渡す形にしています。

そして、この安全性を確認するテスト自体も危険になり得ます。

テスト用junctionのリンク先や「管理領域外」を本当のTempや実Libraryで作るのではなく、build tree内に専用sandboxを作り、その中だけで破壊的テストが完結するルールも追加しました。

削除機能を安全にするためのテストが、別のfileを消してしまったら笑えません。

**本体だけでなく、壊すテストの方にも安全境界が必要でした。**

---

## 本物のROMで、入れて、消して、また遊ぶ

最後は25本の実ROMを使って、一連の操作を通しました。

```text
A
 ↓
25本をBulk Import
 ↓
Game Listへ反映
 ↓
D
 ↓
選択Gameと管理ROMを削除
 ↓
I
 ↓
1本ずつ再Import
 ↓
Game Detail
 ↓
PLAY
```

Bulk Importは25 / 25成功。

revision違いは別Entryのまま、自作ROMもUnknownのまま棚へ入りました。

削除したChrono Triggerなどをもう一度Importすると、元と同じtitleでGameが作られ、Mediaを解決して実際に起動するところまで確認できました。

管理領域外を指す危険なMediaは、削除を拒否します。

ユーザー側でも `I` / `A` / `D` とPLAYまで実際に操作して、期待した流れになることを確認しました。

---

## 画面はまだ変。でも、棚の中身は本物になった

見た目はまだ開発用です。

文字だけの一覧で、Artworkもありません。

でも、最初に作ったGame Listとは意味が変わりました。

あの頃の棚は、ゲーム機らしい一周を先に作るための舞台装置でした。

今は違います。

ImportしたROMがLibrary Databaseへ入り、そのGameが一覧に現れ、選択してDetailへ進み、紐づいたMediaでPLAYできる。

消して、もう一度取り込んでも同じ流れへ戻れる。

**嘘だったゲーム棚の中身が、ようやく本物になりました。**

---

## micから

パット見はゲームリストがあるけど嘘表示だったライブラリ。
まだ見た目は変だけど、次の次くらいにはちゃんと吸い出したデータで表示されるようになるはず

--- mic

---

← [前の日記 #7 — ROMが分かると、ゲーム棚になる](0007-understand-the-rom.md)
