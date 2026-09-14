# #25 — 二台目で、設計が試された

ここまでのNOA Systemは、ずっとSuper Famicomを中心に育ててきました。

Library、PLAY、Controller、Save、Save State、AutoSnap、Preview、Overlay。

機能を追加するたびに、できるだけ「SFC専用の仕組み」にはしないようにしてきました。

でも、それが本当に共通設計なのかは、SFCしか動かしていない間は分かりません。

名前だけGeneralにしていて、実際にはSFCの事情が染み込んでいるかもしれない。

そこで、二台目のSystemとしてMega Driveを追加しました。

今回面白かったのは、Mega Driveが動いたことそのものより、その後でした。

新しいSystemのために作り直すつもりだった機能が、次々に**そのまま動いてしまった**のです。

二台目を追加することで、これまで作ってきた設計が初めて試された話です。

---

## 「Mega Drive版」を作らない

最初に決めたことは単純でした。

Mega Driveを追加するからといって、Mega Drive専用のGame DetailやSessionを作らない。

```text
SFC Session
MD Session
```

という二本立てにはしません。

ゲームがどのSystemなのかを見て、対応するCoreを選ぶ。

その先は、これまで使ってきた同じEmulation Sessionへ流します。

```text
Game
  ↓
System
  ↓
対応するCoreを解決
  ↓
共通のSession
```

SFC向けに固定されていた箇所は、必要な範囲だけSystemから解決できる形へ直しました。

入力まわりも同じです。

もともとlibretroの共通Controller abstractionを使っていたので、SFC用の名前になっていた部分をGeneralな名前へ整理し、Mega Drive専用Input Layerは増やしませんでした。

この段階では、まだ「設計が共通だった」とは言えません。

ただ、少なくとも二台目を無理やり横へコピーせずに起動経路へ入れられる形にはなりました。

---

## 本当に別のゲーム機が動いた

実際のMega Drive ROMをLibraryへ入れ、Game DetailからPLAYします。

そこで二台目のCoreが選ばれ、実ゲームが起動しました。

Video、Audio、Controller、Keyboard fallback、Exit。

一通り確認して、正常にGame Detailへ戻ります。

これだけなら、普通の「Mega Drive対応」でした。

でも確認中に、少し予想外のことが起きました。

Battery Saveまで、すでに動いていました。

Mega Drive用Save処理をまだ作っていないのに、ゲーム内で保存してSessionを終えると、SaveがNOA SystemのLibraryへ残っていたのです。

---

## 「対応する」Issueで、実装することが無かった

次の作業では、Mega DriveのBattery Saveを既存Save基盤へ接続する予定でした。

ところがコードを追ってみると、接続するものがほとんどありませんでした。

以前SFCのSaveを作ったときから、保存先はSystemのidentityを受け取り、Session側も特定Systemを前提にしない形になっていました。

Mega Driveが正式にSystemとして解決できるようになった時点で、そのまま同じ経路へ流れていたのです。

```text
SFC ─┐
     ├─> 共通Save基盤
MD  ─┘
```

そこでこの作業では、新しいSave実装を足す代わりに、

- Systemが違えばSaveの場所も安全に分かれること
- Mega Driveでも実際にSaveを往復できること
- 既存SFCのSaveを壊していないこと

を確認するTestとDocumentationを追加しました。

**機能追加のIssueなのに、production codeの変更が無い。**

一見すると何も作っていないようですが、今回はむしろそれが良い結果でした。

---

## Save Stateも、AutoSnapも、Previewも

同じことが、その次でも起きました。

Mega DriveでManual Save State、Load State、AutoSnap、Auto Resume、Preview Screenshot、プレイ中Overlayを確認します。

ここも当初は、二台目を入れたことでSFC固有の前提がいくつか出てくるだろうと考えていました。

しかしproduction code側では、ほぼ見つかりませんでした。

Stateにはもともと、

```text
ROM / Media identity
System
Core
Core Version
Schema Version
```

などの互換性情報が入っています。

だからMega DriveのStateをSFCへ誤って適用することもありません。

AutoSnapも同じSave State基盤の上にあります。

PreviewもFrameの幅や高さを毎回見て扱うので、System固有の固定解像度を前提にしていませんでした。

Overlayもゲーム内容には依存しません。

結局、実装側で見つかったSFC固定は主にTest helperの中だけでした。

実際の製品コードより、テストコードの方が先に二台目で引っかかったのは少し面白い結果でした。

---

## 二台目は、新機能ではなくテストだった

SFCだけを作っている間も、ずっと「あとで別のSystemが増える」ことは意識していました。

でも設計というものは、未来を想像してGeneralにしたつもりでも、本当にGeneralかどうかは分かりません。

抽象化しすぎているかもしれない。

逆に、どこかに一台目の都合が残っているかもしれない。

二台目を実際に入れて初めて、その答えが出ます。

今回Mega Driveを追加して分かったのは、全部が完璧だったということではありません。

ROM Databaseなど、まだSystemごとに整理した方がよい部分も見つかりました。

Cartridge Adapter側も、この時点ではまだSFC中心です。

でも、ゲームを起動して遊び、保存し、Stateを作り、続きを残し、Previewを見て、Overlayを使って終了するという**NOA Systemの中心部分**は、そのまま二台目でも使えました。

これはかなり大きな確認でした。

---

## 「共通にした」ではなく、「共通だったと分かった」

今回の作業では、Mega Drive向けに大量の機能を追加したわけではありません。

むしろ後半になるほど、追加するコードが減っていきました。

最初にSystemとCoreをつなぐ。

すると、Saveがそのまま動く。

Stateも動く。

AutoSnapも動く。

Previewも動く。

Overlayも動く。

それまでSFCのために一つずつ作ってきたものが、別のゲーム機でも同じ意味を持ち始めました。

**二台目を追加したことで、初めて一台目の設計を評価できた。**

そんな作業だったと思います。

NOA Systemが「Super Famicomを遊ぶためのFrontend」から、少しだけ本当の意味で「System」へ変わった瞬間でもありました。

次は、ファイルから動かすだけではなく、実際のMega Drive Cartridgeをどう扱うかへ進んでいきます。

---

← [前の日記 #24 — 最後にいた景色を、残す](0024-last-scene.md)
