# #7 — ROMが分かると、ゲーム棚になる

前回までで、ROM Databaseを再生成できる土台と、それを支える設計文書が整いました。

次にやりたかったのは、そのDatabaseを実際のLibraryへつなぐことです。

取り込まれたROMのhashを調べて、何のゲームなのかを識別する。

Known ROMなら正式な名前でLibraryへ登録し、Databaseに無いROMでもUnknownとして拒絶せず、そのまま遊べるようにする。

ここまでつながれば、NOA SystemのLibraryは単なるファイル一覧ではなく、少しずつ「自分のゲーム棚」になっていきます。

ところが、Databaseもすでにあるし素直につながるだろうと思っていたこの作業は、実データを当ててみると意外なところで引っかかりました。

---

## GameとROMは、同じものではない

まず整理したのは、Libraryの中で何をIdentityとして扱うかでした。

たとえば同じ作品でも、revision違いやregion違いならROMの内容は異なります。

逆に、まったく同じROMを別のfilenameで取り込んだからといって、別のゲームとして増えてほしくはありません。

そこで、少なくとも次のものを分けて考えます。

```text
Game
  = Library上で選択・起動するrelease / revision / edition単位

ROM / Media
  = 実際のROM imageそのもの

Install
  = Libraryへ保存された実体
```

ROMのSHA-1はMediaを識別するために使います。

Gameそのものをhashで決めるわけではありません。

同一contentならfilenameが違っても重複登録しない。一方、revision違いのようにhashが違うものは別のLibrary Entryとして保持する。

将来、複数releaseを「同じ作品」として棚の上でまとめたくなったら、それはIdentityとは別の表示整理として考えることにしました。

---

## 最初のDatabaseでは、9本がUnknownになった

今回は、手元にある25本のSFC ROMをAcceptance Suiteとして使いました。

標準的なタイトルだけではなく、revision違い、大容量ROM、特殊chip搭載タイトル、自作ROMなどを混ぜています。

最初は、それまで保存・生成してきたMAME Software List由来のDatabaseをそのままROM Identityの照合に使いました。

結果はこうなりました。

```text
Known   : 16
Unknown : 9
Import  : 25 / 25
```

UnknownになったROMを調べると、単にDatabaseにゲームが無いわけではありませんでした。

MAMEのSoftware Listでは、実際のカートリッジ内部にある複数のROM chipを、それぞれ別のROMとして記録しているタイトルがあります。

一方、こちらで扱っている`.sfc`は、それらをひとつにつないだwhole-fileです。

そのため、chip単位のhashとwhole-fileのhashを直接比較しても一致しません。

Databaseの内容が間違っているわけでも、ROMが壊れているわけでもない。

**同じものを、違う粒度で見ていた。**

実データを25本まとめて当ててみたことで、その違いがかなりはっきり見えました。

---

## ROMそのものを見るDatabaseへ

そこで、ROM IdentityのPrimary Sourceを見直しました。

開発用にNo-Intro DAT-o-MATIC由来のSFC Databaseを用意し、同じ25本をwhole-file SHA-1で照合してみます。

結果は、

```text
Known   : 24
Unknown : 1
Import  : 25 / 25
```

でした。

Unknownとして残った1本は、もともとDatabase未登録のケースを見るために入れていた自作ROMです。

つまり今回扱いたい「ユーザーが持っているROM fileそのもの」を識別する用途には、No-Introの情報モデルの方が素直に合っていました。

だからといって、MAMEの資料を捨てるわけではありません。

役割を分けます。

```text
No-Intro
  → whole-file ROM IdentityのPrimary Source

MAME Software List
  → cartridge構成やchip情報などのTechnical Metadata Source
```

ひとつのDatabaseですべてを解決しようとするのではなく、何を知りたいのかに応じてSourceを使い分ける形になりました。

なお、これらのSourceを将来配布物へ含める場合のライセンスや配布条件については、実際の公開形態が決まった段階で改めて確認する必要があります。

---

## Unknownでも、ゲームはゲーム

今回かなり大事にしたのが、Databaseに一致しないROMの扱いです。

```text
DB No Match
≠ Invalid ROM
≠ Import Failure
≠ Launch禁止
```

Databaseに無いHomebrewや同人タイトル、将来まだ登録されていないROMでも、NOA System側が勝手に「無効」と判断してはいけません。

Known ROMならSource由来のcanonical nameを使う。

Unknown ROMなら元filenameをもとに仮の表示名を作る。

どちらもLibraryへ取り込み、Game DetailからPLAYできます。

今回の25本も、Known / Unknownに関係なくすべてImportに成功しました。

Databaseはゲームを遊ぶための許可証ではなく、**そのROMについて何を知っているかを増やすためのもの**として扱います。

---

## 実ゲーム25本を通してみる

Identityだけ確認して終わりにはせず、そのままImport → Library登録 → PLAYまで通しました。

```text
25 ROM
  ↓
Hash
  ↓
DB Lookup
  ↓
Known / Unknown
  ↓
Library Import
  ↓
Game Detail
  ↓
PLAY
```

Importは25本すべて成功。

Boot smoke testは21 / 25が成功しました。

残る4本はDSP-1 / CX4 / SPC7110系などが要求するfirmwareをCoreへまだ供給できていないことが原因で、IdentityやImportとは別の問題だと切り分けられています。

逆にSuper FX、Super FX2、SA-1などを使うタイトルはこの時点でも起動しました。

ひとつのROMだけで確認していると見えなかった違いが、まとまった実データを流すことで一気に出てきます。

このAcceptance Suite自体が、だんだん開発の道具になってきました。

---

## 失敗したImportを、Libraryへ残さない

レビューではもうひとつ、Import中に失敗したときのData Safetyも見直しました。

最初の実装では、ROMの保存が完了する前にGameだけDatabaseへ登録される経路がありました。

その状態でファイル書き込みやDB登録が失敗すると、Mediaを持たない空のGameや、中途半端に保存されたROMだけが残る可能性があります。

そこでImportの順序を整理しました。

```text
ROMを一時ファイルへ保存
 ↓
finalへ確定
 ↓
DB transaction開始
 ↓
Game作成 / 再利用 + Media登録
 ↓
COMMIT
 ↓
Inboxを消費
```

DB登録に失敗した場合はROLLBACKし、確定済みROMも削除して、元のSource ROMはInboxに残します。

「成功したように見える」ことより、失敗したときに元へ戻れることを優先しました。

ゲームやSaveと同じで、Libraryも長く使うなら、こういう失敗側の動作がだんだん重要になってきます。

---

## ファイルの棚から、ゲームの棚へ

これまでもLibraryにはROMを置けました。

でも、そこにあるものが何なのかをNOA System自身が理解していたわけではありません。

今回、ROMのhashからIdentityを照合し、Knownなら正式な名前を付け、revisionの違いも別のものとして扱い、UnknownならUnknownのまま受け入れるところまでつながりました。

「このファイルを起動する」から、

**「このゲームをLibraryから選んで遊ぶ」**

へ、少しだけ意味が変わった気がします。

NOA Systemが自分の手元にあるゲームを理解し始めた回でした。

---

## micから

DBもあるしすんなり行くかなって思ってた課題。
しかし意外とそうでもなく、結果的には照合の仕方が今回の方式と会わなかった。
それで開発用途に No-Introの DBと照合してみたらすんなりいった。
結構色々あるもんだ。

配布時のライセンスについては確認する必要があるのでそれはDocsかなにかに残しておいてもらって、公開する時になったら考える。
（DBにもソースとライセンスの情報がある）

— mic

---

← [前の日記 #6 — 作りながら、設計書も育てる](0006-grow-the-design-docs.md)
