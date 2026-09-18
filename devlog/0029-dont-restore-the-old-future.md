# #29 — 古い続きを、勝手に戻さない

前の日記では、SaveやAutoSnapの検証をしやすくするためにDeveloper Debug Menuを作りました。

AutoSnap Creationを止める。

Auto Resumeだけ止める。

必要ならAutoSnapを削除する。

それだけで、Battery Saveの確認はかなり楽になりました。

でも、その作業を繰り返しているうちに、もう一段だけ根本的な問題が見えてきました。

**そもそも、Persistent Saveが変わったのに古いAutoSnapを自動で読み込んでいいのか。**

今回は、その問題を直した話です。

---

## AutoSnapは「その時のSave」と一緒に成立している

AutoSnapは、単なる画面の記録ではありません。

その時点のゲーム内部状態を丸ごと保存します。

だから、そのSnapshotを作ったときには、Persistent Saveもある状態を前提にしています。

例えば、

```text
AutoSnap A
  └─ Persistent Save S1
```

という組み合わせがあったとします。

ここで後から、Library側のPersistent SaveだけがS2へ変わったとします。

原因はいろいろ考えられます。

- 実カートリッジからSaveを取り直した
- backupをrestoreした
- 別環境からSaveをimportした
- 手動でSave fileを差し替えた

この状態で次にPLAYすると、起動時にはまずS2がCoreへ渡されます。

でも、そのあとAutoSnap Aを自動Loadすると、Snapshot内部に残っていた古い状態S1相当へ戻る可能性があります。

さらにそのまま終了すると、古い状態が新しいPersistent Saveへ書き戻されるかもしれません。

つまり、

```text
新しいSaveを入れる
      ↓
古いAutoSnapを自動Load
      ↓
古い状態へ戻る
      ↓
終了時に古いSaveを再保存
```

という、かなり嫌なことが起こり得ます。

AutoSnapは続きを守るための機能なのに、状況によっては**新しい続きを古い続きで上書きする**ことになります。

---

## 更新日時ではなく、中身を見る

最初に考えやすいのは、Save fileの更新日時を見る方法です。

でも、それでは足りません。

file copyでtimestampが保持されることもあります。

restore方法によっては、内容が変わってもmtimeだけでは意味が分からない。

逆にtimestampだけ変わって内容は同じ、ということもあります。

なので、AutoSnap作成時点のPersistent Saveについて、

```text
Save exists?
Size
SHA-1
```

をidentityとして記録することにしました。

起動時には現在のPersistent Saveから同じidentityを計算し、AutoSnap metadataに残っているものと比較します。

```text
AutoSnap metadata
  Persistent Save Identity
      ↓
current Persistent Save Identity
      ↓
一致？
  ├─ YES → Auto Resumeしてよい
  └─ NO  → Auto Resumeしない
```

中身が同じなら従来どおり。

違うなら、古いSnapshotは自動では使いません。

---

## 不一致でも、AutoSnapは消さない

ここで大事なのは、AutoSnap自体を削除しないことです。

Persistent Saveが変わったからといって、古いSnapshotが壊れているわけではありません。

ただ、**今のSaveとの組み合わせでは自動Resumeに使うべきではない**というだけです。

なので不一致時は、

```text
Auto Resumeをskip
      ↓
current Persistent Saveで通常起動
      ↓
AutoSnap自体はそのまま残す
```

という動作にしました。

Manual Save Stateの明示Loadも別扱いです。

今回止めたいのは、ユーザーが何も指定していない起動時に古いSnapshotが勝手に優先されることです。

明示的に「このStateをLoadする」と操作した場合まで、自動で拒否する話にはしませんでした。

Auto ResumeとManual Loadは、似ているようで意味が違います。

---

## Saveが無いこともidentityにする

Save fileが無いゲームもあります。

なので、

```text
Saveなし
```

も単なる例外ではなく、一つの状態として扱います。

Snapshot作成時にSaveが無く、現在も無い。

これは一致です。

Snapshot作成時には無かったのに、今はSaveがある。

これは不一致です。

逆も同じです。

```text
Snapshot時   Current
----------------------
None         None     → Match
None         Save     → Mismatch
Save         None     → Mismatch
Save A       Save A   → Match
Save A       Save B   → Mismatch
```

こうしておくと、Systemごとの例外処理を増やさず、同じルールで判定できます。

---

## 古いAutoSnapは、一度だけ安全側へ倒す

もう一つ問題がありました。

この機能を追加する前に作られたAutoSnapには、Persistent Save identityが入っていません。

現在のSaveのhashは計算できます。

でも、古いAutoSnapを作った当時のSaveが何だったかは、後からは分かりません。

証明できないものを「たぶん一致」と扱うのは、この機能の目的と逆になります。

なので旧metadataは、

**Legacy / Unknown**

として扱うことにしました。

```text
旧AutoSnap
Persistent Save Identityなし
      ↓
Auto Resumeをskip
      ↓
current Saveで通常起動
      ↓
正常終了
      ↓
新しいAutoSnapを生成
      ↓
今度はIdentity付き
```

古いAutoSnapを削除する必要はありません。

一度だけ自動Resumeに使わず、現在のSaveで通常起動して新しいSnapshotを作れば、そこで自然に新形式へ移行できます。

大げさなmigration処理を用意せず、安全側へ倒しながら自然に更新する形です。

---

## 「元のSaveへ戻したらResumeできる」ではない

実装後のReviewで、一つ説明の間違いも見つかりました。

最初は、

「Saveを元の内容へ戻せば、元のAutoSnapとまた一致してResumeできる」

ような説明を書いていました。

でも実際のルールはそうではありません。

比較する相手は、**常に最新AutoSnapが記録しているSave identity**です。

例えば、

```text
AutoSnap A <-> S1

SaveをS2へ変更
  → AとはMismatch
  → Auto Resumeをskip

そのまま終了
  → AutoSnap B <-> S2 を作る

SaveをS1へ戻す
  → 最新AutoSnap BとはMismatch
  → またskip
```

となります。

「昔のどれかと一致するか」ではなく、

**今使おうとしている最新AutoSnapが、現在のSaveを前提にしているか。**

それだけを見ます。

コードの不具合ではなく説明文の問題でしたが、こういうところを曖昧にすると後から仕様そのものが誤解されます。

Reviewで止められて良かった部分でした。

---

## SFCでもMega Driveでも同じルールで動く

この仕組みはSystem固有にはしていません。

SFCだからこう。

Mega Driveだからこう。

という分岐ではなく、Persistent Saveを読み込んだ後の共通byte列に対してidentityを計算します。

実機確認では、SFCとMega Driveの両方でSave内容を差し替えながら確認しました。

結果は、

- Saveが変わっていない → 従来どおりAuto Resume
- Saveが変わった → Auto Resumeをskip
- current Saveから通常起動
- 古いSnapshot由来のSaveへ巻き戻らない

という期待通りの動作になりました。

Debug Menuで毎回Auto ResumeをOFFにする必要も減りました。

前回は「テストを楽にするための道具」を作りましたが、今回は**人間が切り替えなくても、NOA自身が危ない組み合わせを避ける**ようになったことになります。

---

## 便利な自動機能ほど、いつ使わないかを決める

AutoSnapは便利です。

Saveも便利です。

自動Resumeも便利です。

でも、自動化された機能が増えるほど、

「いつ動くか」

だけでは足りなくなります。

**いつ動かないべきか。**

これも同じくらい重要になります。

Persistent Saveが更新されたら、古いAutoSnapを勝手に使わない。

分からないLegacy Snapshotなら、一度安全側へ止まる。

明示操作のManual Loadまでは奪わない。

便利さを保ちながら、勝手にやりすぎない。

NOA Systemでは、こういう境界を少しずつ増やしています。

続きを残すための仕組みだからこそ、

**新しくできた続きを、古い続きで消さない。**

今回は、そのための小さな安全装置を追加しました。

---

## micから

この機能が入ったおかげでSRAM系のテストがめっちゃ楽になった！

嬉しい！

--- mic

---

← [前の日記 #28 — 作るための道具も、NOAの中へ](0028-tools-for-building.md)
