# #2 — 初めて本物のゲームが動いた日

前回まで、PLAYの先にあったのはDummy Sessionでした。

Libraryからゲームを選び、Game Detailを開き、PLAYして、Sessionを終えて戻ってくる。その一周はできたけれど、まだそこに本物のゲームはありませんでした。

今回は、そのDummy Sessionの向こう側へ初めて実ゲームをつなぎました。

自分で吸い出したSFC ROMを開発用の入口からImportし、Libraryへ登録し、PLAYする。

そしてSDL3のWindowの中で、Chrono Triggerのオープニングにある振り子が動きました。

---

## ImportからPLAYまでを一本につなぐ

今回やりたかったのは、単にlibretro Coreを呼んでROMを起動することではありませんでした。

NOA Systemの中で、ゲームが取り込まれ、Libraryに登録され、そのゲームのGame DetailからPLAYされ、遊び終わったらまた元のゲームへ戻ってくるところまでを一本の流れとして成立させることです。

```text
Development Import Source
        ↓
Import Service
        ↓
Hash / Store / Register
        ↓
Library
        ↓
Game Detail
        ↓
PLAY
        ↓
Session
        ↓
libretro Core
        ↓
実ゲーム
        ↓
Exit
        ↓
Game Detail
```

開発中はFile-based Sourceを使っていますが、Import SourceとImport処理そのものは分けました。

将来Cartridge Readerを接続するときにも、入口だけを差し替えて同じImport Serviceへ流せる構造にするためです。

---

## 初めて本物の画面が出た

最初の実ゲーム確認には、自分で吸い出してあった **Chrono Trigger** を使いました。

Importを行い、Game DetailからPLAY。

すると、SDL3のWindowの中にChrono Triggerのオープニング画面が表示されました。

古時計の文字盤と、その前を揺れる振り子。

静止画が出ただけではなく、フレームをまたいで振り子が実際に動いている。

つまり、libretro Coreがロードされ、ROMが読み込まれ、`retro_run` が継続的に呼ばれ、Video callbackを通してNOA Systemの画面へ描画されているところまで、本当に一周がつながったことになります。

前回まで緑色のDummy Sessionだった場所に、突然昔のゲームが現れました。

---

## 一発で動いた。でも、それで終わりではなかった

最初の実ゲーム起動そのものは、驚くほどあっさり成功しました。

ただ、その後のレビューではいくつか重要な問題が見つかりました。

ひとつはEmulation速度です。

最初はDisplay Refresh Rateに引っ張られてしまい、環境によってゲームが本来より速く動く状態になっていました。ここはDisplay側ではなく、Coreが申告するFPSを基準にFrame Pacingするよう修正しました。

Audioについても、callbackが呼ばれているだけでは「音が出る」とは言えません。SDL Audioの初期化と失敗の見える化を行い、実際にWindows側のAudio Sessionと実音声まで確認しました。

また、開発用Import元は単なる置き場ではなくInboxとして扱い、Importに成功したファイルは処理済みとして消費する形に変更しました。

さらに、開発中のデータが意図せずWorkspace外へ散らばらないよう、Windowsでの開発Storage配置も見直しました。

最初にゲームが動いた瞬間は派手ですが、そのあとに見つかったこうした問題を直していくことで、単なる動作デモから少しずつ「仕組み」に近づいていきます。

---

## 7つのテストと、実際に目で見る確認

今回の縦切りでは、LibraryやSessionだけでなく、ROM Hash、Import Service、libretro Core、Emulation Smoke Testまで含めて自動テストを追加しました。

最終的に7つのテストがPassし、実ROMがない環境でも検証できる部分と、Coreや実ROMがある場合だけ確認する部分を分けています。

それとは別に、最後は実際にWindowを開いて確認しました。

- Importできる
- Game Detailへ移動する
- PLAYで実ゲームが起動する
- 映像が動く
- 音が出る
- ESCでSessionを終えられる
- 元のGame Detailへ戻る

ここまで通って、Issue #2のVertical Sliceを完了としました。

---

## PLAYの向こう側が、本物になった

まだImport UIは暫定です。

Game Identityも、ROM Databaseも、Controller対応も、Saveもこれからです。

それでも今回、Library → Game → PLAY → 実ゲーム → Exit → Gameという道が初めて最後までつながりました。

NOA Systemにとって、これは「エミュレータが動いた」というより、前回作ったゲーム機の骨格の中へ初めて本物のゲームが入った瞬間だったと思います。

そして次に気になったのは、ゲームが動くことではなく、**遊んだ続きをちゃんと残して戻ってこられるのか**ということでした。

---

## micから

この実装のことはよく覚えてる。

なんか動こうとして止まるとか、エラーでも出て調べるんだろうなって思ってたんだけど、まさか一発起動。

自分で吸い出してあったクロノトリガーを渡して、仮のインポート処理を踏んで、スタート押したらあの古時計の画面出るんだもん。

深夜なのに一人で拭いちゃって、いやーそんな、そんな事ある？って言ってた。

リストも全てダミーだけど、ちょっと本当にできるのかもって思い始めてた

— mic

---

← [前の日記 #1 — エミュレータより先に、ゲーム機の一周を作る](0001-first-vertical-slice.md)

[次の日記 #3 — ゲームが残るなら、遊んだ時間も残したい](0003-keep-the-time-we-played.md) →
