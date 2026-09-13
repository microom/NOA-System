# #10 — カートリッジから、ゲームが読めた日

ここまでのNOA Systemは、すでにROM fileをImportして、DatabaseでIdentityを調べ、Libraryに並べて遊べるようになっていました。

でも、そのROM fileはまだ外から用意したものです。

今回やりたかったのは、その一歩手前。

**実物のカートリッジから、自分でROMを読む。**

RetroFreakのCartridge AdapterをWindowsにつなぎ、SFCカートリッジをread-onlyで読み出して、既存のROM Databaseまでつなげます。

Libraryへ入れるのはまだ先。

今回はまず、物理カートリッジから「正しいROM image」が取り出せることを確かめる回です。

---

## Adapterを、まず普通のDeviceとして扱う

RetroFreak Cartridge Adapterは、WindowsではCDCのUSB Serial Deviceとして見えます。

最初の実装では、そのCOM PortをWindows側で検出し、上位のDevice logicとはTransport abstractionで分離しました。

```text
SFC Reader / Protocol
        ↓
Cartridge Transport
        ↓
Windows COM Port
```

今はWindowsですが、上位側を「COMポート機器」と決めつけないようにしています。

将来Pi/Linuxへ移ったときにraw USBや別Transportへ差し替えられるよう、Platform都合は下側へ閉じ込めます。

このIssueは完成したDevice Serviceではなく、最初の実機Spikeです。

それでも、最初からこの境界だけは残しました。

---

## まずは「刺さっているか」を聞く

いきなりROMを読み始めるのではなく、まずAdapterへCartridge Statusを問い合わせます。

実機で確認できたのは、

```text
Adapter接続
  ↓
No Cartridge
  ↓
SFC Cartridge inserted
  ↓
SFCとして識別
  ↓
Cartridge removed
  ↓
No Cartridgeへ戻る
```

という基本の一周です。

カートリッジ無しではtype 255、SFCを挿すとtype 1。

抜いたあとも安全にNo Cartridgeへ戻ることを確認しました。

ROM dumpより地味ですが、物理Deviceを相手にするなら、この「今どういう状態なのか」を確実に取れることが最初の土台になります。

---

## 返事が来ない原因は、DTR / RTSだった

実機でひとつ、資料だけでは分からなかったことも見つかりました。

WindowsのCOM Portを開いただけでは、Adapterがまったく返事をしません。

調べていくと、DTR / RTSを明示的に有効にして、CDC ACMのcontrol line stateをHost側から送る必要がありました。

```text
COM Port Open
  ↓
DTR / RTS Enable
  ↓
Adapterが応答開始
```

ここを省略すると、Cartridge Statusへの応答すら返りません。

こういう「Protocol packet自体は合っているのに、周辺の初期化がひとつ足りない」というのは実機らしいところです。

分かった内容はDeviceの設計資料へ戻し、今後のReferenceにしました。

---

## そして、SFCのROMを読む

Statusが取れたら、次はSFCのHeaderを読み、ROMの配置とsizeを判断してdumpします。

今回まず対象にしたのは通常のLoROM / HiROMです。

特殊chipや特殊mappingを最初から全部解こうとはせず、まず普通のカートリッジを正しく最後まで読めることを優先しました。

実機Acceptanceに使ったのは、SFCの **Panel de Pon**。

通常LoROM、1 MiBのカートリッジです。

読み出しは最後まで成功しました。

さらに同じカートリッジをもう一度dumpして、SHA-1とCRC32を比較します。

結果は同一。

そして、すでに持っていた検証済みROMのSHA-1とも一致しました。

つまり、

```text
Physical Cartridge
        ↓
Cartridge Adapter
        ↓
ROM Read
        ↓
1 MiB ROM image
        ↓
SHA-1 / CRC32
```

までが、実物から決定的に再現できました。

単に「それっぽいbyte列が取れた」ではなく、**正しいROM imageを読めた**ところまで確認できたことが重要です。

---

## 読めたROMを、既存Databaseへ渡す

ROMが正しく読めたなら、ここから先はすでに作ってきたIdentity pipelineを使えます。

新しくDevice専用の照合処理を作るのではなく、読み出したROM imageのSHA-1を既存Databaseへ渡します。

結果は、

```text
KNOWN
Panel de Pon (Japan)
```

でした。

物理カートリッジから読んだROMが、そのまま既存のROM Identityへつながったことになります。

これまで別々に作ってきた、

```text
ROM Database
Identity
Device
```

が、ここで初めて一本の線になりました。

---

## でも、Libraryにはまだ入れない

この回では、あえてImportしませんでした。

```text
Physical Cartridge
  ↓
ROM Read
  ↓
Hash
  ↓
Database Lookup
  ↓
ここまで
```

Library登録も、Game作成も、Frontendへの追加もなし。

理由は単純で、Device layerそのものが正しくROMを読めるのかを、Importの問題と混ぜずに確認したかったからです。

実際、Debug用のCartridge ProbeはLibraryやImport Serviceへ依存しない独立したtoolとして作っています。

ここで境界を切ったことで、読み出しに失敗したときに「Deviceが悪いのか、Importが悪いのか」が曖昧になりません。

---

## 書き込み機能は、まだ作らない

実物のカートリッジを扱う以上、Data Safetyもかなり明確にしました。

今回のDevice pathは完全read-onlyです。

ROMやSave RAMへ書く命令は実装せず、呼び出し経路も作りません。

Protocol上にWRITE系commandが存在していても、必要だからといって先回りして実装しない。

特殊chipのbank/window切り替えのようにROM readのため一時的な制御が必要になる場合も、永続データへのwriteとは明確に分けて考えます。

まずは、**読むだけなら安心して触れるDevice layer**を作ることを優先しました。

---

## 特殊カートリッジは、次へ

SFCには、通常のLoROM / HiROMだけでは読めないカートリッジもあります。

SA-1、S-DD1、SPC7110、BigLoROM、ExHiROMなどです。

今回はそれらを無理に完全対応せず、検出できるところまでに留めました。

通常の1本で、

```text
接続
→ 状態取得
→ ROM Read
→ Hash一致
→ DatabaseでKnown
```

が通った。

まずはこの縦切りを成立させてから、特殊chipの実物を相手に次の問題を解く方がいい。

この判断はレビューでもそのままAcceptedになりました。

---

## 実物と、これまで作った世界がつながった

ROM Databaseを作っていた頃は、それはまだ「ファイルを理解する仕組み」でした。

Libraryを作った頃は、「持っているROMをゲームとして並べる仕組み」になりました。

そして今回は、そのさらに手前にある現実のカートリッジから情報が入ってきました。

**カートリッジを挿して、読んで、hashを取り、それが何のゲームか分かる。**

まだLibraryには入りません。

でも、NOA Systemの外側にあった物理メディアへ、初めて手が届いた回でした。

---

## micから

これテストする時、遂にダンプが出来てしまうのか・・・！？
ってワクワクしてやってみて、あれ？吸い出しはされてるみたいだけどライブラリにでないよ？
ってEchoに相談したら、

Echo「このissueはダンプのテストでインポートはその先です」

って言われて、うん、ああ、そうだよね知ってたよ！ごめんごめん。みたいに話してた気がする。
（ちゃんと僕もissueの内容をチェックしないとダメですねと引き締まりました）

--- mic

---

← [前の日記 #9 — ゲームの名前を、ちゃんと書けるようにする](0009-true-type-text.md)
