# #28 — 作るための道具も、NOAの中へ

前の日記では、Mega DriveのSaveまわりで何度も違和感にぶつかったことをきっかけに、実装を急がず複数のゲーム機についてResearchし直しました。

あの期間で一つはっきりしたことがあります。

**実装そのものより、確認する作業の方が大変になることがある。**

特にSaveやAutoSnapのように「前回の状態を自動で戻す」機能が増えてくると、普段は便利な機能が、デバッグ中だけは原因の切り分けを難しくします。

Sonic 3のSaveを調べたい。

でも起動するとAutoSnapから再開してしまう。

AutoSnapを消して試す。

もう一度起動する。

今度は新しいAutoSnapが作られる。

また消す。

こういうことを何度も繰り返していました。

そこで、ゲームを遊ぶための機能だけではなく、**NOA Systemそのものを作るための道具も、NOAの中へ用意する**ことにしました。

今回はDeveloper Debug MenuとScreenshot機能の話です。

---

## 便利な機能を、一時的に黙らせたい

AutoSnapは、通常利用ではかなり便利です。

ゲームを終了すると自動で現在の状態を残し、次にPLAYしたときはそこから続きを始められる。

でもBattery Saveの検証をしているときには、その便利さが逆に邪魔になります。

確認したいのは、

```text
Persistent Save
      ↓
CoreへRestore
      ↓
通常Boot
```

という経路なのに、AutoSnapがあると、

```text
Persistent Save
      ↓
通常Boot
      ↓
AutoSnap Load
```

となり、最終的に見えている状態がどちら由来なのか分かりづらくなります。

必要なのはAutoSnapを削除することではありません。

**今回は使わない、というだけです。**

そこでDeveloper Debug Menuを作りました。

---

## F12で、開発中だけの操作を出す

Game DetailでF12を押すと、Developer Debug Menuが開きます。

初期版で必要だったのは、大きなdebuggerではありませんでした。

```text
AutoSnap Creation      ON / OFF
AutoSnap Auto Resume   ON / OFF
Delete AutoSnap

System
Core
ROM / Media path
Save path
AutoSnap exists
```

これだけです。

重要なのは、AutoSnapの生成とAuto Resumeを別々に切れることでした。

例えば、

- 既存AutoSnapは残したい
- 今回だけAuto Resumeしたくない

という場合があります。

逆に、

- Auto Resumeは使ってよい
- でも今回の終了時には新しいAutoSnapを作りたくない

という場合もあります。

二つを一つの「AutoSnap OFF」にすると、検証したい条件を正確に作れません。

なので独立したRuntime flagにしました。

しかもこの設定は保存しません。

アプリを再起動すれば必ず通常設定へ戻ります。

開発用設定をOFFにしたまま忘れて、「なんでResumeしないんだろう」と未来の自分が悩むのを防ぐためです。

---

## Debug UIだからといって、本体へ直結させない

急いで作った機能ではありますが、Debug MenuからSession内部の変数を直接書き換える形にはしませんでした。

```text
Developer Debug Menu
        ↓
Developer Runtime Settings
        ↓
AutoSnap policy
```

という小さな層を挟みます。

Game DetailやSession側は「Debug Menuが存在するか」を知りません。

ただ現在のpolicyを問い合わせるだけです。

Debug Menuを消しても、設定の入口を将来変えても、AutoSnap本体の責務は変わらない。

開発用の機能ほど雑に本体へ刺さりやすいので、ここは少し意識しました。

---

## 本当に、テストが楽になった

実機では、

- AutoSnap Creation ON / OFF
- AutoSnap Auto Resume ON / OFF
- 選択中GameのAutoSnap削除
- 削除後もManual Save Stateが独立して使えること
- F12 / ESCでMenuを閉じられること

を確認しました。

これでBattery Saveを調べるとき、毎回fileを手で探して消したり、どの復元経路を通ったのか疑ったりする必要がかなり減りました。

ユーザー向けの新機能ではありません。

でも開発者側から見ると、こういう小さな道具の方が日々の速度を大きく変えることがあります。

---

## 次に欲しくなったのは、「証拠を残す」ボタンだった

検証を繰り返していると、もう一つ面倒な作業があります。

Screenshotです。

新しい機能が動いた。

珍しい挙動が出た。

UIが良い感じになった。

Devlogへ残しておきたい。

でも、そのたびにOS側のScreenshot操作をする必要がありました。

しかも開発初期の画面は、意識して撮らない限り残りません。

後から振り返って、

「あの頃の画面、ほとんど残ってないな」

となります。

AutoSnap Previewを作ったことで、NOAには既にgame frameをPNGへ変換する仕組みがありました。

だったら、任意の瞬間にも同じ経路を使えるようにします。

---

## F1で、その瞬間を残す

Screenshot機能では、F1を最初のtriggerにしました。

```text
F1
  ↓
Screenshot Action
  ↓
Capture Target
  ↓
PNG Encode
  ↓
Screenshot Store
```

保存先はGameごとに分け、時刻を含むfilenameで保存します。

同じ秒に何枚撮っても上書きせず、連番を付けます。

保存自体も一時fileからrenameする形にして、途中失敗で中途半端なPNGを残しにくくしました。

AutoSnap PreviewとはPNG化の低レベル処理を共有しますが、保存物としての寿命は別です。

```text
AutoSnap Preview
= AutoSnapに従属する画像

Manual Screenshot
= 独立して残す記録
```

AutoSnapを削除しても、Screenshotは消えません。

これは後になってかなり重要な違いになりそうです。

---

## 「ゲーム画面だけ」と「今見えているNOA」を分ける

最初はgame frameだけ撮れれば十分だと思っていました。

でも実際に使い始めると、Devlogで残したいものはゲームそのものだけではありません。

Libraryの画面。

Game Detail。

InGame Menu。

NOAのUIも残したい。

そこでF1の意味を、現在のcontextによって変える形にしました。

```text
Gameplay中
  → original Game Frame

InGame Menu表示中
  → Menu込みのFrontend Frame

Library / Game Detail
  → Frontend Frame
```

一方、InGame Menuの `SCREENSHOT` を選んだ場合は、menuを写さずcleanなGame Frameを撮ります。

つまり、

```text
F1
= 今見えているものを残す

InGame Menu > SCREENSHOT
= ゲーム画面だけを残す
```

という役割分担になりました。

Screenshotという一つの機能でも、残したいものには少し違う意味があります。

---

## 開発中の画面も、あとからは戻せない

NOA SystemではSaveやStateをかなり大事にしています。

ゲームをどこまで遊んだか。

最後にどこにいたか。

昔のカートリッジに何が残っていたか。

そういうものは、後から再現できないことがあります。

考えてみれば、開発中の画面も同じでした。

最初のDummy Library。

まだフォントが仮だった頃。

初めてGame Detailが出た瞬間。

UIが少しずつNOAらしくなっていった途中。

完成したものだけ見れば、全部消えてしまう景色です。

Screenshot機能は最初、Devlogの証拠を撮るための便利機能として作りました。

でも使い始めると、これは**NOA System自身の成長過程を保存する機能**でもあるように見えてきました。

ゲームを保存するシステムが、自分自身の変化も少しずつ保存し始めたことになります。

---

## 作る人の摩擦も、放置しない

Developer Debug MenuもScreenshotも、最初から製品の中心機能として計画していたものではありません。

開発中に、

「これ毎回やるの面倒だな」

と思ったところから生まれました。

以前なら、開発だから仕方ないと我慢していたかもしれません。

でもNOAでは、ユーザーの操作摩擦を減らすのと同じように、開発者側の摩擦も少しずつ減らすことにしました。

AIによって実装速度が上がると、むしろ人間側の確認作業がボトルネックになる場面が増えます。

なら、確認するための道具も作る。

記録するための道具も作る。

**速く実装するだけでなく、速く確かめられる環境を作る。**

これもAIと一緒に開発する上で、かなり大事な部分になってきました。

---

## micから

SRAMまわりのチェックは本当に面倒だった。

AutoSnap自体は普段めちゃくちゃ便利なんだけど、Saveの復元だけを確認したい時には、その便利機能のせいで「今どっちから戻ったんだ？」ってなる。

それで急遽Debug Menuを作って、AutoSnap CreationとAuto ResumeをそれぞれON/OFFできるようにした。

これだけでテストがめっちゃしやすくなったー。

そしてScreenshot。

僕はScreenshotとか録画がかなり好きなので、この機能は普通に嬉しい。

Devlog用の画像もNOAからそのまま撮れるようになったから、これからは開発中の画面をちゃんと残していけそう。

逆に言うと、開発初期は手動で撮らないと何も残らなかったから、最初期の画面はあまり撮ってないんだよね。

今になってちょっと惜しい。

でも、そう思った時点から残せるようになったのは良かったと思う。

--- mic

---

← [前の日記 #27 — 壊す前に、地図を描く](0027-draw-the-map-first.md)

[次の日記 #29 — 古い続きを、勝手に戻さない](0029-dont-restore-the-old-future.md) →
