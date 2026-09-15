# #27 — 壊す前に、地図を描く

前の日記では、Mega Driveの実カートリッジからROMとSaveを読み出しました。

ROMは既知のHashと一致し、Sonic 3のFRAMもShining Force IIのSRAMも、カートリッジに残っていたSaveをNOA Systemへ持ってこられました。

かなりうまくいったように見えます。

でも、その実機確認の途中で、何度も妙な挙動にぶつかりました。

シャイニングフォースを起動しては、また「セーブデータが壊れている」と言われる。

調べる。

直したと思って、もう一度試す。

また違和感が出る。

こういうことを繰り返しているうちに、一つ思うようになりました。

**まだ、それぞれのゲーム機のカートリッジについて知らなさすぎる。**

実装を先へ進める前に、一度きちんと地図を描いた方がいい。

今回は、新しい機能を作った話ではありません。

Mega Drive、Super Famicom、PC Engine、Family Computer / NES、Game Boy Advance。

これから物理カートリッジへ触っていくために、**何が分かっていて、何が分かっていないのかを先に整理した話**です。

---

## 動いたからといって、分かったことにはならない

カートリッジを読み出す処理は、うまくいったときだけ見れば簡単に見えます。

```text
Cartridge
   ↓
Read
   ↓
ROM / Save
```

でも実際には、その間にたくさんの前提があります。

例えばSaveだけでも、Mega DriveにはSRAM、FRAM、EEPROMがあります。

EEPROMも一種類ではありません。

メーカーや基板によって配線が違い、容量も違う。

Emulation Core側では一つのlogicalなSave bufferに見えていても、物理カートリッジ側では全く同じものではありません。

さらに、既存のダンパーがあるcommandを使っているからといって、そのcommandがどういう条件なら安全なのかまで分かったことにはならない。

ここで怖いのは、**それっぽく動いてしまうこと**です。

読み出したbyte数が合っている。

ゲームも起動する。

Save fileもできた。

それでも、たまたま一つのタイトルで成立しただけかもしれません。

だから今回から、実装の前にResearchを一段置くことにしました。

---

## まず「答え」ではなく「地図」を作る

調査を始めるとき、いきなり個別のcommandやtitleへ潜るのではなく、最初にResearch Mapを作りました。

何を調べる必要があるか。

どの情報とどの情報を混ぜてはいけないか。

どこから先が未確認なのか。

例えばMega Driveのpersistent memoryなら、

```text
Game / Media Identity
        ↓
Persistent Memory Profile
        ↓
Physical Cartridge Access
        ↓
Emulator Persistence
```

という層に分けます。

ゲームのidentityが分かることと、EEPROMの配線profileが分かることは別です。

Adapterへcommandを送れることと、そのSave imageがCore側の表現と一致することも別です。

こうして分けておくと、途中までしか分からなかったときに、

```text
ここまではConfirmed
ここからはInferred
ここはUnverified
```

と止められます。

**分からない部分を空欄のまま残せる構造**を先に作ることが、かなり重要でした。

---

## Mega Drive — EEPROMを一種類だと思わない

最初に整理したのは、直前まで苦労していたMega DriveのSaveです。

SRAM、FRAM、I2C EEPROM。

さらに現在のhomebrew環境まで見れば、Flash系のSaveもあります。

特にEEPROMは厄介でした。

EA、Sega、Acclaim、Codemasters / J-Cartなどで、wiringやcapacityが異なります。

ROM headerだけではprofileを一意に決められないものもあります。

一方、Emulation Coreの実装を見ると、product codeやchecksumなど複数のidentity情報を使ってtable-drivenにprofileを選んでいます。

ここで一つ大事な境界が見えました。

**Emulatorが互換性のために推測してよいことと、実カートリッジへwriteするときに推測してよいことは同じではない。**

Emulatorなら、多少のfallbackでゲームが動く方が嬉しい場合があります。

でも物理カートリッジへのwriteでは、間違ったprofileを選んだときに実データを壊す可能性があります。

だからNOAでは、

```text
readなら十分な根拠がある範囲まで
writeならidentity + exact profile + size + backup + verify
```

というように、必要な確信度を変えることにしました。

そしてAdapter側でEEPROM familyをどう解決しているのか分からない部分は、最後までUnverifiedのまま残しました。

分からないなら、まだwriteしない。

それでいいことにしました。

---

## Super Famicom — 「それっぽい長さ」に切らない

次に見直したのはSuper Famicomです。

最初のSystemとしてかなり実機を触ってきたので、ある程度分かっているつもりでした。

でも改めて整理すると、physical dumpの長さと、最終的に保存したいcanonical ROM imageの長さは必ずしも同じではありません。

3 MiB、5 MiB、6 MiBのようなnon-power-of-two ROMもあります。

address space上ではmirrorして見えていても、canonical fileには重複部分を含めない場合があります。

そこでcanonicalizationを、

```text
Physical Acquisition
        ↓
Structural Interpretation
        ↓
Canonical Candidate Generation
        ↓
Trusted Exact-Hash Validation
```

に分けました。

mirrorに見えるから削る。

headerにこのsizeと書いてあるから切る。

Hashが合うまでprefixを試す。

そういうやり方はしません。

Known commercial ROMなら、構造的な根拠からcandidateを作り、trusted whole-file Hashが一致して初めてcanonicalと判断する。

Unknown / Homebrew / Prototypeなら、**分からない部分を勝手に捨てずrawを残す**。

ここでも結論は、「賢く推測する」より「推測していい場所を限定する」でした。

---

## PC Engine — 一つのbyteだけを真実にしない

PC Engine / TurboGrafx-16では、さらに面白い問題がありました。

HuCardとTurboChipではdata lineの並びが異なるため、同じ物理readでもbyte bit-reverseした候補を考える必要があります。

既存実装には、ある1 byteを見てregionを推測するheuristicもありました。

でもNOAでは、それをtruthにはしませんでした。

raw dataから、

```text
as-read candidate
bit-reversed candidate
```

の両方を作り、最終的にはtrusted whole-file Hashでどちらが正しいかを決める。

どちらも一致しなければ、regionを勝手に確定しない。

また、384 KiBの特殊なHuCardでは、単純に先頭384 KiBを切ればよいわけではなく、physical address上の別々の領域を組み合わせてcanonical imageを作る構造も見えてきました。

つまり、

**「何byte読めたか」だけでは、そのROMが何なのか分からない。**

物理配置と論理的なgame imageを分けて考える必要があります。

---

## Family Computer / NES — そもそも「ROM一個」ではない

Family Computer / NESを調べ始めると、さらに前提が変わりました。

ここでは、カートリッジを単一のROM blobとして考えること自体が危険です。

```text
Physical Cartridge
├─ PRG ROM
├─ CHR ROM / CHR RAM
├─ mapper / board hardware
├─ mirroring / IRQ / audioなどのbehavior
├─ writable resource
└─ physical interface
```

一般的な `.nes` fileにはheaderがありますが、それは物理カートリッジ上にそのまま存在するbytesではありません。

mapper番号も、physical board identityそのものではありません。

CHR-ROMがなくCHR-RAMを使う構成も正常です。

mirroringもROM payloadではなくboard behaviorです。

なのでNOA内部では、将来的に単一の`.nes` fileを絶対的なsource of truthとするより、

```text
Canonical Cartridge Record
├─ PRG resource
├─ CHR resource / RAM profile
├─ board profile
├─ writable resources
└─ export metadata
```

のように考える方が自然だと整理しました。

これはまだ実装ではありません。

でも、ここを先に決めずに「とりあえずNESのROMを吸おう」と始めていたら、あとでかなり苦しくなっていたと思います。

---

## Game Boy Advance — 読めることと、Saveへ触れることを分ける

Game Boy AdvanceはROM mapping自体は比較的素直ですが、Saveと特殊hardwareが一気に複雑になります。

SRAM / FRAM。

Flash 64 KiB / 128 KiB。

EEPROM 512 B / 8 KiB。

さらにRTC、solar sensor、tilt、gyro、rumbleなどもあります。

FlashやEEPROMは、readのためのidentificationですらcommand writeが必要になる場合があります。

つまり「read-only調査だから安全」と単純には言えません。

そこでGBAでも、

```text
ROM acquisition
   ↓
raw保存
   ↓
header / structure
   ↓
identity
   ↓
board / save profile
   ↓
必要になって初めてpersistent memoryへ触る
```

という順序を固定しました。

既存ダンパーの実装も調べましたが、そこにあるheuristicをそのままNOAへ移植することはしませんでした。

例えば、一定sizeごとにDatabase一致を探す方法や、EEPROM sizeを反復patternから縮める方法は、既知タイトルには便利でもUnknown cartridgeでは情報を失う可能性があります。

**既存ツールが長年動いていることと、その判断をNOAの安全契約として採用できることは別。**

これも今回のResearch全体で何度も出てきた考え方です。

---

## 「分からない」を成果物にする

今回のResearchで一番変わったのは、資料の量ではありません。

Unverifiedを残すことへの抵抗がなくなったことだと思います。

開発をしていると、空欄を見ると埋めたくなります。

Unknownを見ると、何か推測して先へ進みたくなります。

AIを使っていると特に、もっともらしい答えはかなり簡単に作れてしまいます。

だからこそ、

```text
Public specificationで確認したこと
Emulator sourceで確認したこと
既存toolの静的解析で見えたこと
Synthetic testで再現したこと
実カートリッジで確認したこと
まだ分からないこと
```

を意識的に分けるようにしました。

そして最後の一行が残っていても、Researchは完了にしてよい。

**「ここはまだ分からないので触らない」と判断できる状態まで整理できたなら、それも立派な完了です。**

これは、物理メディアへ触るNOAにとってかなり大事な考え方になりました。

---

## AIを一人の万能担当にしない

この調査期間は、AIとの作業の仕方も少し変わりました。

大量のResearchを一人のAIへ丸ごと投げるのではなく、問題を小さく分けます。

私は全体の論点を整理し、何を確定させる必要があるか、どの資料同士をcross-checkするか、どこで止まるべきかを一緒に組み立てる。

特に難しい調査はCodexへ深く掘ってもらう。

実装や再現用のprogramが必要になればClaudeへ渡す。

そして最後は、人間が実物で確かめる。

```text
mic
  ├─ 目的 / 違和感 / 実機確認
  │
Echo
  ├─ 問題分解 / 調査設計 / cross-check / review
  │
Codex
  ├─ 深い個別Research
  │
Claude
  └─ 実装 / test / 再現
```

もちろん、こんなに綺麗な分業表の通り毎回進むわけではありません。

行ったり来たりもします。

でも「AIを使う」というより、**能力の違うメンバーへ仕事を割り振る**感覚に近くなってきました。

そしてAIが出した答えそのものより、

- 何を聞いたか
- 何と照合したか
- どこまで確定したか
- 何を未確認のまま残したか

の方が重要になってきました。

---

## 実装を止めたことで、先へ進めるようになった

一見すると、この期間は新しいSystemが動いたわけでも、新しいUIが増えたわけでもありません。

Research documentが増えただけです。

でも実際には、

- Mega Driveのpersistent memory
- Super Famicomのcanonicalization
- PC Engine / TurboGrafx-16のHuCard mapping
- Family Computer / NESのcartridge resource model
- Game Boy AdvanceのROM / Save / special hardware

について、どこからなら安全に実装を始められるかが見えるようになりました。

これはかなり大きいです。

「次は何を試そう」ではなく、

**「次はここまでなら触っていい」**

と言えるようになったからです。

物理カートリッジを扱うプロジェクトでは、実装速度だけが速いことは必ずしも強さではありません。

壊す前に止まれること。

分からないものを分からないと記録できること。

そして、必要になったときに戻ってこられる地図があること。

NOA SystemのResearchは、そのための装備になってきました。

---

## micから

前のMega DriveのSaveまわりで、何十回もシャイニングフォースの「セーブデータが壊れてるよ！」みたいな画面を見ることになった。

そこで、まだそれぞれのハードについて調査が足りないなと思って、今まで集めていた資料も含めて一度ちゃんと整理することにした。

とはいえ、僕自身が全部の資料を一枚ずつ読むというより、AIが集中して調べやすいようにタスクを分けて、Echoと相談しながら順番に投げていく感じ。

その中でも特に難しそうな調査をCodexへ任せたときは、結果を見たEchoまで驚いていて、これはすごいなと思った。

一方で、深く調べれば調べるほど計算資源が勢いよく溶けていくのも目の前で見えて、そこはちょっと面白かった（笑）。

それでも、一人で何週間も資料を追うことを考えると、今のAIとの共同作業は凄まじい効率だと思う。

今回いちばん良かったのは、全部の答えが出たことじゃない。

「ここは分からないからまだ触らない」と言えるところまで、ちゃんと分けられたことだった気がする。

--- mic

---

← [前の日記 #26 — 実物のカートリッジが、NOAへ渡ってきた](0026-cartridge-crosses-over.md)  
[次の日記 #28 — 作るための道具も、NOAの中へ →](0028-tools-for-building.md)
