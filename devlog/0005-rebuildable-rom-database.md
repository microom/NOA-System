# #5 — 消しても困らないROM Database

前回は、ROM Databaseの元になる一次資料を固定し、出典やライセンス、SHA-256まで含めて保存しました。

今回は、その保存したSource Snapshotから、実際に検索できるSQLite Databaseを作るところまで進めました。

ただし、ここでもDatabaseそのものを正本にはしません。

狙っているのは、**何度でも同じSourceから作り直せるDatabase**です。

---

## Source SnapshotからSQLiteまでを一本につなぐ

今回作ったpipelineはこうです。

```text
Preserved MAME Source
        ↓
      Parse
        ↓
    Normalize
        ↓
    Validate
        ↓
      SQLite
```

入力は、前回保存したMAME 0.289の`hash/snes.xml`。

ネットワークから何かを取り直すことはせず、Archive済みのSourceだけを使ってofflineで完結します。

生成先は`Generated/ROMDatabase/`。

つまり、生成したSQLiteを消してしまっても、Source Snapshotとbuild toolが残っていればもう一度作れます。

---

## Sourceをそのままコピーしない

MAMEのXMLをそのままSQLiteへ詰め込むのではなく、一度Source由来のrecordへParse / Normalizeする層を作りました。

Software側では、MAMEのsoftware name、cloneof、description、year、publisherなど。

ROM側では、filename、size、CRC32、SHA-1、status、dataareaなどを保持します。

ここで重要なのは、これらをNOA Systemの正式なGame Identityとして扱っていないことです。

まだこれはあくまで、**MAMEから得たSource metadata**です。

将来のGame / ROM / Media Identity設計と、外部Sourceの情報をこの段階で混ぜないようにしています。

---

## 3710本のSoftwareと4292個のROM record

実際にMAME 0.289のSFC Software Listからbuildした結果は、

```text
source_software : 3710 rows
source_rom      : 4292 rows
```

でした。

F-Zero (Japan) と Chrono Trigger (Japan) もDatabaseから検索でき、それぞれROM hash candidateを持っていることを確認しています。

SHA-1とCRC32にはlookup用indexも作りました。

これで次の段階では、実際に吸い出したROMのhashとSource由来recordを照合する準備が整ったことになります。

---

## 同じ材料なら、同じ意味のDatabaseになる

今回かなり重視したのがdeterministic buildです。

SQLiteファイルそのもののbyte列が完全一致することまでは要求していません。

build時刻のような非決定情報は存在するからです。

その代わり、同じSource Snapshotから作った場合に、

- software / ROMの件数
- normalized value
- provenance
- schema version
- query結果

が同じになることを確認しました。

実Sourceでも、独立して2回buildし、`built_at`を除いた主要tableの内容が一致しています。

Databaseを「出来上がったファイル」ではなく「手順の結果」として扱うための確認です。

---

## ReviewでData Safetyをもう一段固くする

最初の実装は動いていましたが、レビューで3点修正しました。

ひとつは、missing valueと明示的なempty stringの扱い。

もうひとつはmalformedなhashをどう扱うか。

そして一番重要だったのが、Database更新の順番です。

最初は一時DBを作ったあと、先に本番Databaseへ置き換え、その後validationしていました。

これでは、新しいDatabaseが壊れていた場合に正常な既存Databaseを先に失ってしまいます。

そこで最終的には、

```text
.tmpへbuild
    ↓
fsync
    ↓
.tmpをvalidate
    ↓
成功した場合だけatomic replace
```

という順序に変更しました。

validationに失敗した場合は既存Databaseを残し、一時ファイルだけを捨てます。

malformed hashを含むfixtureも追加し、「壊れたSourceからは壊れたDatabaseを確定しない」ことまでtestで固定しました。

---

## 25個のPython testと、実Sourceでのvalidation

最終的にpipeline側では25件のunit testがPassしました。

実際のMAME 0.289 Sourceを使ったbuildでも、3710 Software / 4292 ROMを生成し、hash format、orphan record、provenance、F-Zero / Chrono Triggerの存在まで自動検証しています。

既存のC++側12 testsにもregressionはありませんでした。

前回はSource自体が正しく保存されていることを検証しました。

今回はさらに、そのSourceを食べるpipelineも、正常系だけでなく壊れた入力や失敗時の挙動まで含めて固定し始めています。

---

## 消しても困らないDatabase

Databaseというと、つい大事なデータの塊に見えます。

でもNOA Systemでは、生成したSQLiteはむしろ「消しても困らない」状態にしておきたい。

大事なのは、

```text
どのSourceを使ったか
どう解釈したか
どう正規化したか
どう検証したか
```

が残っていることです。

それさえ残っていれば、Databaseはまた作れる。

この段階でようやく、ROMを吸い出したあとに「これは何のROMなのか」を機械的に照合していくための足場ができました。

まだ実ROMとのlookupはつないでいません。

でも、Sourceを残すところから始めたことで、この先の照合処理も「なんとなくそれっぽいDatabaseを使う」のではなく、どこから来た情報なのかを追いかけられる形で作れそうです。

---

## micから

引き続きDBまわり。

この辺りは昔触ってたけど概念くらいしか覚えてないからおまかせ。

吸い出しの準備が一旦できたかなと喜んでいた頃。

— mic

---

← [前の日記 #4 — データベースより先に、その故郷を保存する](0004-preserve-the-source-before-the-database.md)

[次の日記 #6 — 作りながら、設計書も育てる](0006-grow-the-design-docs.md) →
