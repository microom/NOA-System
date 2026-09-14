# #12 — カートリッジを挿したら、ゲームになる

前回までで、SFCの実カートリッジからROMを読み、特殊チップを含むいくつものタイトルをDatabaseで特定できるようになりました。

でも、まだそこには境界がありました。

カートリッジを読むDevice。
ROMをLibraryへ入れるImport。
ゲームを並べるFrontend。
そして、実際に遊ぶSession。

それぞれは動いているけれど、実物のカートリッジから始めると、まだ一本にはつながっていません。

今回はそこをつなぎます。

```text
Physical Cartridge
  ↓
Dump
  ↓
Identity
  ↓
Import
  ↓
Library
  ↓
Game Detail
  ↓
PLAY
```

**カートリッジを挿したら、そのゲームがNOA Systemの中へ入って、そのまま遊べる。**

ここまで作ってきたものが、初めてひとつのゲーム機らしい流れになります。

---

## DeviceからLibraryへ、直接はつながない

物理カートリッジからROMが取れるようになったからといって、Device layerからLibrary DBへ直接書き込むようにはしませんでした。

境界はこれまで通り残します。

```text
DEVICE
  ↓ ROM image
Cartridge Acquisition / Canonicalization
  ↓
ImportService
  ↓
Library
```

Deviceが知るのは、カートリッジから正しくbyte列を読むところまで。

そこから先のHash計算、Database照合、ROM保存、Game / Media登録は、すでに作ってあるImportServiceへ任せます。

実カートリッジだから特別なLibrary経路を増やすのではなく、**入口だけが違って、その先は同じImportへ合流する**形です。

これで、これまで積み上げてきたatomic writeやdedupe、Unknown ROMの扱いもそのまま使えます。

---

## 「短くしたらKnownになった」を、推測にしない

前回、SFC Headerが示すROM sizeと実際のcanonical ROM sizeが一致しないカートリッジがあることが分かりました。

たとえば3 MiBのROMをHeaderだけから4 MiBとして読んでしまうケースです。

開発用Probeでは、より短いprefixをDatabaseへ照合してKnownになれば、そのsizeを採用する方法を試していました。

正式なImportへ持ってくるなら、もう少し慎重にする必要があります。

今回のルールは、

```text
full dumpがKnown
  → そのまま採用

full dumpはUnknown
  ↓
短いprefixをDB照合
  ↓
一致候補が1つだけ
  → canonical ROMとして採用

複数sizeがKnown
  → ambiguousとして採用しない
```

としました。

「最初に見つかったKnownだから、たぶんこれ」では切りません。

UnknownやHomebrewの末尾を勝手に削ることもしません。

Databaseを使ってROMを理解する仕組みが、ここでは**ROMを安全にcanonicalizeする根拠**にもなっています。

---

## 前回読めなかったRockman X2

そして、前回ひとつだけ残っていたのが **Rockman X2** でした。

CX4を搭載したこのカートリッジは、毎回同じdumpにはなるのに、正しい1.5 MiB ROMのSHA-1と一致しませんでした。

再現性があるということは、通信が不安定というより、**ROMの見え方そのものが違う**可能性が高い。

そこでCX4について資料を掘り直しました。

複数の実機reader事例やhardware資料を突き合わせると、CX4のregister `$7F52` がROM mapping / chip-selectに関係しており、Rockman X2ではdump前にその状態を切り替える必要があることが見えてきました。

実装では、

```text
CX4検出
  ↓
$7F52 の現在値を保存
  ↓
Rockman X2用のmappingへ変更
  ↓
ROM dump
  ↓
元の値へrestore
```

という最小の操作だけを行います。

永続データを書き換えるものではなく、ROMを読むための一時的なmapping制御です。

結果、Rockman X2は **1.5 MiBのcanonical ROM** として読み出せるようになり、SHA-1も既知の正しいROMと一致。

Databaseでも `Rockman X2 (Japan)` とKNOWNになりました。

前回「まだ知らないことがある」と残した1本が、ちゃんと次の調査につながりました。

---

## カートリッジを挿すと、自分のゲーム棚へ入る

ROMを正しく読めるようになったので、Frontend側からCartridge Adapterを監視し、挿入を検知したら正式なImport経路へ渡します。

```text
Game List
  ↓
Cartridge inserted
  ↓
debounce
  ↓
Dump
  ↓
Canonicalize / Identity
  ↓
ImportService
  ↓
Library refresh
```

Importが成功すると、今回追加されたGameをIDで特定します。

タイトル文字列で検索するのではなく、Import結果が返したLibrary上のidentityを使います。

そしてLibraryを更新したあと、そのゲームを自動で選択してGame Detailへ。

```text
カートリッジを挿す
  ↓
読み出す
  ↓
ゲーム棚へ入る
  ↓
そのゲームが選ばれる
  ↓
Game Detail
```

ここまで来ると、開発用toolを触っている感じがかなり薄くなりました。

---

## 同じゲームをもう一度入れても、増殖しない

物理カートリッジは何度でも挿せます。

だから同じROMをもう一度読んだとき、Libraryに同じGameが増え続けてはいけません。

ここも既存ImportServiceのdedupeをそのまま利用します。

同じROMを再度Importすると、新しいGameを作るのではなく既存Gameのidentityが返ります。

Frontendはその既存Gameを選択すればいい。

「新しく取り込んだ」と「もう持っていた」の違いを、UI側で無理に特別扱いしなくても同じ流れへ戻せます。

---

## そして、PLAY

実機Acceptanceでは、まず通常HiROMの **Sutte Hakkun** を使いました。

結果は、

```text
Cartridge Insert
  ↓
Dump
  ↓
DB KNOWN
  ↓
Import
  ↓
Library refresh
  ↓
自動選択
  ↓
Game Detail
  ↓
PLAY
  ↓
実ゲーム起動
  ↓
SRAM保存
```

まで成功。

初めて、**実物のカートリッジを入口にして、ゲームが動くところまで全部つながりました。**

これまで別々のIssueで作ってきたDevice、ROM Database、Import、Library、Frontend、Sessionが、ここで一本の縦切りになりました。

---

## Rockman X2は、もう一段先があった

Rockman X2も、

```text
実カートリッジ
→ CX4対応dump
→ 1.5 MiB canonical ROM
→ DB KNOWN
→ Import
→ 自動選択
→ Game Detail
→ PLAY要求
```

までは通りました。

ただし実ゲーム起動時、現在使っているCoreが `cx4.data.rom` というCX4用の追加Data ROMを要求しました。

これは今回正しくdumpできるようになった**ゲームROMとは別物**です。

手元にはそのfirmwareがありません。

ここで外から適当なfileを拾ってきて終わりにはしませんでした。

NOA System側はcrashせずGame Detailへ残り、「必要なfileが無い」という具体的な理由を表示できています。

そして、Rockman X2のactual gameplayだけは今回のClose条件から外し、

**実カートリッジからCX4内部Data ROMを取得できないか、あるいはfirmware requirementをNOA Systemとしてどう扱うか**

という次の問題へ分離しました。

ひとつつながると、その先にまた知らなかった境界が出てきます。

---

## レビューで、成功した後始末も詰める

最初の実装が縦に動いたあと、レビューでは3つの安全性を詰め直しました。

ひとつは、filesystemを触るtestをOSのTempではなく専用TestSandboxへ閉じ込めること。

もうひとつは、Import失敗時に一時的なCartridge Staging fileを確実に片付けること。

そして、短いROM prefixが複数Knownになった場合に、勝手にひとつを選ばないこと。

```text
動いた
  ↓
でも失敗したら？
  ↓
候補が複数あったら？
  ↓
途中のfileは残らない？
```

実機で一周できたことと、その一周を安心して繰り返せることは別です。

最終的にはこれらを修正し、自動テストも26/26 PassでAcceptedになりました。

---

## ゲーム機らしい一本の線

最初のDevlogでは、まだ本物のゲームすら動いていない状態で、

```text
Library → PLAY → Session → Exit
```

というゲーム機の一周だけを先に作りました。

そこへ本物のROMが入り、Saveが残り、Databaseがゲームを理解し、Libraryが本物の棚になり、実カートリッジを読めるようになりました。

そして今回、ついに入口が物理カートリッジまで伸びました。

```text
手に持っているカートリッジ
  ↓
NOA System
  ↓
自分のゲーム棚
  ↓
PLAY
```

まだUIは開発途中です。
まだfirmwareの問題も残っています。

でも、かなり最初に思い描いていた「ゲーム機」の形が見えるところまで来ました。

---

## micから

なんか色んなタイプのスーファミソフトを集めてテストしてて、なんでロックマンX2のDBがMatchしないんだろうって試行錯誤してた。
で、まさにこの前始めたROMの詳細の集め方を細分化するのがマッチして、原因を特定するのに役立った。

この頃からEcho, Claude, mic の役回り立ち回りがはっきりしてきたと思う。
初めて実ROM -> Dump -> DB照合 -> Import -> Detail画面 -> Play まで行けて相当感動してた気がする。
（この時はdevlogの構想がなかったので後日書いてます）

--- mic

---

← [前の日記 #11 — カートリッジは、そんなに素直じゃない](0011-when-the-cartridge-fights-back.md)

[次の日記 #13 — ROMだけでは、ゲームは動かない](0013-rom-is-not-enough.md) →
