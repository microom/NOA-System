# #14 — ゲーム機に、メニューができた

NOA SystemのFrontendに、ようやくトップレベルのメニューが入りました。

これまでLibraryからゲームを選び、Game Detailへ進み、PLAYしてSessionへ入るところまではかなり整ってきました。

でも、NOA System全体の設定やImport、将来のGame Environmentへ入るための「入口」はまだありませんでした。

今回はそこへ、画面左から開く **NOA Menu** を追加しました。

```text
NOA Menu
├─ LIBRARY
├─ CARTRIDGE / IMPORT
├─ SETTINGS
└─ ABOUT NOA-SYSTEM
```

controllerではSELECT、mouseではhamburger、keyboardでは開発確認用の導線も用意しています。

見た目はまだ仮です。

でも、これでNOA Systemに「ゲームを選ぶ画面」だけではなく、**システム全体へ触るための場所**ができました。

---

## LibraryとSettingsを同じ階層にしない

最初に決めたのは、メニューから開くものを全部同じView Stackへ積まないことでした。

LibraryやGame Detail、Cartridge / Importは、ユーザーが「場所を移動する」画面です。

一方でSettingsやGame Environmentは、いま見ているLibrary等を捨てて別の場所へ移動するというより、**その場でNOA System本体を設定するためのUI**です。

そこで、

```text
Primary View
    Library / Game Detail / Cartridge

System Utility
    Settings / Game Environment / About
```

として責務を分けました。

Settings側はPrimary Viewを裏に残したままOverlayとして開き、閉じれば元の画面へ戻ります。

今のSettingsはまだplaceholderに近い状態ですが、次に作るCore周りの管理機能をここへ接続できるようになっています。

---

## 実際に触ると、小さな違和感がすぐ見つかる

最初の実装ができたあと、controllerとkeyboardで実際に触ってみると、いくつか調整点が出ました。

たとえばNOA Menuで`LIBRARY`を決定したとき。

すでにLibrary rootにいる場合、画面遷移そのものは発生しません。

そのため決定に使ったbutton入力が次のLibrary側にも残り、意図せずそのままGame Detailへ入ってしまいました。

これはOverlayを閉じるタイミングでNavigation stateを再同期するようにして解消しました。

ほかにも、

- menu slideの速度を上げる
- `SYSTEM / ABOUT`を`ABOUT NOA-SYSTEM`へ整理する
- Library rootではESCからもmenuを開けるようにする
- Enterでも項目を決定できるようにする

といった調整を入れました。

Enter対応もNOA Menuだけの特別処理にはせず、Frontend Navigation上の`Activate`として共通化しています。

こういう部分は仕様書だけ眺めていても分かりにくく、**一度触れるものを作ってから直す**方が早いです。

---

## 久しぶりに、クラッシュした

今回、一番大きかったのはInGameMenuから`EXIT GAME`を選んだときに発生したクラッシュでした。

久しぶりにアプリがそのまま落ちたので、かなり嫌な感じのする現象です。

minidumpを解析すると、原因はゲームCoreそのものではなくFrontendのView lifetimeにありました。

Sessionの`Render()`中にExit処理が走ると、そのSession View自身がView Stackから外れて破棄されることがあります。

ところが呼び出し元のFrontend側では、`Render()`を呼ぶ前に取得したraw View pointerを、その後もそのまま使っていました。

```text
Current Viewを取得
    ↓
View::Render()
    ↓
Render内でPopView()
    ↓
元のViewは破棄される
    ↓
古いpointerを再利用
    ↓
use-after-free
```

クラッシュダンプではaccess violationとNULLへのjumpが確認でき、呼び出し位置もこの流れと一致しました。

修正は単純で、Navigation Stackを変更する可能性がある処理の後では、`CurrentView()`を取り直します。

もともと別の処理では同じ安全策を入れていたのですが、今回新しく追加したMenu表示判定の直前だけ抜けていました。

これをきっかけに、Frontendでは次のルールを明示的に残しました。

> Navigation Stackを変更し得るView callの後で、それ以前に取得したraw View pointerを再利用しない。

局所的にクラッシュだけ直すのではなく、次に同じ種類のバグを作らないためのルールまで残します。

---

## ESCは「閉じる」と「終了する」の両方を持っていた

同時に、ESC入力にも別の問題がありました。

InGameMenuではESCをBackとして使います。

一方、通常のSession中ではESCはゲーム終了のshortcutとしても残っていました。

そのためMenuをESCで閉じた直後、keyboardのrepeat入力が残っていると、次のESC eventがSession Exitとして拾われる可能性がありました。

Overlay側にはもともと「閉じるために使ったbuttonがreleaseされるまで待つ」仕組みがあります。

そこで直接ESC Exitする側も同じrelease gateを見るようにしました。

結果として、

```text
InGameMenu + ESC
    → Menuだけ閉じる

Menu closed + ESC
    → Sessionを終了する
```

が安定して分離できました。

---

## 次は、Game Environment

NOA Menu自体はまだ最終デザインではありません。

hamburgerの見せ方、menu幅、animation、Settings画面の情報設計など、見た目はあとでいくらでも変えられます。

ただし、今回欲しかったのは「見た目の完成」ではなく、**FrontendからNOA System全体の機能へ入れる構造**でした。

その入口ができたので、次はCore周りのセットアップと検証をまとめるGame Environmentへ進みます。

Coreを手作業で配置したり、環境差を気にしながら毎回確認したりする部分をNOA System自身が管理できるようになると、開発中のチェックもかなり楽になります。

そしてその仕組みは、そのまま将来の配布・初期セットアップにもつながります。

Frontendに小さなmenuが付いただけですが、プロジェクト全体としては次の段階へ入るための入口になりました。

---

## micから

遂にFrontEnd側にもメニューが追加された。
とりあえずの実装だけどやりたいことは出来るので見た目は後で考える。
次はCore周りのセッティング。
これが完成すると今後のチェックも一層楽になるし、最終的なNOAのリリース準備にもぐっと近づくね。

PS. 
今回、久しぶりにクラッシュが起きてドキッとしたけどちゃんと理解の範疇で無事収まって良かった。
AI 駆動開発は如何に人が理解の範疇でコントロールできるかが大事だと思うので、この辺りも高いラインを維持していきたい。

--- mic

---

← [前の日記 #13 — ROMだけでは、ゲームは動かない](0013-rom-is-not-enough.md)
