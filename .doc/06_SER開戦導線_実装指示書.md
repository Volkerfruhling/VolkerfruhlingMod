# VF β実装指示書：セルビア幕間枝と世界大戦の発火

> **この文書の位置づけ**
> 開発リポジトリ（Mod本体）で作業するClaude Codeセッションへ渡す実装指示書。
> 設定資料リポジトリ（docs）にアクセスできない前提で、必要な文脈をすべてこの1ファイルに閉じ込めてある。
> 作成 2026-08-26。ソース: planning/01〜04、input/33_SER_NF.txt、input/34_SER_event.txt、input/35_vf_focus_SER.png、prehistory/nations/SER.md、prehistory/ENTITIES.md

---

## 0. 実行者への注意

- **Phase 0 → 1 → 2 → 3 の順に進めること。** Phase 0 は事前監査と既存の不具合修正で、これを飛ばすと以降の動作確認が成立しない。
- **最初に §4-0-0（陣営の実在監査）と §4-0-0b（処理の所在監査）を実行し、§13・§14 の表を埋めること。** この指示書の全体が「宣戦が同盟連鎖で世界大戦へ拡大する」ことに依存しており、陣営が実在しなければ何を作っても大戦は起きない。
- **§10「要裁定」の項目は実装してはならない。** 主宰（リポジトリオーナー）の判断待ち。該当箇所に当たったら手を止めて確認を求めること。
- ファイルパスはHOI4 Modの標準構成を想定して書いている。**実際のパスは着手前に必ず実リポジトリで確認すること。**
  想定: `common/national_focus/vf_focus_SER.txt` / `events/vf_SER_events.txt` / `localisation/japanese/*_l_japanese.yml`
- 迷った箇所は勝手に決めず、`# TODO(VF):` コメントを残して報告すること。

---

## 1. 世界観の最小前提

Mod名 **Völkerfrühling**（独語「諸国民の春」）。HOI4の架空史Mod。**ゲーム開始日 1925年3月**。

- 分岐点は1825年のデカブリストの乱の長期内乱化。ロシアが弱体化し、1848年の諸国民の春が各地で成功した世界。
- **第一次世界大戦は起きていない**（「凍りついた平和」）。代わりにバルカンで局地戦争が繰り返された。
- 陣営構造: **英独同盟**（GER + ENG、衛星国 LIT・CRO・BOH等）対 **露仏協商**（RUS + FRA）。その間で **ITA** が二重外交。
- ドイツ帝国(GER)は皇帝(プロイセン王ヴィルヘルム2世)と摂政(ハプスブルク家カール1世)の**二元君主制**。首都フランクフルト。
- **BOH（ボヘミア王国）と CRO（クロアチア王国）は GER の自治領邦**。ハプスブルク家の下にある半自治王国で、独立国ではない。

### セルビア国 (SER) の立場

1914-15年の「セルビア懲罰戦争」で独・墺・伊・洪・克に敗北。**ウィーン条約**でマケドニア→BUL、コソボ→ALB、スレム西部等→CRO を割譲し、巨額の賠償金と軍備制限を課された。1919年に王政廃止、1921年のクーデタで **ディミトリエ・リョティッチの「ズボル独裁」体制**（正教的コーポラティズム＋失地回復主義）が成立。

包囲同盟（HUN・CRO・ALB・BUL）に囲まれて孤立しているが、**ロシアの後援**を頼みに復讐戦争を志向する。

**この世界で世界大戦の引き金を引くのはセルビアである。** 1929年夏、SERが最後の失地（スレム・マチュヴァ＝帝冠領クロアチア領）を要求してサラエボ型の突発事件が起き、約5週間のエスカレーションを経て 1929年秋に **GER + ENG vs FRA + RUS + SER** の世界大戦が始まる。これが正史ラインである。

### 関連TAG

| TAG | 国名 | 立場 |
|---|---|---|
| SER | セルビア国 | 本書の主役。ズボル独裁、露の後援 |
| BUL | ブルガリア王国 | 包囲同盟。マケドニア領有 |
| HUN | ハンガリー王国 | 包囲同盟。ベルナドッテ朝 |
| ALB | アルバニア公国 | 包囲同盟。コソボ領有 |
| CRO | クロアチア王国 | **GERの自治領邦**。スレム西部領有。危機の舞台 |
| BOH | ボヘミア王国 | **GERの自治領邦**。首都プラハ |
| GRE | ギリシャ王国 | バルカン戦争でSER側（救国同盟） |
| ROM | ルーマニア王国 | バルカン戦争でSER側（救国同盟） |
| MNT | モンテネグロ王国 | SERが1926年に統合する |
| GER / ENG | ドイツ・英国 | 英独同盟 |
| RUS / FRA | ロシア・フランス | 露仏協商。SERの後援者 |
| ITA | イタリア連邦国 | 二重外交。対セルビア遺恨あり |

---

## 2. 現状（実装済みの範囲）

SERは**ゲーム開始から1928年春のバルカン戦争講和まで**が一本通っている。以降が未実装。

### NF（`input/33_SER_NF.txt` 相当、focus_tree id = `focus_SER`）

3系統・約53NF。ID接頭辞は `focus_SER_pol_` / `focus_SER_mil_` / `focus_SER_eco_` で統一済み。

- **政治**: リョティッチの演説 → ZBORの規律／モンテネグロへの圧力／国民精神再興運動 → 最終提案 → モンテネグロ統合・失われたコソボ → ティラナへの最後通牒 → アルバニア平定作戦／バルカン外交の再開 → ギリシャ・ルーマニアへの使節 → 救国同盟 → バルカン協商への対抗 → **復讐の日**
- **軍事**: 国軍再編成 → ZBOR戦闘団／山岳地帯への適応／新式歩兵装備の研究／参謀本部の刷新 → 特殊部隊創設 ほか計11NF
- **経済**: 戦後復興の継続 → 賠償金問題への対処 → 3ルート排他（支払い継続への意思／再交渉へのテーブル／鉄の意志）→ 各末端

**終端NF `focus_SER_pol_day_of_revenge`（復讐の日）** が `will_lead_to_war_with = BUL / HUN` を持ち、`completion_reward` で `event_SER_pol.8` を発火する。正史では1927年3月頃。

### イベント（`input/34_SER_event.txt` 相当、namespace `event_SER_pol`）

| ID | 内容 |
|---|---|
| .1〜.7 | モンテネグロ圧力〜アルバニア平定までのフレーバー・処理 |
| **.8** | **復讐の日**。`vf_started_balkan_war` を立て、BULへ宣戦、SER陣営を参戦させ、`idea_balkan_war` を180日付与。BUL/SER/HUN/ROM に暫定師団 "Militiaaaa" を生成し、HUNへ30日後の `event_HUN_pol.1` を予約 |
| **.9** | **戦争からの撤退**。HUNが州82/83/84/764のうち2つ以上を失うと発火。HUN離脱・単独講和、82/83/84→ROM、764→SER。加えてBUL降伏済みなら BUL とも講和し 803/106→SER、77→ROM |
| **.10** | **講和**。`vf_ended_balkan_war` を立て、BULの `surrender_progress` に応じて4段階で領土を処理（>0.7: 803/106→SER, 77→ROM, 184→GRE ／ >0.5: 803/106→SER ／ >0.3: 803→SER ／ それ以下: 白紙和平） |

### 設計資料 `35_vf_focus_SER.png` との差分

図には存在するが実装にない、または逆のもの。**§10の要裁定事項**。

- 図の終端「**アルバニアからの略奪**」が未実装。経済ツリーの `focus_SER_eco_path_to_plunder`（略奪への道）が現状**行き止まり**になっている
- 図の「**失地回復の準備 → 開戦**」に対し、実装は「バルカン協商への対抗 → **復讐の日**」の2段。図に「復讐の日」というNFは登場しない
- 図の「**アルバニアの脅威認識**」は実装側でコメントアウトされている（`## アルバニアツリー ##` 直下）

---

## 3. スコープ

### やること

| Phase | 内容 | 規模の目安 |
|---|---|---|
| 0 | 陣営・処理所在の事前監査 ＋ 既存イベントの不具合修正 | 中 |
| 1 | BOH・CROの自治領邦タグ整備 | 中 |
| 2 | SER幕間枝 NF 14本（1928春〜1929夏） | 中 |
| 3 | クロアチア危機 → 世界大戦の発火連鎖 | 中 |

### やらないこと（このタスクの範囲外）

- GERのコンテンツ全般（パワーバランス、議会ルート、軍事・産業・戦時ツリー）
- 幕間の危機イベント3件（ローマ進軍1925 / ポーランド・リトアニア危機1927 / オスマン危機1929）
  → **ただし Phase 3 はこれらが立てるフラグを読む形で書くこと**（§8参照）。本体は後日実装
- FRA / RUS / ENG のミニツリー
- アイコン制作（`GFX_goal_unknown` のままでよい）
- 大戦の詳細な講和処理（βは「ゲームが終われる」だけでよい）

---

## 4. Phase 0：事前監査と既存の不具合修正

**新規NFを1本も書く前に、ここを全部潰すこと。** 以下はいずれもテスト走行を汚染する。

### 0-0. 陣営の実在監査【最初にやること】

**この指示書の全体が「SERがCROへ宣戦 → GERが自動参戦 → ENGが同盟で参戦 → 露仏がSER側で参戦」という連鎖に依存している。この連鎖は陣営(faction)と属国関係が実際に定義されていて初めて動く。**

1925年3月1日時点で以下が実在するかをゲーム内の外交画面と `history/countries/*.txt` の両方で確認し、**§13の表に記入すること**。

確認項目:

- 各陣営が `create_faction` / `add_to_faction` で開始時に組まれているか、それとも未実装か
- 陣営のキー名（`add_to_faction` に渡す文字列）とローカライズの有無
- 盟主が誰か
- **HOI4は1国1陣営しか所属できない。** 二重所属を要求している設定が無いか

#### 先に解く必要がある設計上の衝突（3件）

**衝突1: ITAの二重外交**
設定上、ITAは仏伊協商（FRA）と中央保障条約（GER・BOH・CRO）の両方に属する。**HOI4では両方をfactionにできない。**
→ 一方だけをfactionにし、他方は `give_guarantee`・関係値・専用ideaで表現する。
**推奨**: 中央保障条約はfaction化せず、英独同盟＋GERの属国（BOH/CRO）＋保障で表現し、**ITAは無所属（天秤）で開始**する。これなら1929年にどちらへも転べる。

**衝突2: SERが陣営を二重に必要とする**
既存NF `focus_SER_pol_alliance_for_salvation`（救国同盟）で、SERはGRE・ROMを率いる**陣営の盟主になる**。ところがPhase 2で露仏に接近するため、そのままでは露仏協商に加入できない。以下から選ぶこと（§10-3の裁定と連動）。

- (a) 露仏がSERの陣営（救国同盟）へ加入する
- (b) **SERは救国同盟の盟主のまま共同交戦国とし、`vf_greatwar.6` で `add_to_war` により露仏を参戦させる ← 推奨**
- (c) 救国同盟を解散して露仏協商へ加入（GRE・ROMとの関係が失われるため非推奨）

**衝突3: BULとHUNが同一陣営でないとバルカン戦争が成立しない**
`event_SER_pol.8` は**BULにのみ宣戦**しており、HUNは陣営連鎖で参戦する前提で書かれている（`.9` がHUNの離脱処理を持つことがその証拠）。**対セルビア包囲同盟（HUN・CRO・ALB・BUL）がfactionとして実在し、BULとHUNが同一陣営でなければ、HUNは参戦せず `.9` は永久に発火しない。**

なお包囲同盟にはCROが含まれる。CROがGERの属国かつ包囲同盟の一員だと、**1927年のバルカン戦争の時点でGERが巻き込まれて大戦が2年早まる恐れがある**。CROを包囲同盟から外すか、`.8` の宣戦対象・参戦条件でCROを除外すること。**この点は必ず実機で確認し、結果を報告すること。**

#### `.8` のSER側参戦ロジックの脆弱性【要修正】

`event_SER_pol.8` はSER側の参戦国を `is_in_faction_with = SER` で集めている。つまり**救国同盟NFを取らずに「復讐の日」を取ると、SERは単独でBUL・HUNと戦うことになる。**

以下のどちらかで塞ぐこと。**前者を推奨**。

- `focus_SER_pol_day_of_revenge` の `available` に `focus_SER_pol_alliance_for_salvation` の完了を要求する
- `.8` に「陣営が無い場合はGRE・ROMへ参戦要請イベントを送る」フォールバックを入れる

### 0-0b. 処理の所在監査【NF・イベント以外に分散していないか】

この指示書はNFとイベントを前提に書いてあるが、**実際の挙動はそれ以外のファイルに分散している可能性がある。** 見落とすと「NFを直したのに挙動が変わらない」「原因不明で大戦が起きない」に直結する。

以下を全部確認し、**§14の「処理の所在マップ」に記入すること**。

| 場所 | 見るもの |
|---|---|
| `common/on_actions/` | `on_startup` / `on_war` / `on_capitulation` / `on_annex` 等からイベントを起動していないか |
| `common/scripted_effects/` `common/scripted_triggers/` | SER・大戦関連の共通処理が切り出されていないか |
| `common/decisions/` `common/decisions/categories/` | NFの代わりにdecisionで動いている処理 |
| `common/ideas/` | `idea_balkan_war` の実体、ウィーン条約の軍備制限idea、国民精神 |
| `common/national_focus/` | `focus_SER` 以外のツリーが `vf_` フラグを読み書きしていないか |
| `history/countries/` | **開始時の陣営・属国・関係・請求権・保障**（0-0の主戦場） |
| `history/states/` | 州 803 / 106 / 77 / 764 / 82〜84 / 184 の初期所有国 |
| `common/autonomous_states/` | 自治領邦（Phase 1）。既存の自治レベル定義との衝突 |
| `common/ai_strategy/` `common/ai_focuses/` | **AIがNFを取る順序。T1・T2の再現性に直結する** |
| `common/country_leader/` `common/characters/` | 体制変更やNFが差し替える人物 |
| `events/` | 他国のイベントが `vf_` フラグを読んでいないか |

**grepすべきキーワード**: `vf_` / `focus_SER` / `event_SER_pol` / `SER` / `BUL` / `HUN` / `CRO` / `BOH` / `balkan` / `faction`

**発見した分散処理は、消したり移動したりせずそのまま記録すること。** 統合の判断は主宰に諮る。

### 0-1. `event_SER_pol.10` に国指定がない【要修正】

現状のtriggerは国を限定していない。

```
trigger = {
    BUL = {
        has_global_flag = vf_started_balkan_war
        NOT = { has_global_flag = vf_ended_balkan_war }
        OR = { and = { surrender_progress > 0  date > 1928.4.1 } }
    }
}
```

`BUL = { ... }` はスコープ変更なので、この条件は**全ての国について同時に真になる**。`fire_only_once = yes` があるため、実際にはたまたま最初に評価されたAI国のスコープで1回だけ発火し、**プレイヤーは講和イベントを見られない可能性が高い**。`immediate` の効果はグローバルなので領土処理自体は走るが、演出上も検証上も破綻している。

同じファイルの `.9` には `tag = HUN` のガードがあるので、これは書き忘れと判断してよい。

**修正**: triggerの先頭に `tag = SER` を追加し、グローバルフラグの判定はスコープ外へ出す。

```
trigger = {
    tag = SER
    has_global_flag = vf_started_balkan_war
    NOT = { has_global_flag = vf_ended_balkan_war }
    ...
}
```

### 0-2. 講和の日付ロック `date > 1928.4.1`【要修正】

固定日付のため、プレイヤーが1926年に早期開戦すると**戦争が2年以上人為的に引き延ばされる**。以後の幕間枝・大戦連鎖のテストが全部これに引きずられる。

**修正方針**: 開戦からの経過日数で判定する。変数を使わず、遅延イベントで実現するのが確実。

1. `event_SER_pol.8` の option に、自国宛の遅延イベント予約を追加する

```
SER = { country_event = { id = event_SER_pol.11  days = 330 } }
```

2. 新規 `event_SER_pol.11`（hidden、`is_triggered_only = yes`、`fire_only_once = yes`）を作り、
   `immediate` で `set_global_flag = vf_balkan_war_min_duration_passed` を立てる

3. `.10` のtriggerを差し替える

```
trigger = {
    tag = SER
    has_global_flag = vf_started_balkan_war
    NOT = { has_global_flag = vf_ended_balkan_war }
    OR = {
        AND = {
            has_global_flag = vf_balkan_war_min_duration_passed
            BUL = { surrender_progress > 0 }
        }
        BUL = { has_capitulated = yes }
    }
}
```

330日は正史（1927年3月開戦 → 1928年4月講和 ≒ 13ヶ月）に対する下限として置いた。BULが早期に完全降伏した場合は日数を待たずに講和できる。

### 0-3. `.9` 経由で `vf_ended_balkan_war` が立たない経路がある【要検証・おそらく要修正】

`.9`（HUN離脱）の後段は「BULが降伏済みならBULとも白紙和平して領土を移す」処理を持つが、**`vf_ended_balkan_war` を立てていない**。この経路を通ると：

- 白紙和平によって戦争が終わり、BULの `surrender_progress` は0に戻る
- `.10` のtriggerは `surrender_progress > 0`（または `has_capitulated`）を要求するので、以後**永久に真にならない可能性が高い**
- 結果、`vf_ended_balkan_war` が立たないまま戦争だけ終わり、**Phase 2 の幕間枝が出現しない**

まず実機で再現を確認すること。再現するなら、`.9` のBUL降伏分岐でも `set_global_flag = vf_ended_balkan_war` を立てるか、戦争終結処理を `.10` に一本化する（`.9` はHUN離脱のみを扱い、BUL処理は `.10` に委ねる）。**後者を推奨**。

### 0-4. `.9` と `.10` の領土処理の重複【要検証】

州803・106・77 が `.9` と `.10` の両方で移譲される。`.9` 側は `add_core_of` を伴わず、`.10` 側は伴う。0-3の修正で両方が走る経路が生まれる場合、**コアの付与状態が実行順に依存する**。0-3で `.10` 一本化を選べば同時に解消する。

### 0-5. `event_HUN_pol.1` が未執筆【要修正】

`.8` から `days = 30` で予約されているが実体がない。1回の標準走行で必ず踏むため、ここで落ちるとテストが成立しない。

**内容**: バルカン戦争に巻き込まれたハンガリーの世論・宮廷の動揺を描くフレーバー。選択肢は最低1つ、効果は軽微（安定度・戦争協力度の小変動程度）でよい。`is_triggered_only = yes`。

### 0-6. 暫定師団 "Militiaaaa" の整理【任意・低優先】

`.8` が BUL/SER/HUN/ROM に生成する師団テンプレート名が仮置きのまま。βのローカライズ対象になるので、`"Militia"` 等へリネームし、`prioritize_location = 9660` が4ヶ国すべてで妥当かを確認すること（現状、全国が同じ location を指している）。

---

## 5. Phase 1：BOH・CROの自治領邦

**Phase 2の終端NFはCROへの要求で終わる。CROが存在しなければ枝を書けない。** ここが実質的なブロッカー。

### 1-1. タグと初期状態

- BOH・CRO のタグが既に存在するか確認する。無ければ新設
- 初期領有州・コア設定（CRO: クロアチア本土＋スレム西部＝SERの請求対象／BOH: ボヘミア・モラヴィア）
- 両国とも **GERの属国** として開始し、**中央保障条約**（GER・ITA・BOH・CRO）の加盟国

### 1-2. カスタム自治レベル「自治領邦」

`common/autonomous_states/` に新規定義。要件：

| 項目 | 内容 |
|---|---|
| 資源・工場 | 宗主（GER）が完全にアクセスできる |
| 外交 | ベルリンに委任（自主的な陣営加入・宣戦をしない） |
| 参戦 | **宗主の戦争に自動参戦。逆に自治領邦が攻撃された場合は宗主が自動参戦する** |
| 講和 | **単独講和不可** |
| 自治度 | 上下する。BOHは「忠誠度」の受け皿として使う（GER側実装で参照） |

**「CROへの宣戦が確実にGERとの全面戦争へ拡大すること」がβの最重要要件。** ここが繋がらないと大戦が起きない。

### 1-3. 講和会議での扱い

大戦の講和会議でBOH・CRO領がどう処理されるかをスクリプトで明示すること（βは簡易でよいが、州が消える・帰属不明になる事故は避ける）。

---

## 6. Phase 2：SER幕間枝（1928春 → 1929夏）

### 6-1. 設計方針

- **内政ツリーを増築しない。** これは開戦導線である。平時枝を太らせると1929年秋の開戦に間に合わなくなる
- 既存 `focus_SER` ツリーに **`allow_branch` で追加**する。新しいfocus_treeを `load_focus_tree` で差し替えてはならない（取得済みNFが飛ぶ）
- 座標は既存ツリーと重ならない位置に確保すること
- 終端NFは**直接宣戦しない**。Phase 3の危機イベント連鎖に投げる

### 6-2. 出現条件と日数配分

```
allow_branch = { has_global_flag = vf_ended_balkan_war }
```

正史では講和1928年4月 → サラエボの再来1929年8月末で、**約490日**。14NF を `cost = 5`（35日）で置くと 14 × 35 = 490日 でほぼ一致する。既存ツリーは `cost = 4` だが、**幕間枝は `cost = 5` を標準とする**。

さらに終端NF `focus_SER_pol_sarajevo_again` には `available = { date > 1929.6.1 }` を置き、最短走行でも1929年夏より前には危機が起きないようにする。

### 6-3. NF一覧（14本）

| # | 名称 | ID | 前提 | completion_reward の骨子 |
|---|---|---|---|---|
| 1 | 講和の後で | `focus_SER_pol_after_the_peace` | （枝の入口） | 幕間枝の解禁。安定度+、PP+ |
| 2 | 露国軍事使節の受入 | `focus_SER_pol_receive_russian_mission` | 1 | `set_global_flag = vf_SER_patronage_russia`、RUSとの関係+ |
| 3 | 汎スラヴの大義 | `focus_SER_pol_panslavic_cause` | 2 | 国民精神「汎スラヴの大義」付与（戦争協力度+、徴兵可能人口+） |
| 4 | 露仏の保障 | `focus_SER_pol_franco_russian_guarantee` | 3 | FRA・RUSとの関係+。**陣営加入の扱いは §10-3 の裁定待ち。βは関係改善＋フラグのみ** |
| 5 | ウィーン条約軍備制限の破棄 | `focus_SER_mil_abrogate_vienna_treaty` | 1 | ウィーン条約由来の軍備制限idea除去。**該当ideaの現存を要確認**、無ければ新規作成 |
| 6 | 露式装備の導入 | `focus_SER_mil_russian_equipment` | 5 | 歩兵装備の研究ボーナス、装備供与 |
| 7 | 突撃隊の正規編入 | `focus_SER_mil_integrate_zbor_battalions` | 5 | 師団テンプレート／人的資源。既存 `focus_SER_mil_zbor_battalion` の続きとして接続 |
| 8 | 参謀本部の戦争計画 | `focus_SER_mil_general_staff_war_plan` | 6 + 7 | 陸軍経験値、計画立案速度 |
| 9 | 回復地の統合 | `focus_SER_eco_integrate_recovered_lands` | 1 | 講和で獲得した州（803/106/764等）のインフラ・工場。**保有していない州はスキップするようIF分岐で書くこと** |
| 10 | 軍需産業の拡張 | `focus_SER_eco_expand_arms_industry` | 9 | 軍需工場+2 |
| 11 | 最後の失地 | `focus_SER_pol_the_last_irredenta` | 4 + 8 | スレム・マチュヴァへの `add_claim_by`。国民精神で戦争協力度+ |
| 12 | 在クロアチア同胞への呼びかけ | `focus_SER_pol_call_to_serbs_in_croatia` | 11 | CROの安定度-、自治度への圧力。`set_global_flag = vf_SER_agitating_croatia` |
| 13 | スレムとマチュヴァの要求 | `focus_SER_pol_demand_srem_and_macva` | 12 | GER・CROへ要求イベント。緊張度+ |
| 14 | サラエボの再来 | `focus_SER_pol_sarajevo_again` | 13 + `date > 1929.6.1` | **`country_event = vf_greatwar.1` を発火。宣戦はしない** |

### 6-4. 講和結果による分岐

`event_SER_pol.10` の4段階のどれで講和したかで幕間枝の条件を変えること。**バルカン戦争の勝ち方が1929年に効く**設計にする。

- 803（マケドニア相当）を保持している → #9「回復地の統合」がフル効果
- 803・106 の両方を保持 → #10「軍需産業の拡張」の工場+1追加
- 白紙和平だった → #11「最後の失地」に安定度ペナルティを追加（国内で「またしても何も得られなかった」）

判定は `controls_state = 803` 等の直接判定でよい。講和段階を記録する専用フラグを `.10` の各分岐で立てておくと後段が楽になる（`vf_SER_peace_tier_1`〜`_4`）。**この方式を推奨**。

---

## 7. Phase 3：クロアチア危機と世界大戦の発火

### 7-1. ファイル構成

複数国が絡むため、SERのイベントファイルとは分けること。

- `events/vf_greatwar.txt` / namespace `vf_greatwar`

### 7-2. 連鎖の骨格（約5週間）

史実の七月危機に倣い、開戦決定を短期間で駆け抜ける。日数は `days = N` で相対指定する。

| ID | Day | 発火先 | 内容 |
|---|---|---|---|
| `.1` | 0 | SER | **ザグレブ／サラエボの突発事件**。危機の開始。`set_global_flag = vf_croatia_crisis_started`。CRO・GERへ通知 |
| `.2` | +3 | GER | **帝国の対応**。選択肢: 強硬（最後通牒）／仲裁／黙認。βは強硬を既定路線とし、他は効果を軽くしてよい |
| `.3` | +7 | SER | **露仏の保障確認**。`vf_SER_patronage_russia` の有無で文面と効果が変わる |
| `.4` | +14 | SER | **GERからの最後通牒**。選択肢: 受諾（屈服＝開戦回避、代償として安定度・PP大損失＋体制動揺）／拒否 |
| `.5` | +21 | 全体 | **動員の連鎖**。緊張度大幅上昇。各国に警告ニュース |
| `.6` | +35 | SER | **開戦**。`set_global_flag = vf_greatwar_started`。SERがCROへ宣戦 → 自治領邦の規定によりGERが自動参戦 → 同盟連鎖でENG参戦、露仏がSER側で参戦 |
| `.10` | +35 | 各国 | **参戦判定**。§8のフラグ群を読んで POL / OTT / ITA / IST の去就を決める |

### 7-2b. 参戦連鎖は「陣営任せ」にしないこと【重要】

`.6` の開戦処理は、**陣営の自動連鎖に頼りきらず、意図した参戦国を明示的に戦争へ加えること**。理由は2つ。

- 陣営の自動連鎖はAIの `join_war` 判断・戦争協力度・世界緊張度に左右され、**同じ条件でも参戦しないことがある**。これではT2が再現しない
- §4-0-0 の衝突2により、SERは救国同盟の盟主のまま露仏協商には入れない。**露仏の参戦はfactionでは表現できない**

したがって `.6` の処理は次の順で書く。

1. `SER = { declare_war_on = { target = CRO type = ... } }`
2. **自動連鎖に期待する分**（GERの自動参戦、ENGの同盟参戦）を実行後に `has_war_with` で**検証**し、参戦していなければログ用にフラグを立てる（`vf_greatwar_chain_incomplete`）
3. **自動連鎖で表現できない分**（RUS・FRAのSER側参戦）は `add_to_war = { targeted_alliance = SER  enemy = GER }` で明示的に加える
4. `.10` の参戦判定（POL / OTT / ITA / IST）も同様に `add_to_war` で明示

`vf_greatwar_chain_incomplete` が立った状態はバグである。T2・T8で必ず確認すること。

### 7-3. 宥和ルート（必須）

`.4` の「受諾」を選ぶと開戦が**数ヶ月遅れる**（回避ではなく遅延）。`vf_croatia_crisis_deferred` を立て、6〜9ヶ月後に `.1` を再発火する。SERは代償として安定度・戦争協力度を失う。

これがないと危機イベントが単なる「はい」ボタンになる。

### 7-4. フラグ未設定でも完走すること【最重要】

幕間の危機3件（ローマ進軍・波立危機・オスマン危機）は**まだ実装されていない**。したがって `vf_POL_tilt_*` 等は**どれも立っていない状態が既定**である。

`.10` の参戦判定は必ず `ELSE` 節を持ち、**フラグが1つも無くても正史どおりの陣営で開戦が成立する**こと。フラグは「既定からのズレ」としてのみ作用させる。

```
IF = { limit = { has_global_flag = vf_POL_tilt_fra } ... }
ELSE_IF = { limit = { has_global_flag = vf_POL_tilt_ger } ... }
ELSE = { # 既定: POLは中立 }
```

### 7-5. 大戦の終結（β簡易版）

勝敗が付いてゲームが終わること。凝った講和は不要。ただしBOH・CRO領の帰属だけは明示的に処理すること（§5-3）。

---

## 8. フラグ・変数の契約【最重要】

**他国の実装（特にGER）がこれを読む。名前を勝手に変えないこと。** 新しく必要になったら本表に追記した上で報告すること。

### 既存（変更禁止）

| 名前 | 種別 | 立てる場所 | 意味 |
|---|---|---|---|
| `vf_started_balkan_war` | global flag | `event_SER_pol.8` | バルカン戦争開戦 |
| `vf_ended_balkan_war` | global flag | `event_SER_pol.10` | バルカン戦争講和成立 |
| `vf_HUN_left_balkan_war` | global flag | `event_SER_pol.9` | ハンガリーの戦線離脱 |

### 本タスクで新設

| 名前 | 種別 | 立てる場所 | 意味 |
|---|---|---|---|
| `vf_balkan_war_min_duration_passed` | global flag | `event_SER_pol.11` | 開戦から330日経過（講和解禁） |
| `vf_SER_peace_tier_1`〜`_4` | global flag | `event_SER_pol.10` | 講和の段階（1が最大の戦果） |
| `vf_SER_patronage_russia` | global flag | NF #2 | セルビアが露の後援を受け入れた |
| `vf_SER_agitating_croatia` | global flag | NF #12 | 在クロアチア・セルビア人の扇動中 |
| `vf_croatia_crisis_started` | global flag | `vf_greatwar.1` | クロアチア危機の開始 |
| `vf_croatia_crisis_deferred` | global flag | `vf_greatwar.4` | 宥和により危機が延期された |
| `vf_greatwar_started` | global flag | `vf_greatwar.6` | 世界大戦の勃発 |
| `vf_greatwar_chain_incomplete` | global flag | `vf_greatwar.6` | **参戦連鎖の検証に失敗した（＝バグ）**。立っていたら報告すること |
| `vf_SER_franco_russian_guarantee` | global flag | NF #4 | 露仏がSERを保障した（実装時に追加。2026-08-26） |
| `vf_SER_albania_war` | **country flag (SER)** | `event_SER_pol.7` | アルバニア平定作戦の開戦。`.12`（アルバニアの崩壊）が経過日数判定に使う（実装時に追加。2026-08-26。ALB戦泥沼化対策） |
| `vf_SER_preparing_war_ALB` | global flag | NF `focus_SER_pol_lost_kosovo`（hidden_effect） | AI用。平定作戦に備えALB国境へ集結（`_vf_Balkan.txt` が読む。2026-08-26追加） |
| `vf_SER_preparing_war_BUL` | global flag | NF `focus_SER_pol_oppose_balkan_pact`（hidden_effect） | AI用。復讐の日に備えSER・GRE・ROMがBUL・HUN国境へ集結（同上） |
| `vf_SER_preparing_war_CRO` | global flag | NF `focus_SER_pol_the_last_irredenta`（hidden_effect） | AI用。大戦に備えCRO国境へ集結（同上） |

### 受け口だけ用意する（本タスクでは立てない・読むだけ）

幕間の危機イベントが後日立てる。**Phase 3 はこれらを読む形で書くが、未設定でも完走すること（§7-4）。**

| 名前 | 立てる予定の実装 | 影響 |
|---|---|---|
| `vf_ITA_regime_fascist` / `vf_ITA_regime_liberal` | ローマ進軍（1925） | イタリアの参戦・中立 |
| `vf_ITA_grudge_SER` | 伊のアルバニア抗議 | イタリアの対セルビア姿勢 |
| `vf_POL_tilt_ger` / `vf_POL_tilt_fra` / `vf_POL_tilt_neutral` | 波立危機（1927） | ポーランドの陣営 |
| `vf_OTT_alignment_fra` / `_ger` / `_neutral` | オスマン危機（1929） | オスマンの去就 |
| `vf_IST_leaning_ger` / `_ita` | イストリア交渉（GER側NF） | イストリアの帰属 ※**立てる側は実装済み**（2026-08-27。`event_GER_pol.23`「ローマとの対話」） |
| `vf_GER_route_parliament` / `_ausgleich` / `_civilwar` | GER「帝国の岐路」（1926） | 開戦時のドイツの国力・体制 |

---

## 9. 受け入れテスト

各項目を実機で走らせて結果を報告すること。**失敗した項目は黙って直さず、原因とともに報告する。**

| # | シナリオ | 期待する結果 |
|---|---|---|
| T1 | 全AI放置で1925年開始から3年観測 | 1927年前半にバルカン戦争が発生し、1928年中に `vf_ended_balkan_war` が立つ |
| T2 | 同上をさらに継続 | 1929年7月〜1930年3月の間に `vf_greatwar_started` が立ち、GER+ENG 対 FRA+RUS+SER の構図になる |
| T3 | SERプレイ、標準進行 | 幕間枝が講和後に出現し、完走して1929年夏に `vf_greatwar.1` が発火する |
| T4 | SERプレイ、**1926年2月に早期開戦** | 講和が330日後以降に正しく成立する（1928.4.1に引き延ばされない）。幕間枝も出現する |
| T5 | バルカン戦争でHUNが2州失陥 | `event_SER_pol.9` が発火し、その後も `vf_ended_balkan_war` が正しく立つ（§0-3） |
| T6 | BULを早期に完全降伏させる | 330日待たずに講和イベントが発火する |
| T7 | 白紙和平で講和（`surrender_progress` 低） | `vf_SER_peace_tier_4` が立ち、幕間枝が出現し、#9/#10 が州非保有でエラーを出さない |
| T8 | **CROへ宣戦** | GERが自動参戦し、ENGが同盟で参戦し、世界大戦へ拡大する（**β最重要**） |
| T9 | `vf_greatwar.4` で宥和を選択 | 開戦が数ヶ月遅れ、SERが安定度を失い、後に危機が再発する |
| T10 | 幕間フラグを一つも立てずに大戦まで到達 | `.10` の参戦判定がエラーなく完走し、正史の陣営になる |
| T11 | エラーログ確認 | `error.log` に本タスク由来の未定義ID・欠落ローカライズが出ていない |
| T12 | **1925.3.1 に外交画面で陣営を目視** | 英独同盟・露仏協商・対セルビア包囲同盟が陣営として実在し、§13の表どおりの構成になっている |
| T13 | **CROの所属確認** | CROがGERの属国であり、かつバルカン戦争（1927）にGERが巻き込まれない（§4-0-0 衝突3） |
| T14 | 救国同盟NFを取らずに「復讐の日」を取る | SERが単独でBUL・HUNと戦う事態にならない（`available` で塞がれている、またはフォールバックが働く） |
| T15 | バルカン戦争開戦直後 | HUNが陣営連鎖で自動参戦し、`event_SER_pol.9` が発火しうる状態になっている |
| T16 | T2の走行後にフラグ確認 | `vf_greatwar_chain_incomplete` が**立っていない**（立っていたら参戦連鎖のバグ） |
| T17 | AI放置でSERを観測 | SERのAIが幕間枝のNFを実際に取り進める（`ai_will_do` が0や未設定で止まっていない） |
| T18 | §13・§14 の表 | 空欄なく記入され、NF/event外の処理がすべて相互参照コメントで結ばれている |

---

## 10. 要裁定（主宰の判断を待つこと。実装するな）

> **裁定記録（2026-08-26 主宰）**
> 1. 実装済みの「復讐の日」を正とし、「アルバニアからの略奪」（`focus_SER_eco_plunder_albania`）のみ補完 → 実装済み
> 2. 「アルバニアの脅威認識」は削除して確定 → 実装済み
> 3. βは共同交戦国方式（推奨案どおり）。NF #4 は保障＋関係改善＋フラグのみ → 実装済み
> 4. クロアチア危機の口実は**国境衝突型** → 実装済み
> 5. βは1929年固定（推奨どおり） → 実装済み
> 6. 衝突1: 中央保障条約はfaction化せずITA無所属（推奨どおり）／衝突2: 共同交戦国＋`add_to_war`（推奨どおり）／衝突3: 実装上CROはバルカン協商に非加盟で既に回避
> 追加裁定: `event_HUN_pol.1` は既存の革命（内戦）イベントを正とし維持する

以下は設計資料と実装が食い違っている、または未決定の項目。**該当箇所に達したら手を止め、推奨案を添えて確認を求めること。**

1. **設計図35と実装の差分**（§2末尾）
   - 終端「アルバニアからの略奪」を実装するか。現状 `focus_SER_eco_path_to_plunder` が行き止まり
   - 「失地回復の準備 → 開戦」（図）と「復讐の日」（実装）のどちらを正とするか
   - 推奨: 実装済みの「復讐の日」を正とし、「アルバニアからの略奪」だけを補完する

2. **「アルバニアの脅威認識」のコメントアウト**を復活させるか、削除して確定するか

3. **開戦時のセルビアの陣営上の地位**。露仏協商に正式加盟するのか、共同交戦国どまりか。
   NF #4「露仏の保障」の効果が変わる。推奨: βは共同交戦国（関係改善＋フラグのみ）とし、`vf_greatwar.6` で参戦させる

4. **クロアチア危機の口実**。要人暗殺型（サラエボの反復）か、国境衝突型か。イベント文の骨格が変わる

5. **開戦年の可変幅**。planning/03 では「1929±1年の窓」が本リリース要件とされている。βで窓を実装するか、1929年固定にするか。推奨: βは固定

6. **陣営の設計衝突3件**（§4-0-0）。監査結果が出てから諮ること
   - 衝突1: ITAの二重外交をどう表現するか（推奨: 中央保障条約をfaction化せず、ITAは無所属で開始）
   - 衝突2: SERは救国同盟の盟主のまま露仏協商に入れない（推奨: 共同交戦国とし `add_to_war` で処理）
   - 衝突3: CROが包囲同盟に入っているとバルカン戦争でGERが巻き込まれ、大戦が2年早まる（推奨: CROを包囲同盟から外す）

7. **監査で発見した分散処理の統合**。`on_action` や `decision` に散っていた処理を集約するか、現状維持で相互参照コメントのみに留めるか

---

## 11. 規約

- **NF ID**: `focus_SER_pol_*`（政治・外交）/ `focus_SER_mil_*`（軍事）/ `focus_SER_eco_*`（産業・経済）。既存の接頭辞体系を維持する
- **アイコン**: `GFX_goal_focus_SER_<ID以下同文>` を指定しつつ、実素材が無い間は `GFX_goal_unknown` にフォールバックさせる（既存コードのコメントアウト方式を踏襲）
- **イベント namespace**: SER固有は `event_SER_pol`、多国間の大戦連鎖は `vf_greatwar`
- **フラグ**: すべて `vf_` 接頭辞
- **ローカライズ**: 日本語が第一言語。NF名・イベントタイトルはβ必須、desc は骨子だけでも可（`to_do` を残す場合は必ず報告する）
- **コメント**: 既存ファイルは日本語コメントが豊富に入っている。同じ密度で書くこと
- 既存の命名ミス（`Militiaaaa` 等）を見つけたら、直す前に報告すること

### 11-1. 関連ファイルの明記【必須】

**新規作成・改修したファイルの冒頭に、必ず以下のコメントブロックを置くこと。** 処理がNF・イベント以外へ散る場合は特に重要で、**置いた側と呼ぶ側の双方に相互参照を書く**（片方向では次のセッションが辿れない）。

```
# =========================================================
# VF / セルビア幕間枝・世界大戦の発火
# 指示書: docs/planning/06_SER開戦導線_実装指示書.md
#
# 関連ファイル:
#   common/national_focus/vf_focus_SER.txt    … NF本体（幕間枝14本）
#   events/vf_SER_events.txt                  … event_SER_pol.1〜.11
#   events/vf_greatwar.txt                    … クロアチア危機〜開戦連鎖
#   common/ideas/vf_SER_ideas.txt             … 汎スラヴの大義 / 軍備制限
#   common/autonomous_states/vf_autonomy.txt  … 自治領邦（GERの自動参戦）
#   history/countries/SER - *.txt             … 開始時の陣営・請求権
#   common/on_actions/vf_on_actions.txt       … （使っている場合のみ）
#
# 立てるフラグ: vf_SER_patronage_russia / vf_SER_agitating_croatia
# 読むフラグ:   vf_ended_balkan_war / vf_SER_peace_tier_*
# =========================================================
```

- 処理をNF・イベントの外（`on_actions` / `decisions` / `scripted_effects` 等）へ置く場合は、**なぜそこに置いたかを1行で書くこと**。「NFでは表現できないため」等
- 置いたら **§14の「処理の所在マップ」を必ず更新する**

---

## 12. 着手順チェックリスト

- [ ] 実リポジトリのファイル構成を確認し、想定パスとの差異を報告
- [ ] **Phase 0-0: 陣営の実在監査 → §13 の表を記入。衝突1〜3の解決方針を推奨案付きで報告**
- [ ] **Phase 0-0b: 処理の所在監査（grep）→ §14 の表を記入**
- [ ] Phase 0-0: `.8` のSER側参戦ロジック（`is_in_faction_with`）を塞ぐ
- [ ] Phase 0-1: `event_SER_pol.10` に `tag = SER` を追加
- [ ] Phase 0-2: 日付ロックを `event_SER_pol.11`（330日遅延）方式へ置換
- [ ] Phase 0-3: `.9` 経由で `vf_ended_balkan_war` が立たない問題を再現確認 → `.10` 一本化
- [ ] Phase 0-4: 州803/106/77 の二重移譲を確認
- [ ] Phase 0-5: `event_HUN_pol.1` を執筆
- [ ] Phase 0 完了時点で T1・T4・T5・T6・T7・T12・T14・T15 を実行
- [ ] Phase 1: BOH・CROタグと自治領邦の定義 → T8・T13 を実行
- [ ] Phase 2: 幕間枝14NF → T3・T7・T17 を実行
- [ ] Phase 3: `vf_greatwar` 連鎖 → T2・T9・T10・T16 を実行
- [ ] T11（エラーログ）・T18（表の記入確認）で総仕上げ
- [ ] §8のフラグ表に追加・変更があれば追記して報告
- [ ] §13・§14 を記入済みの状態でこの指示書を更新し、次のセッションへ引き継ぐ

---

## 13. 陣営構成表【監査結果をここに記入すること】

§4-0-0 の監査で埋める。**「実装状況」が「未実装」の行があれば、それが大戦の連鎖を止める原因になる。**

監査実施 2026-08-26（実装セッション）。監査時点では英独同盟・露仏協商とも**未実装**だったため、本タスクで新設した。

| 陣営 | 想定盟主 | 想定構成 | 実装状況（記入） | faction key（記入） | 備考 |
|---|---|---|---|---|---|
| 英独同盟 | GER | GER, ENG（+ LIT） | **本タスクで新設**（`history/countries/GER - Germany.txt` の `create_faction`）。構成 GER+ENG。LITは陣営外（GERの保障のみ） | `"英独同盟"`（リテラル文字列） | ENGの参戦はここに依存。**必須** |
| 露仏協商 | FRA または RUS | FRA, RUS | **本タスクで新設**（`history/countries/FRA - France.txt`）。盟主FRA、構成 FRA+RUS | `"露仏協商"`（リテラル文字列） | 露仏のSER側参戦は `vf_greatwar.6` の `add_to_war` で明示的に処理する |
| 中央保障条約 | GER | GER, ITA, BOH, CRO | **faction化せず**（推奨案どおり）。BOH・CROはGERの自治領邦、ITAは無所属の天秤で開始 | — | **衝突1** → 解決（ITA無所属） |
| 仏伊協商 | FRA | FRA, ITA | 未実装（faction化せず）。ITAは無所属 | — | 衝突1。ITAは天秤として無所属 |
| 対セルビア包囲同盟 | HUN? | HUN, CRO, ALB, BUL | **「バルカン協商」として実装済み**（`history/countries/BUL - Bulgaria.txt`）。盟主BUL、構成 BUL+MNT+HUN。**CRO・ALBは非加盟** | `"バルカン協商"`（リテラル文字列） | **衝突3** → CRO非加盟のため既に回避されている。HUNの参戦は `.8` の明示的 `add_to_war` でも保証（T15） |
| 救国同盟 | SER | SER, GRE, ROM | NF `focus_SER_pol_alliance_for_salvation` で生成（実装済み） | `"救国同盟"`（リテラル文字列） | **衝突2** → SERは盟主のまま共同交戦国方式（`vf_greatwar.6` の `add_to_war`）で解決 |
| 伊洪協商 | ITA | ITA, HUN | 未実装（faction化せず） | — | 1850年からの伝統的友好。faction化は不要 |

**属国関係（陣営とは別に確認）**

| 宗主 | 属国 | 自治レベル | 実装状況（記入） | 備考 |
|---|---|---|---|---|
| GER | CRO | 自治領邦（Phase 1で新設） | **実装済み**。`puppet` + `set_autonomy = autonomy_vf_crown_dominion`（`common/autonomous_states/_vf_autonomy_crown_dominion.txt`） | **T8の要**。自動参戦が働かない場合のフォールバックは `vf_greatwar.6` にある |
| GER | BOH | 自治領邦（Phase 1で新設） | **実装済み**。同上 | 自治度を「忠誠度」の受け皿として使う |
| GER | LIT | （要確認） | 属国ではない。GERがLITを保障（`history/countries/LIT - Lithuania.txt` の `diplomatic_relation = guarantee`） | 親独衛星国は保障で表現されている |

**補足（監査で判明した注意点）**
- MNTが「バルカン協商」に加盟したまま `event_SER_pol.4` で併合される。`annex_country` は強制実行されるため動作はするが、併合前に「復讐の日」へ達した場合はMNTもBUL側で参戦する（`.8` の明示的 `add_to_war` の対象になる）。挙動としては設定に反しない。
- `event_HUN_pol.1` は指示書0-5の想定（フレーバー）と異なり**ハンガリー共産革命（内戦生成）イベントとして実装済み**。主宰裁定（2026-08-26）により革命イベントを正とし、指示書側のズレとして記録する。

---

## 14. 処理の所在マップ【監査結果をここに記入すること】

§4-0-0b の監査で埋める。**NF・イベント以外の場所にある処理をすべて洗い出し、相互参照コメント（§11-1）を張った上でここに記録する。**

監査実施 2026-08-26（実装セッション）。grep対象: `vf_` / `focus_SER` / `event_SER_pol` / `SER` / `BUL` / `HUN` / `CRO` / `BOH` / `balkan` / `faction`

**実パスの注記**: 実リポジトリの命名は指示書の想定と異なり、VF固有ファイルは `_vf_` 接頭辞（例: `events/_vf_events_SER.txt`、`common/national_focus/_vf_focus_SER.txt`）。本タスクの新規ファイルもこの規約に合わせた。

| ファイル | 種別 | 何をしているか | 関連するNF / イベント | 相互参照コメント |
|---|---|---|---|---|
| `common/ai_strategy/_vf_Balkan.txt` | ai_strategy | `vf_started/ended_balkan_war` を読み、バルカン諸国AIの開戦準備・師団比率を制御。**本タスクで大戦準備（対CRO）の `VF_serbia_greatwar_prep_strategy` を追記** | `event_SER_pol.8` / `.10`、幕間枝全般 | ☑ |
| `common/ideas/_vf_ideas_SER.txt` | ideas | `idea_balkan_war`（`.8` が180日付与）、SER開始時国民精神、**本タスクで軍備制限・幕間枝の国民精神を追加** | `event_SER_pol.8`、NF #3/#5/#8/#11 | ☑ |
| `common/scripted_effects/01_startup.txt` | scripted_effect | `startup_cosmetic_tag`（開始時の国名コスメティックタグ一括設定のみ。陣営・SER処理なし） | — | 不要（無関係） |
| `common/opinion_modifiers/_vf_opinion.txt` | opinion_modifier | **本タスクで新設**。幕間枝 #2/#4 の関係値改善の実体 | NF #2/#4 | ☑ |
| `common/autonomous_states/_vf_autonomy_crown_dominion.txt` | autonomy_state | **本タスクで新設**。自治領邦（BOH・CRO）。NFでは表現できない属国規則のためここに置く | `vf_greatwar.6`（T8） | ☑ |
| `history/countries/GER - Germany.txt` | history | **本タスクで英独同盟の `create_faction` を追加** | `vf_greatwar.6` | ☑ |
| `history/countries/FRA - France.txt` | history | **本タスクで露仏協商の `create_faction` を追加** | `vf_greatwar.6` | ☑ |
| `history/countries/BUL - Bulgaria.txt` | history | 開始時に「バルカン協商」（BUL+MNT+HUN）を生成（既存） | `event_SER_pol.8` / `.9` | 既存のためコメント未付与（変更せず） |
| `history/countries/CRO - Croatia.txt` / `BOH - Bohemia.txt` | history | GERの属国。**本タスクで自治領邦レベルへ変更** | `vf_greatwar.6` | ☑ |
| `history/countries/SER - Serbia.txt` | history | 開始時国民精神。**本タスクで `idea_SER_vienna_arms_limit` を追加** | NF #5 | ☑ |
| `history/countries/LIT - Lithuania.txt` | history | GERがLITを保障（既存） | — | 既存のため変更せず |
| `events/_vf_events_HUN.txt` | event | `event_HUN_pol.1`＝ハンガリー共産革命（内戦生成）。`.8` から30日後に予約される（既存。裁定により維持） | `event_SER_pol.8` | 既存のため変更せず |
| `events/_vf_events_ITA.txt` / `common/national_focus/_vf_focus_ITA.txt` | event / NF | ITA固有処理。`vf_ITA_pol` namespace のみで、SER・大戦フラグの読み書きなし | — | 不要（無関係） |
| `common/decisions/` | decision | SER・大戦関連なし（`VF_debug.txt` にデバッグ用「テスト陣営」の `create_faction` があるのみ） | — | 不要 |
| `common/on_actions/` | on_action | VF固有の処理なし（バニラ由来のみ） | — | 不要 |
| `common/scripted_triggers/` | scripted_trigger | SER関連なし | — | 不要 |
| `common/ai_focuses/` | ai_focus | SER関連なし（幕間枝のAI誘導はNF側の `ai_will_do = 20` で対応） | 幕間枝全般（T17） | 不要 |
| `common/bookmarks/the_gathering_storm.txt` | bookmark | `startup_cosmetic_tag` を呼ぶ（コスメティックのみ） | — | 不要 |
| `history/states/` | state | 州803/106/77→BUL、764/82/83/84→HUN、184→BUL、109（スレム・マチュヴァ）→CRO を確認済み | `.9` / `.10`、NF #9/#11、`vf_greatwar.20` | 不要（初期所有のみ） |

**記入時の注意**

- 「見たが何も無かった」場所も1行残すこと（`common/decisions/` … SER関連なし、等）。次のセッションが再監査せずに済む
- 分散していた処理を勝手に統合・移動しないこと。判断は主宰に諮る
- ここに書かれていない場所に処理を新設した場合は、**必ず行を追加してから作業を終えること**
