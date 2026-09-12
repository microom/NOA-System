# #4 — データベースより先に、その故郷を保存する

前回までで、ゲームを起動し、遊んだ記録をSRAMとして残せるところまで進みました。

次に必要になったのは、取り込んだROMが「何のゲームなのか」を確かめるための情報です。

ただし、ここでいきなりROM Databaseそのものを作るのではなく、まずその元になる一次資料をどう残すかから始めました。

---

## Databaseそのものを正本にしない

今回決めた方針は、かなり単純です。

> **Databaseを所有するのではなく、出典が明確な情報から信頼できるDatabaseを再現する仕組みを所有する。**

SQLiteなどのDatabaseは便利ですが、それ自体を唯一の正としてしまうと、あとから「この情報はどこから来たのか」「同じDatabaseをもう一度作れるのか」が分からなくなります。

そこで、NOA SystemではDatabaseより先に、その材料となるSource Snapshotを保存することにしました。

```text
Preserved Source Snapshot
 + Provenance / Manifest
 + Build Tools
        ↓
再現可能なROM Database
```

生成したDatabaseを消してしまっても、元資料と手順が残っていれば作り直せる。

今回作ったのは、そのための土台です。

---

## 最初の一次資料としてMAME 0.289を保存する

SFCのROM識別情報の最初のSourceとして、MAMEのSoftware Listを採用しました。

使ったのはMAME 0.289の固定Snapshotです。

可変の`master`から最新版を取るのではなく、`mame0289`が指すcommitを固定し、そこから必要な資料を保存しました。

保存したのは、SFC Software List本体だけではありません。

```text
ROMDatabaseSources/
└ Archives/
   └ MAME/
      └ 0.289/
         ├ snes.xml
         ├ softwarelist.dtd
         ├ hash-README.md
         └ COPYING
```

`snes.xml`が参照するDTD、そして`hash/`配下がCC0であることを確認できるライセンス資料まで、一緒に残しています。

単にデータだけをコピーするのではなく、「なぜこのSourceを使ってよいのか」まで後から追える形にしました。

---

## 出典をmanifestへ残す

保存したSourceには、machine-readableなmanifestを用意しました。

そこには、Source名だけではなく、version、revision、commit、取得元URL、license、SHA-256、保存先などを記録しています。

これで将来Sourceが増えても、どの資料を使ってどのDatabaseを作ったのかを追跡できます。

特にSHA-256は、保存した原本が後から変わっていないことを確認するために使います。

---

## 「残すもの」と「作り直せるもの」を分ける

今回もうひとつ整理したのが、データの寿命です。

```text
Archives   = 採用した一次資料。消してはいけない
Extracted  = 作業用。消して再生成してよい
Generated  = Database等の生成物。消して再生成してよい
```

ここを曖昧にしないことにしました。

`Library/`はユーザー自身のROMやSaveを置く場所。

`Runtime/`は実行時に必要なもの。

ROM DatabaseのSourceは、それらとは別の責務として扱います。

また、「Gitに入っているか」と「長期保全すべきか」も別問題として考えます。

今回はMAMEの資料が合計約2.8MBで、ライセンス上も保存可能だったため、採用Source SnapshotそのものをGit管理することにしました。

---

## 保存した資料だけで検証する

Sourceを保存しただけでは、壊れていても気づけません。

そこで、ネットワークへアクセスせずにSnapshotだけを検証できる`validate_source.py`も作りました。

確認しているのは、たとえば次のようなことです。

- 保存した各SourceのSHA-256がmanifestと一致する
- XMLとして読み込める
- SFC Software Listとして期待する構造を持っている
- Software entryが存在する
- ROMのCRC / SHA-1候補が存在する
- F-Zero (Japan) と Chrono Trigger (Japan) がSource内に存在する

実際のMAME 0.289 Snapshotでは、3710件のSoftware entryを確認できました。

F-ZeroとChrono Triggerも、以前の実機確認で使った名前と一致するrecordが見つかっています。

この時点ではまだ、手元のROMとhashを照合してはいません。

今回はあくまで、「信頼できる材料を固定し、その材料が正しく残っていることを確認できる」ところまでです。

---

## 一度レビューで止めた

最初の実装レビューでは、validation scriptにひとつ問題が見つかりました。

F-ZeroやChrono Triggerのような期待タイトルが見つからない場合でも、表示上は`MISSING`と出すだけでvalidation自体は成功扱いになっていました。

これは「検証」と呼ぶには弱いので、期待タイトルが欠けていたら明確にfailureになるよう修正しました。

正常系が通るだけではなく、壊れた場合にちゃんと止まることも確認しています。

こういう小さなレビューを積み重ねることで、Sourceを「置いてある資料」ではなく「再現可能性を担保する資料」にしていきます。

---

## Databaseより先に、その故郷を残す

ROM Databaseを作り始めるなら、普通はまずschemaやlookup処理を考えたくなります。

でも今回は、その一歩手前で止まりました。

将来Databaseを作り直したくなったとき、あるいは配布元の内容が変わったときに、採用した情報がどこから来たのか分からなくなる方が怖かったからです。

Databaseは作り直せる。

でも、その根拠になった一次資料を失えば、同じものを本当に再現できるかは分からない。

NOA Systemで保存したいのは、ROMだけではなく、**そのROMを理解するために使った根拠まで含めた記録**なのだと思います。

---

## micから

ROM照合のDB準備だったかな。
この辺りから今のワークフローがはまり始めて、AIとのやり取りを基本的に全てGitHub経由にした。

相談はECHOに直接話して、資料集めの結果や必要なドキュメントも全てGitHubに入れてもらう運用。

最初懸念してたレビューの流れややり取りも、全てissueに記載してもらうことで、僕の稚拙な表現ではなく、お互いのAI同士が結果とレビューをやり取りして、とても手堅い実装が実現できてる気がする。

内容を把握できてないのはまずいので、ECHOには僕にわかるようにレビュー内容などを報告してもらってる。

これは革命的に便利だし、やり取りの記録まで残るようになってるから本当に最高

— mic

---

← [前の日記 #3 — ゲームが残るなら、遊んだ時間も残したい](0003-keep-the-time-we-played.md)

[次の日記 #5 — 消しても困らないROM Database](0005-rebuildable-rom-database.md) →
