# #11 — カートリッジは、そんなに素直じゃない

前回は、実物のSFCカートリッジからROMを読み出して、Hashを取り、Databaseでゲームを特定するところまで進みました。

1本の通常LoROMで、

```text
Cartridge
  ↓
ROM Read
  ↓
SHA-1 / CRC32
  ↓
Database
  ↓
KNOWN
```

が通った。

次にやることは自然でした。

**じゃあ、特殊チップが載ったカートリッジも読んでみよう。**

ところがここから、SFCのカートリッジが急に「ただのROM」ではなくなっていきます。

---

## 特殊チップは、ROMの見え方を変える

SFCには、CPUの性能を補ったり、圧縮データを扱ったりするために、カートリッジ側へ追加チップを載せたゲームがあります。

今回対象にしたのは、SA-1、S-DD1、SPC7110、SuperFX、DSP1など。

通常のLoROM / HiROMなら、決まったaddress mappingで順番にROMを読めば済みます。

でも一部の特殊チップでは、ROMのbankをHostから直接読むために、カートリッジ内のregisterを切り替えて「今どのROM windowを見せるか」を指定しなければなりません。

たとえばSA-1、S-DD1、SPC7110では、それぞれ異なるregister sequenceが必要でした。

ここで使うwriteはSaveやROMを書き換えるためのものではなく、**ROMを読むための一時的なwindow切り替え**だけに限定します。

知らないaddressへ推測でwriteはしない。

参考実装、公開されているhardware情報、実機結果を突き合わせて、裏の取れた操作だけを実装しました。

---

## 最初から全部を同じ扱いにはしない

特殊チップだからといって、すべて専用の読み出し処理が必要なわけでもありません。

今回調べた結果、

```text
SA-1      → ROM window切替が必要
S-DD1     → ROM window切替が必要
SPC7110   → 初期化とwindow切替が必要
SuperFX   → 通常のread経路で読める
DSP1      → 通常のread経路で読める
```

という違いがありました。

「特殊チップ搭載」という分類だけを見て処理を増やすのではなく、**実際にROMを読むために何が必要なのか**で分けます。

BigLoROM / ExHiROMについてもaddress mappingは実装しましたが、この時点では対応する実物での検証まではできていません。

分かっていることと、まだ実機で確認できていないことを混ぜないようにしました。

---

## 一度起動したら、カートリッジを次々挿せるようにする

特殊チップ対応を実機で確認するには、何本もカートリッジを差し替える必要があります。

毎回toolを起動し直すのは面倒なので、Cartridge ProbeにWatch Modeを追加しました。

```text
Waiting for cartridge...
        ↓
      挿入
        ↓
   debounce
        ↓
ROM dump / Hash / DB lookup
        ↓
      結果表示
        ↓
      抜去待ち
        ↓
Waiting for next cartridge...
```

1本失敗してもprocessは終了しません。

UNKNOWNでもUnsupportedでも結果を出して、抜いたら次へ進みます。

Game Detail風のTransient Preview UIも案にはありましたが、今回はそこまで広げず、まずconsole上でCanonical Title、Known / Unknown、ROM sizeなどを確認できるところまでにしました。

目的はUIを作ることではなく、**大量の実物をテンポよく調べられる環境を作ること**です。

---

## 実物を連続で試すと、別の問題が出てきた

ここからが、実機検証らしいところでした。

実装時に想定していなかった問題が2つ出ました。

ひとつ目は、カートリッジを挿した直後の**contact bounce**。

物理端子の接触が安定する前にpollすると、挿入直後だけ不安定な状態を拾うことがあります。

そこで、挿入を検知した直後に少し待ち、複数回連続で同じ状態が取れてからdumpへ進むようにしました。

ソフトウェアの世界では「挿さった」は一瞬のstate changeに見えます。

でも現実の端子は、そんなに綺麗には切り替わりません。

---

## HeaderのROM sizeを信じたら、大きすぎた

もうひとつは、もっと面白い問題でした。

SFC HeaderのRomSizeCodeは、基本的に2のべき乗のsizeしか表現できません。

ところが実際のカートリッジには、複数のROM chipを組み合わせた結果、3 MiB、5 MiB、6 MiBのようなsizeも存在します。

その場合Headerだけを見ると、実際より大きいsizeとして読むことがあります。

たとえば今回、

```text
Star Ocean          : Header 8 MiB → DB一致したprefixは6 MiB
Tengai Makyou Zero  : Header 8 MiB → DB一致したprefixは5 MiB
Super Metroid       : Header 4 MiB → DB一致したprefixは3 MiB
```

というケースがありました。

最初は「末尾がmirrorされているからtrimする」と考えました。

ただ、レビューでそこまで断定する根拠はない、と指摘が入りました。

実際に観測できた事実は、

> Header申告sizeより短いprefixを既存ROM Databaseへ照合すると、既知のROMとして一致した

というところまでです。

そこで実装も記録も、`mirrorを除去する` ではなく、**known-ROM prefixが一致した場合にcanonical sizeとして採用する**という表現へ修正しました。

動けばいい、だけではなく「自分たちが本当に確認したことは何か」をレビューで削り出した部分です。

---

## 10本は読めた。1本は読めなかった

最終的な実機結果はかなり良いものでした。

| Title | Mapper / Chip | Result |
| --- | --- | --- |
| Hoshi no Kirby Super Deluxe | SA-1 | KNOWN |
| Super Mario RPG | SA-1 | KNOWN |
| Star Ocean | S-DD1 | KNOWN |
| Tengai Makyou Zero | SPC7110 | KNOWN |
| Star Fox | SuperFX | KNOWN |
| Super Mario Kart | DSP1 / HiROM | KNOWN |
| Sutte Hakkun (NP version) | HiROM | KNOWN |
| Super Metroid | LoROM | KNOWN |
| Super Donkey Kong 2 | HiROM | KNOWN |
| Panel de Pon | LoROM | KNOWN |
| Rockman X2 | CX4 / LoROM | UNKNOWN |

成功したものはfull dump後のSHA-1が既存の正しいROMと一致し、Databaseからcanonical nameまで取得できました。

同じカートリッジを複数回dumpしたものも、毎回同じSHA-1になっています。

一方でRockman X2 / CX4だけは、この時点では正しいROMになりませんでした。

無理に「特殊チップ対応完了」にせず、CX4は未解決として残します。

この1本が残ったことで、むしろ「まだ知らないことがある」という境界がはっきりしました。

---

## Watch Modeだから、cleanupも大事になる

レビューではもうひとつ、長時間動かすtoolになったことでsession cleanupも見直しました。

初期化途中で失敗した場合でも、可能な限りfinish処理を通すようにします。

1回起動して終わるSpikeならprocess終了に任せられる部分でも、Watch Modeでは次のカートリッジが待っています。

```text
1本目で失敗
  ↓
sessionを片付ける
  ↓
2本目を試せる
```

という状態にしておく必要があります。

小さなdebug toolが、実機検証を繰り返すための道具へ少し成長した瞬間でもありました。

---

## 読み出しは、Protocolだけ知っていても足りない

今回かなり強く感じたのは、カートリッジの吸い出しは単にcommandを知れば終わりではない、ということです。

特殊chipのregister。

ROM mapping。

Headerが表現できるsizeの限界。

物理端子の接触。

そして実物から得たROMが、本当に既知の正しいデータと一致するか。

```text
資料
  +
hardwareの仕様
  +
実機観測
  +
Database照合
```

これらを行ったり来たりして、ようやくひとつの「読めた」になります。

前回は、物理カートリッジへ初めて手が届いた回でした。

今回は、その先にある地形が思ったよりずっと複雑だと分かった回でした。

---

## micから

吸い出しってやっぱ大変なんだなって思った。
割と前情報を集めて進めてるつもりだったけど、まだまだ情報が足りない。

docsに情報を集めるときも１ステップではなくて、まず何を集める必要がありそうかを相談して、
その情報を下に詳しく調べる方針にしてみた。

Echoとは、地図の作成と詳細調査っていう名目になってちょっと面白かった。
（正直、よく僕の意図を理解してくれてるなって思う）

--- mic

---

← [前の日記 #10 — カートリッジから、ゲームが読めた日](0010-read-the-cartridge.md)

[次の日記 #12 — カートリッジを挿したら、ゲームになる](0012-cartridge-to-play.md) →
