# #9 — ゲームの名前を、ちゃんと書けるようにする

前回で、Game Listの中身は本物のLibraryになりました。

ところが、棚に並ぶGameが本物になったことで、今度は別の仮物が目立ち始めます。

文字です。

開発初期のFrontendでは、大文字の英数字だけを描ける小さなBitmapFontを使っていました。

Vertical Sliceを作るには十分でしたが、実Libraryには小文字も括弧もカンマもあります。

もちろん日本語も使いたい。

そこで今回は、その開発用文字描画を卒業して、UTF-8の文字列を普通に描けるTrueType Fontの基盤へ置き換えます。

---

## 本物のタイトルには、文字が足りない

Dummy Gameなら、表示できる文字だけで名前を付ければ済みます。

実ROMから得たcanonical titleはそうはいきません。

たとえば、

```text
Super Metroid (Japan, USA) (En,Ja)
```

には小文字もスペースも括弧もカンマもあります。

これまでのBitmapFontでは、そもそも表現できない文字が多すぎました。

Gameを正しく識別できても、その名前を画面にちゃんと書けない。

Libraryが本物になったからこそ、文字描画も仮のままではいられなくなりました。

---

## 標準FontにM PLUS 2を使う

標準Fontには **M PLUS 2 Medium** を採用しました。

Light / Medium / BoldのFont Assetは保存していますが、今回実際の描画に使うのはMediumだけです。

FontをRepositoryへ置くなら、fileだけではなく由来も残します。

```text
Font
+ Source
+ License
```

取得元とSIL Open Font License 1.1の情報を記録し、将来「このAssetはどこから来たのか」が分からなくならないようにしました。

ROM DatabaseのSourceを残したときと同じで、使えることだけではなく、**なぜここにあるのかを後から辿れること**も大事にしています。

---

## ViewからFontの事情を追い出す

各画面が直接TrueType Fontを扱い始めると、Font handleやGlyph生成の処理があちこちへ広がります。

そこでFrontend側には薄い `TextRenderer` を置きました。

```text
M PLUS 2 Medium
       ↓
  TextRenderer
       ↓
Game List / Game Detail / Session
```

Viewが知るのは、UTF-8の`std::string`と「どこへ、どの大きさで描くか」だけです。

Glyphの生成やcache、Fontのload/unloadはTextRenderer側へまとめます。

BitmapFontはfallbackとして残さず、通常Frontendから完全に外しました。

これで文字描画の入口がひとつになり、将来Fontを差し替えたりfallbackを追加したくなったときにも、各Viewを書き直さずに済みます。

---

## UTF-8をFrontendの普通の文字列にする

今回からFrontendではUTF-8文字列をそのまま扱います。

ASCIIだけを特別扱いするのではなく、1〜4byteのUTF-8 sequenceをcodepointへdecodeして描画します。

不正なbyte列が来てもCrashせず、安全に読み飛ばすようにしました。

確認用には、

```text
レトロピフリーク
日本語表示テスト
```

のような日本語文字列も使っています。

実Libraryへdummy Gameを追加してテストするのではなく、隔離したSelf Testの中で幅計測と描画を確認しました。

結果として、英数字だけでなく日本語も同じ描画経路で扱えるようになりました。

---

## Game Detailも、少しだけゲームらしくする

文字を普通に描けるようになったので、Game Detailにも今すでに持っている情報を少しだけ出すことにしました。

追加したのは、

```text
SYSTEM
STATUS
SIZE
```

の3つです。

たとえば、

```text
Super Metroid (Japan, USA) (En,Ja)

SYSTEM    SFC
STATUS    KNOWN
SIZE      3.0 MB

> PLAY
```

という程度です。

`STATUS`はDatabaseに一致したMediaなら`KNOWN`、一致していなければ`UNKNOWN`。

`SIZE`は巨大なbyte数をそのまま見せず、KB / MB / GBへ人間向けに整形します。

Mediaが存在しない場合も無理に値を作らず、欠損として安全に表示します。

まだ完成版のGame Detailではありません。

でも、単にTitleとPLAYだけだった画面が、「このGameについてNOA Systemが今知っていること」を少し見せる画面になりました。

---

## 文字が変わるだけで、急に見えるものが増える

通常Frontendを実Libraryで確認すると、違いはかなり分かりやすいものでした。

Game ListはM PLUS 2で自然に読めるようになり、canonical titleに含まれる小文字や記号も欠けません。

Game DetailではSYSTEM / STATUS / SIZEが表示され、Known ROMとUnknown ROMの違いもその場で確認できます。

そしてPLAYの導線はそのまま動いています。

内部ではTextRendererやUTF-8 decodeといった基盤の変更ですが、人間から見ると一番大きいのは単純で、

**ゲームの名前がちゃんと読めるようになった。**

それだけで、開発用画面だったものが急に少し製品らしく見えてきます。

---

## 前回決めたSafety Ruleは、次のIssueでも効いてくる

レビューでは、文字描画そのものとは別にひとつ修正が入りました。

壊れたFontを読むError Pathを確認するテストが、OSの実Temp領域へtest fileを作ってcleanupしていたためです。

前回、Delete機能を作る過程で「破壊的なfilesystem testはbuild tree内の専用sandboxだけで行う」というルールを決めました。

今回のcleanupは小さなものでも、その例外にはしません。

TextRendererのテストも同じTestSandboxへ移し、`remove_all()`が届く範囲をtest自身が作った領域だけに限定しました。

ひとつ前の作業で得た安全ルールが、次の実装レビューでもそのまま機能しています。

こういう積み重ねで、開発環境そのものも少しずつ強くなっていきます。

---

## それでも、前のFontもちょっとかわいい

今回、BitmapFontは役目を終えました。

実Libraryのタイトルを正しく表示するには、もう明らかに足りません。

M PLUS 2へ移行した画面はずっと読みやすく、日本語も使えるようになりました。

ただ、開発初期のあの小さなドット文字には、妙にゲーム機らしい味もありました。

正しい文字描画へ進んだからといって、昔の見た目まで価値がなくなるわけではありません。

いつかUIを本格的に考えるときに、あの雰囲気を別の形で拾うのも面白そうです。

---

## micから

ちゃんとタイトルが出るようになって、明らかにclaudeが作ってくれたBitMapフォントじゃ表示できなくなった。
日本語も使えるようにということで M+ Fontを導入。

結果としては凄く見やすくなって快適なんだけど、前の見た目も結構かわいい。
これはこれで後でまた考えよう。

--- mic

---

← [前の日記 #8 — 嘘だったゲーム棚を、本物にする](0008-the-shelf-stops-lying.md)
