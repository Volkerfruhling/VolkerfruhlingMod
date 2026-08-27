# VF β実装指示書（追補）：GER初期法・AI軍拡のリグレッション・イデオロギー参照の解消

> **この文書の位置づけ**
> `08_GER議会ルート_実装指示書.md` ＋ `09_GER議会ルート_実装報告書.md` の**続き**。単独では読めない。開発リポジトリのClaude Codeセッションへ渡す短い追補タスク。
> 作成 2026-08-27。09の報告を受けた主宰裁定（同日）に基づく。
> 前提: `06`／`07`（SER開戦導線・大戦の発火）、`08`／`09`（GER議会ルート）

---

## 0. このタスクの位置づけ

09 の報告で挙がった懸案のうち、**主宰裁定が出て着手可能になった3件**と、**未実施テストの消化**を扱う。新規のツリーやシステムは作らない。

| # | 内容 | 裁定 |
|---|---|---|
| 1 | GERが開始時に徴兵法・経済法を持たない | **記述漏れ。history に追加する**（意図的な設定ではない） |
| 2 | RUS・FRA・ENGのAI軍拡がバルカン戦争を壊していないか | **懸念事項として確認する** |
| 3 | lore が存在しないイデオロギー「民主主義」を参照している | 本追補で解消（§3 に裁定事項あり） |
| 4 | 未実施テストの消化 | §4 |

**裁定済み・着手不要**: 日数配分（08 §5-3）は**現状維持で確定**。「1926年選挙以降のNFには時期的な縛りがほぼ無い」ため、A/B/C型走行での厳密な実測は不要（優先度を下げてよい）。

---

## 1. GERの開始時の法律【記述漏れの修正】

### 1-1. 何が起きているか

09 §7 の原因分析①のとおり、**GERだけが `history/countries/GER - Germany.txt` に徴兵法・経済法を持っていない**。他の大国は history で保有している（RUS は `limited_conscription` 等）。

これは世界観上の意図ではなく**単なる記述漏れ**（主宰確認済み 2026-08-27）。GERは英独同盟の陸の柱であり、「凍りついた平和」の下でも他の大国と同程度の平時体制にあるべきである。

### 1-2. やること

1. `history/countries/GER - Germany.txt` に**開始時の徴兵法・経済法・貿易法を明示的に追加**する
   - 水準は**他の大国（RUS・FRA・ENG）と横並びに揃えること**。まず各国の history を読み、GERだけが浮かない値を選ぶ
   - 1925年・大戦前・「凍りついた平和」という文脈に照らして妥当な低めの水準にする（軍拡は1927年以降のNFとAI戦略で行う設計のため、開始時点で高くしない）
2. **`common/ai_strategy/_vf_GreatPowers.txt` と軍事NFの対策を見直す**
   - 09 §7-2 で「国土防衛計画」NFに**限定徴兵制**を、「緊急動員」に**大規模徴兵**を持たせている。開始時に法を持つようになると、**これらのNFが「既に持っている法を再付与するだけ」になる可能性がある**
   - 各NFが与える法を**開始時の法より1段上**になるよう調整すること
   - 開始時に法があると平時のAI建軍が自然に進むため、`ai_wanted_divisions_factor` 等のエスカレーション幅を**過剰にしないよう見直す**（44個師団問題への対策が今度は逆に効きすぎる恐れがある）

### 1-3. 確認

- GERの開始時師団数・人的資源が他の大国と比べて不自然でないこと
- 1929年秋の開戦時の師団数（09 §7 の目安 70〜90）が、この変更後も妥当な範囲に収まること

---

## 2. RUS・FRA・ENGのAI軍拡によるリグレッション【最優先】

### 2-1. 何が懸念か

09 §7-1 で、大国AI軍拡を**GERだけでなくRUS・FRA・ENGにも並行整備**した。大戦が一方的にならないための判断としては正しい。

しかし **RUSはセルビアの後援者**であり、**FRAは露仏協商の盟主**である。`06`／`07` で実機確認済みだった以下が、この変更で崩れている可能性がある。

- **1927年のバルカン戦争**（SER＋GRE＋ROM vs BUL＋MNT＋HUN）の戦力比
- **`event_SER_pol.9`**（HUNが2州を失って離脱）が発火するかどうか
- **`event_SER_pol.10`** の講和が4段階（`vf_SER_peace_tier_1`〜`4`）のどこに着地するか
  → **ここが変わるとSER幕間枝 #9/#10/#11 の分岐がまるごと変わる**
- **アルバニア平定作戦**（`.7`／`.12`）が120日のタイムアウト内に終わるか

### 2-2. やること

1. **AI放置で1925.3.1 → 1930年まで通し走行し、以下を記録して報告する**

| 確認項目 | 期待 |
|---|---|
| バルカン戦争の開戦時期 | 1927年前半 |
| `vf_ended_balkan_war` が立つ時期 | 1928年中 |
| **講和の tier（`vf_SER_peace_tier_*` のどれが立つか）** | `06`/`07` 時点の走行と同じ tier |
| `event_SER_pol.9`（HUN離脱）の発火有無 | 発火する |
| アルバニア戦の終結時期 | 開戦から120日以内 |
| `vf_greatwar_started` の時期 | 1929年秋 |
| 開戦時の師団数（GER / RUS / FRA / ENG / SER） | GERが一方的に劣勢でないこと |

2. **`06`/`07` 時点の結果と食い違った項目があれば、原因を切り分けて報告すること**（勝手に調整しない）
   - 切り分けの起点: `_vf_GreatPowers.txt` の RUS・FRA 向けブロックを一時的に無効化して再走行し、差分が消えるかを見る

3. 調整が必要な場合の**推奨方針**（採否は主宰裁定）
   - RUS・FRAの軍拡開始を**1928年以降**（`vf_ended_balkan_war` 後）に遅らせる。バルカン戦争の期間中は平時水準に留める
   - 理由: 正史では露仏がセルビアへ本格接近するのは1928年秋以降であり（`planning/01`）、1927年の時点で露仏が臨戦態勢にあるのは設定とも合わない

### 2-3. 注意

**SER側のスクリプト（`_vf_focus_SER.txt` / `_vf_events_SER.txt` / `_vf_Balkan.txt`）を書き換えて辻褄を合わせないこと。** 原因は大国AI側にあるはずなので、そちらで調整する。

---

## 3. イデオロギー「民主主義」の参照を解消する

### 3-1. 何が起きているか

09 §17 の監査で、このModの `common/ideologies/00_ideologies.txt` に **`democracy`（民主主義）が存在しない**ことが判明した。一方 `GER_04_lore.xlsx` 由来の記述（＝08 §15/§16）は、**3箇所で「民主主義」を参照している**。

| 箇所 | 記述 | 対応 |
|---|---|---|
| イベント「SPDの躍進」選択肢1 | 国民精神「社会改革への期待」（**月間支持率（民主主義）+0.05**） | 要差し替え |
| NF「ヴァイマル連合の勝利」 | **イデオロギー: 民主主義に固定**／政権与党が社会民主党（民主主義） | 要差し替え |
| NF「連合強化」 | **民主主義イデオロギーの支持率 +10%** | 要差し替え |

lore が書かれた時点ではバニラの4イデオロギー前提だったが、このModは独自のイデオロギー体系を持つ。**loreの文言ではなく、Modの実イデオロギーに合わせること。**

### 3-2. 前提の確認

**まず `common/ideologies/00_ideologies.txt` を読み、実在するイデオロギーの完全な一覧とサブイデオロギー構成を §5 の表に記入すること。** 09 §17 は7種（communism / socialism / liberalism / conservatism / despotism / totalitarianism / ultra_nationalism）と報告しているが、主宰は10種と認識している。**実ファイルが正。**

### 3-3. 差し替え方針【要裁定】

SPDは **`socialism`** に対応する（09 §4-2 で実装済み・確定）。問題は「ヴァイマル連合」が socialism 単独ではないこと。

> ヴァイマル連合 ＝ **社会民主党（socialism）＋ 中央党 ＋ 自由主義者（liberalism）** の三党連立（lore「ヴァイマル連合の勝利」より）

推奨案を添えて主宰に諮ること。

- **「SPDの躍進」選択肢1** → `socialism` の月間支持率 +0.05。**推奨**（SPD自身の躍進を描く選択肢なので素直）
- **「ヴァイマル連合の勝利」** → 与党を `socialism` に固定。**推奨**（09 §4-2 で実装済みの挙動と一致）
- **「連合強化」** → ここが争点。以下から選ぶ
  - (a) `socialism` +10%（実装が単純。ただし「連合の強化」という趣旨と噛み合わない）
  - (b) `socialism` +5% ＋ `liberalism` +5%（連立の実態に近い。**推奨**）
  - (c) 支持率ではなく安定度・PP等へ置き換える

### 3-4. あわせて確認

- 国民精神「議会主権」の「**イデオロギー変動への対抗 +25%**」は特定イデオロギーに依存しないため、そのままでよい
- 「1929年憲法」の「**正当性 +50**」は 09 §9-3 で本リリース送りになっている。このModに正当性メカニクスがあるか確認し、無ければ恒久的に削除して報告すること
- **loreの原文（08 §15/§16）は書き換えないこと。** 実装側で読み替え、その対応を §5 の表に記録する

---

## 4. 未実施テストの消化

09 §9-1 の残り。**優先度順**に並べた。上から潰し、結果を報告すること。

| 優先 | # | シナリオ | 確認内容 |
|---|---|---|---|
| **高** | §2 の通し走行 | AI放置 1925→1930 | §2-2 の表（リグレッション確認）**このタスクの本体** |
| **高** | T-GER-14 | エラーログ | `error.log` に未定義ID・欠落ローカライズが出ていないこと |
| **高** | T-GER-5 | 議会ルート完走 | 国民精神の置換チェーン（1928年改革が3種を吸収／1929年憲法が置換／「枢密院の不在」の除去） |
| 中 | T-GER-12 | 帝冠領再編ディシジョン | 可変コスト（ミヒャエリス在職+50%／中央党軸-25%／枢密院廃止後）が正しく再計算されること |
| 中 | T-GER-4 | 1926年選挙の重心3種 | 首相（エーベルト／マルクス／シュトレーゼマン）と後続イベントの分岐 |
| 中 | T-GER-13 | バルカン戦争の勃発・講和 | GER側で「バルカンの砲声」「ベオグラードの講和」が発火すること |
| 中 | — | 選挙の完了時期 | 09 §6 の AI ロック修正後、**選挙が1926年内に完了する**こと |
| 低 | T-GER-10 | 開戦後 | 軍事・産業ツリーが継続取得可能。「嵐へ備える」系が bypass される |
| 低 | T-GER-11 | 岐路未解決で開戦 | 「対立凍結」イベントの発火 |
| 低 | T-GER-2/3 | 幹線完走・岐路 | イベント9本の発火、非表示選択肢の扱い |
| **不要** | T-GER-6〜8 | A/B/C型走行 | **裁定により優先度を下げる**（日数は現状維持で確定） |

---

## 5. 記入欄【このタスクで埋めること】

### 5-1. イデオロギー実態

出典: `common/ideologies/00_ideologies.txt`（実ファイル。**7種。`democracy` は存在しない**）。
表示名は `localisation/japanese/` より。09 §17 の報告（7種）が正しく、主宰の「10種」認識とは食い違う。

| イデオロギー（token） | 表示名 | サブイデオロギー | 備考 |
|---|---|---|---|
| `communism` | 共産主義 | `communism_ideology` / `collective_communism` / `left_wing_communism` / `military_communism` | |
| `socialism` | 社会主義 | `socialism_ideology` / `marxism` / **`socialdemocratism`** / `democratic_socialism` / `social_populism` / `religious_socialism` / `revolutionary_front` / `sandicalism` / `left_wing_nationalism` / `social_nationalism` / `anarcho_communism` | **SPDの対応先**（09 §4-2 で実装済み） |
| `liberalism` | 自由主義 | `liberalism_ideology` / `national_liberalism` / `market_liberalism` / `social_liberalism` / `classical_liberalism` / `christian_democracism` | ヴァイマル連合の自由主義者・中央党の対応先候補 |
| `conservatism` | 保守主義 | `conservatism_ideology` / `liberal_conservatism` / `national_conservatism` / `social_conservatism` / `agrarian_fundamentalism` / `paternalistic_conservatism` / `christian_conservatism` | **GERの開始時与党** |
| `despotism` | 権威主義 | `despotism_ideology` / `authoritarian_democracy` / `military_regime` / `civilian_dictatorship` / `aristocratic_reactionism` / `royal_autocracy` / `warlord_dictatorship` / `business_nation` / `interim_government` / `oligarchy` / `priestly_system` / `theocracy` / `colonial_government` | RUS・FRA・JAPの与党 |
| `totalitarianism` | 全体主義 | `totalitarianism_ideology` / `national_socialism` / `national_bolshevism` / `national_syndicalism` / `national_corporatism` / `personality_cult_socialism` / `caesarism` / `revolutionary_nationalism` | |
| `ultra_nationalism` | 超国家主義 | `ultra_nationalism_ideology` / `supermilitarism` / `religious_fundamentalism` / `eurasianism` / `slavo_national_movement` | |

### 5-2. lore「民主主義」参照の読み替え記録

| lore の記述箇所 | lore の文言 | 実装での読み替え | 裁定 | 実装状況 |
|---|---|---|---|---|
| イベント「SPDの躍進」選択肢1 | 月間支持率（民主主義）+0.05 | 時限精神 `idea_GER_hope_for_social_reform` の `socialism_drift = 0.05`（365日） | 推奨案どおり | **09時点で既に実装済み**。変更不要 |
| NF「ヴァイマル連合の勝利」 | イデオロギー: 民主主義に固定 | `set_politics = { ruling_party = socialism }` ＋ `add_popularity socialism 0.35`。元首欄は `add_country_leader_role`（`socialism_ideology`）でカール1世を維持 | 推奨案どおり | **09時点で既に実装済み**。変更不要 |
| NF「連合強化」 | 民主主義イデオロギーの支持率 +10% | `add_popularity socialism 0.05` ＋ `add_popularity liberalism 0.05` | **案(b)**（2026-08-27 主宰裁定） | 本タスクで実装（変更前は案(a) の socialism +10%） |

**案(b) を補強する所見**: このModのローカライズでは `liberalism_desc` が「**民主主義政権**」と訳されており、
`liberalism` が事実上バニラの democracy の位置を占めている。また中央党はサブイデオロギー `christian_democracism`（キリスト教民主主義）
に対応するため、**中央党と自由主義者をまとめて `liberalism` で表現できる**。
合計の上がり幅は10%で案(a)と同じであり、憲法改正までのイデオロギー収支は変わらない。

#### 5-2-1. §3-4 の確認結果

| 項目 | 結果 |
|---|---|
| 国民精神「議会主権」の「イデオロギー変動への対抗 +25%」 | `drift_defence_factor = 0.25` で実装済み。特定イデオロギーに依存しないため**そのまま**（追補の想定どおり） |
| 「1929年憲法」の「正当性 +50」 | **恒久的に削除した**。HOI4 の `legitimacy` は亡命政府（government in exile）専用のメカニクスで、主権国家である GER には値そのものが存在しない。このModにも独自の正当性メカニクスは無く、`legitimacy_gain_factor` / `legitimacy_daily` はバニラの指導者特性（`00_traits.txt`）でのみ使用されている。`focus_GER_pol_constitutional_reform` の `TODO(VF)` を削除理由のコメントへ置き換えた（09 §9-3 の本リリース送りTODOから**除去**） |
| lore 原文（08 §15/§16） | **書き換えていない**。ローカライズのdesc内に残る「民主主義」はフレーバー文であってイデオロギートークンの参照ではないため、`focus_GER_pol_1926_election_desc` / `focus_GER_pol_abolish_privy_council_desc` / `focus_GER_pol_constitutional_reform_desc` もそのまま維持した |

### 5-3. 開始時の法律（横並び確認）

**§1-1 の前提の訂正**: `history/countries/` 全109ファイルを走査した結果、**「GERだけが法を持たない」は不正確**だった。
三法すべてを明記しているのは **RUS のみ**、ENG は貿易法のみ、**FRA・ITA・JAP は GER と同様に全部既定値**である。
したがって「他の大国と横並び」の基準が RUS なのか FRA/ENG なのかで結論が変わるため、主宰に上程して裁定を得た（2026-08-27）。

既定値（`default = yes`）: 徴兵法 `volunteer_only` / 経済法 `civilian_economy` / 貿易法 `export_focus`。

| TAG | 徴兵法 | 経済法 | 貿易法 | 出典ファイル |
|---|---|---|---|---|
| **GER** | **`limited_conscription`**（本タスクで追加） | **`low_economic_mobilisation`**（本タスクで追加） | **`export_focus`**（明示。既定と同一） | `GER - Germany.txt` |
| RUS | `limited_conscription` | `partial_economic_mobilisation` | （記述なし→既定 `export_focus`） | `RUS - Russia.txt` |
| FRA | （記述なし→既定 `volunteer_only`） | （記述なし→既定 `civilian_economy`） | （記述なし→既定 `export_focus`） | `FRA - France.txt` |
| ENG | （記述なし→既定 `volunteer_only`） | （記述なし→既定 `civilian_economy`） | `free_trade` | `ENG - United_Kingdom.txt` |
| （参考）ITA / JAP | （記述なし） | （記述なし） | （記述なし） | 各 history |
| （参考）USA | （記述なし） | `undisturbed_isolation` | `free_trade` | `USA - United_States_of_America.txt` |

**裁定（2026-08-27 主宰）**: 徴兵法 = `limited_conscription`（RUSと同格）／経済法 = `low_economic_mobilisation`（既定の1段上・RUSの1段下）。

**裁定の決め手となった発見**: この Mod の `extensive_conscription` は `available` に `has_war = yes` ＋ `enemies_strength_ratio > 0.5` を要求する
（`fascism` / `communism` 分岐はコメントアウト済み、DEN・SWE分岐はGERで偽）。したがって **AIは平時に徴兵法を一切引き上げられない**。
開始時の水準が1927年のNFまでそのまま固定されるため、GER `volunteer_only`（人的資源係数 0.015）対 RUS `limited_conscription`（0.025）の
**67%の劣位が4年半続く**ことになり、これが 09 §7 の44個師団問題の直接原因と見られる。

あわせて `set_war_support = 0.30` を明示（GERは未設定だった）。経済法をAIが自力で引き上げられる下限
（`low_economic_mobilisation` は `has_war_support > 0.15`、`partial_economic_mobilisation` は `> 0.25`）を跨ぐ値であり、
RUS 0.29 / ENG 0.49 と横並びで不自然でない。

#### 5-3-1. §1-2 の見直し結果（NFが与える法・AIエスカレーション幅）

| 対象 | 変更前 | 変更後 | 理由 |
|---|---|---|---|
| NF 軍事「国土防衛計画」`focus_GER_mil_national_defence_plan` | `limited_conscription` | **`extensive_conscription`** | 開始時に limited を持つため再付与の空振りになる。§1-2「開始時の法より1段上」。平時にこの水準へ到達できる唯一の手段（`add_ideas` は `available` を無視する） |
| NF 戦時「緊急動員」`focus_GER_war_emergency_mobilization` | `extensive_conscription` | **`service_by_requirement`** | 上と同じ理由で1段繰り上げ。人的資源係数 0.05→0.1、工業生産力・造船能力・建設速度 各 -10%、訓練時間 +20% |
| NF 戦時「戦時経済体制」`focus_GER_war_wartime_economy` | `war_economy` | `war_economy`（据え置き） | 開始時 `low`(Lv2) から2段上。重複しない |
| NF 戦時「軍需優先経済」`focus_GER_war_military_priority_economy` | `tot_economic_mobilisation` | 同（ガード追加） | 重複付与の防止のみ |
| `_vf_GreatPowers.txt` `VF_GER_base_buildup_strategy` の `ai_wanted_divisions_factor` | 100 | **50** | 開始時法で平時の人的資源が約1.67倍・工場建設ペナルティが -30%→-10% となり、AI建軍が自然に進むため二重取りを回避。段階合計は 平時50 → バルカン戦争後100 → 講和後200（RUS/FRAは同時点で150） |

**あわせて修正したバグ**: 上記4NFの `limit` にあった `NOT = { has_idea = A has_idea = B ... }` は HOI4 では `NOT(AND(...))` と評価されるため、
「いずれも持っていない」の意図と一致しない（1つでも欠ければ真になる）。`NOR` へ書き換えた。

**未調整として残した点（報告事項）**

- GERは `_VF_Law_ideas.txt` の6グループを history で明示しておらず既定値に落ちている: `religious_system_idea`→`Separation_of_church_and_state` / `women_s_rights_idea`→`Paternalistic_society` / `labor_standards_Act_idea`→`_12_hour_workday` / `poverty_level_idea`→**`Working_poor`** / `female_military_service_laws`→`Prohibited_military_service` / `military_training_laws`→`Basic_military_training`。ENGは同グループを明示しており（`Women_s_suffrage` / `_10_hour_workday` / **`Stable_employment`** / `Limited_assistance_missions`）、GERとの差が意図的かどうか要確認。**本タスクの scope（徴兵法・経済法・貿易法）外のため未着手**
- FRA・ITA・JAP も三法すべて既定値のまま。GERだけ引き上げたことで相対的に FRA が弱くなる可能性がある（§2 の通し走行で開戦時師団数を確認のこと）
- NFの `load_oob` による直接軍拡（歩兵+8／騎兵+4／予備役+12。09 §7-2）は据え置き。開戦時師団数が目安（70〜90）を上回った場合は、まず `VF_GER_base_buildup_strategy` の値を戻す/削るのが唯一のノブ（同ファイルにコメント済み）

### 5-3-2. AI師団設計図の欠落【本セッションで追加発見・修正】

主宰の実機観察「大国が師団編成を持っていない」を受けて `common/ai_templates/` を調査した結果、
**これが大国AIが軍拡しない主因**であることが判明した。

**何が起きていたか**

- このModの `common/ai_templates/` には **`generic.txt` 1本しか無い**
- その `generic.txt`（バニラ由来）は全6グループで **`blocked_for = { GER FRA ITA RUS }`** を指定している
  （バニラでは各国専用の ai_templates ファイルが別に存在するため。このModにはそれが無い）
- 結果、**GER・FRA・ITA・RUS は infantry / armor / mountaineer / marine のどの役割の設計図も持たない**。
  AIは「何を作ればよいか」を決められず、師団を設計・更新・生産できない
- ENG・USA・JAP は `blocked_for` に含まれないため generic を使えている（大国間で挙動が割れていた説明がつく）

これは 09 §7 の原因分析（①徴兵法なし ②AI戦略なし ③軍事NFが骨のみ）に**挙がっていなかった第4の原因**であり、
設計図が無い以上、`_vf_GreatPowers.txt` の `force_build_armies` / `ai_wanted_divisions_factor` / `role_ratio` は
**すべて空振りしていた**ことになる。

**対応**: `common/ai_templates/_vf_GreatPowers.txt` を新設し、4か国共通の仮設計図を与えた。

| グループ | role | 対象 | 設計 |
|---|---|---|---|
| `vf_major_line_infantry` | `infantry` | GER/FRA/ITA/RUS | `vf_major_infantry_early`（歩兵9＋工兵・砲兵支援。開始時OOBに近い形）→ 軍需工場18超で `vf_major_infantry_upgraded`（歩兵9＋砲兵大隊1、支援に偵察追加）へ移行。加えて優先度0の認識用エントリ `vf_major_cavalry_legacy`（騎兵4）で、開始時の騎兵旅団を歩兵線の一部としてAIに認識させる |
| `vf_major_line_armor` | `armor` | GER/FRA/ITA/RUS | `vf_major_light_armor`（軽戦車6＋自動車化4）→ 中戦車技術の取得で `vf_major_medium_armor` へ |
| `vf_major_line_mountaineer` | `mountaineer` | GER/ITA | 山岳兵6＋工兵・偵察支援 |

**設計上の配慮**

- `early` は各国の開始時OOB（`history/units/*_1925.txt`）の編成に近づけてある。開幕から大規模な再設計が走って陸軍XPを浪費するのを防ぐため
- `role` トークンは `generic.txt` に実在するもの（`infantry` / `armor` / `mountaineer`）のみを使用。国指定は `available_for`（`common/ai_equipment/` に前例あり）
- `generic.txt` は**書き換えていない**。4か国は自前の設計図を持つようになったので `blocked_for` の指定は正しいまま

**報告事項（未対応）**

- `generic.txt` の `cavalry_generic` と `motorized_generic` は**どちらも `role = marine`** になっており、`marine_generic` と3つ巴で衝突している（バニラ由来のコピペ誤りと思われる）。ENG・USA・JAP等の generic 利用国に影響するが、`role = cavalry` / `role = motorized` が ai_templates の有効トークンか実機で確認できないため**触っていない**
- `_vf_GreatPowers.txt`（ai_strategy）の `role_ratio id = artillery` は、ai_templates 側に対応する role が無い。バニラの `doctrines.txt` でも使われている記法なので残してあるが、実効があるか要確認
- 本ファイルは**4か国共通の仮設計図**である。国ごとの作り分け（GER=攻勢型／FRA=縦深防御・砲兵／RUS=安価な大量編成／ITA=山岳・軽師団）はファイル末尾に `TODO(VF)` として残した

### 5-3-3. 実機確認の結果と積み残し（2026-08-28 主宰走行）

§1（開始時法）＋ §5-3-2（AI師団設計図）の適用後に主宰が走行。**大国AIの軍拡は解消**した。

| 項目 | 結果 |
|---|---|
| 開戦時の師団数 | **大幅に増加**。`ai_templates` の欠落が主因だったことが裏付けられた |
| `vf_greatwar_started`（大戦の勃発） | 発生を確認 |

**積み残し（主宰裁定により後回し。本タスクでは着手しない）**

| # | 内容 | 現時点の見立て |
|---|---|---|
| A | **師団数が今度は多すぎる恐れ**。上振れの調整余地を残しておく | 絞る順序の推奨: ①`_vf_GreatPowers.txt` の `VF_GER_base_buildup_strategy` の `ai_wanted_divisions_factor`（現在50。§5-3-1で100から半減済み）→ ②各段階の `force_build_armies` → ③`ai_templates` の `vf_major_infantry_upgraded` の軍需工場しきい値（現在18）を上げて安価な編成に留める。**開始時法（§1）とAI設計図（§5-3-2）は戻さないこと** — どちらも「無いのが異常だった」ものの修正であり、軍拡の量を決めるノブではない |
| B | **露仏がNFを持たないため早期に降伏する** | 08 §3「やらないこと」で **FRA・RUSのミニツリーはβスコープ外**と決めていた（`vf_greatwar.6` の `add_to_war` が開戦導線を代替するため `planning/02` §3 から降格）。開戦導線としては足りていたが、**開戦後の持久力**という別の要求が顕在化した形。対応の選択肢は ①露仏に軍事・産業の最小NFを与える ②NFを作らずAI戦略と history（法律・OOB・研究）だけで底上げする ③降伏しやすさ自体を許容し大戦の長さを別の手段で担保する。**要裁定** |

### 5-4. §2 通し走行の結果

| 確認項目 | `06`/`07` 時点 | 今回 | 差分の有無 |
|---|---|---|---|
| バルカン戦争の開戦 | 1927年前半 | | |
| `vf_ended_balkan_war` | 1928年中 | | |
| 講和 tier | | | |
| `event_SER_pol.9` の発火 | 発火 | | |
| アルバニア戦の終結 | 120日以内 | | |
| `vf_greatwar_started` | 1929年秋 | | |
| 開戦時師団数（GER/RUS/FRA/ENG/SER） | — | | |

### 5-5. 静的監査の結果（2026-08-28。T-GER-14 / T-GER-5 の机上分）

実機の `error.log` を見る前に、リポジトリ内で完結する参照整合性をスクリプトで総当たりした。
対象: GER関連の全ファイル（NF・イベント・精神・ディシジョン・scripted_*・characters・history・ai_strategy・ai_templates）。

#### 5-5-1. 欠落ローカライズ（T-GER-14の一部）

| 検査 | 対象数 | 欠落 |
|---|---|---|
| NF名・NF desc | 99本×2 | **0** |
| イベントのtitle/desc/選択肢名 | 27本分 | **0** |
| 国民精神の名前・desc | 38本×2 | **0** |
| ディシジョン・カテゴリの名前・desc | 全件 | **0** |
| `custom_trigger_tooltip` のツールチップキー | 全件 | **0** |
| コスメティックタグ（`GER_federal_empire`） | 1件 | **0** |

定義済みローカライズキー5015件に対して、GER側から参照される399キーはすべて解決した。**欠落ゼロ**。

#### 5-5-2. 未定義ID参照（T-GER-14の一部）

NF参照（`prerequisite` / `relative_position_id` / `has_completed_focus`）・イベントID・国民精神・
scripted_effect / scripted_trigger の呼び出し・character・advisor・`load_oob`・GFXスプライト・
decision category を突き合わせ、**未定義参照は0件**。検出された11件はすべて監査スクリプト側の誤検出だった
（バニラのキーワード `fire_only_once` / `is_triggered_only` / `elections_allowed` / `promote_leader` / 
`abort_when_not_enabled` / `exists` を `scripted_effect = yes` と誤認、バニラスプライト `GFX_goal_unknown`、
顧問トークン `vf_GER_pm_prinz_max` を精神として誤認）。

#### 5-5-3. NFツリーの座標

99本すべての `relative_position_id` を再帰的に解決して絶対座標を算出。**重なりは0箇所**。
座標を解決できなかったNFも無し（親子参照に循環・欠落なし）。

#### 5-5-4. イベントの発火経路

| 発火方式 | 本数 | 状態 |
|---|---|---|
| `is_triggered_only`（明示発火が必要） | 9本 | **全本に発火元あり**（NF・ディシジョン・他イベント） |
| `trigger` ＋ `fire_only_once`（自動評価） | 14本 | 正常 |

> **監査時の誤判定と訂正**: 当初「14本が孤立」と判定したが、これは誤り。
> `trigger` ＋ `fire_only_once`（MTTHなし・`is_triggered_only` なし）は、
> 06/07 で実機確認済みの `event_SER_pol.9` / `.10` / `vf_greatwar.20` / `.21` と**同一の方式**であり、
> このModで実際に発火することが確認されている。GER側の14本も同じ書式なので問題ない。

#### 5-5-5. フラグ・変数の整合

`vf_` 接頭辞のフラグ・変数について、立てる側と読む側を全ファイルで突き合わせた。

- **読まれているが立てていない変数**: 0件
- **読まれているが立てていないフラグ**: 8件。内訳と判定:
  - `vf_GER_route_ausgleich` / `vf_GER_route_civilwar` … 08 §10 で**β未使用の受け口**と明記済み。**設計どおり**
  - `vf_ITA_grudge_SER` / `vf_ITA_regime_fascist` / `vf_OTT_alignment_fra` / `_ger` / `vf_POL_tilt_fra` / `_ger` … 06 §幕間の危機イベント3件（ローマ進軍・波立危機・オスマン危機）が立てる想定。08 §3「やらないこと」で**βスコープ外**。`vf_greatwar.10` 側に受け口だけある状態で**設計どおり**
- **立てているが読んでいないフラグ**: 21件。うち非対称に見えた3組を個別に追跡した結果、**すべて設計どおり**だった:
  - `vf_GER_balkan_restrain` … `event_GER_pol.19`（バルカンの砲声）の `ELSE` 分岐が拾っている。フラグ名での明示参照が不要なだけ
  - `vf_IST_leaning_ita` … `vf_greatwar.10` は `_ger` のみ読み、`# ELSE: 既定はIST中立` としている。ITAが天秤（無所属）のβでは中立が正しい帰結。**ITAが参戦する本リリースでは分岐の追加が要る**（要記録）
  - 残りは `vf_GER_crownland_*` / `vf_GER_istria_*`（4択の記録）、`vf_GER_communist_spark`（08 §10 で死にフラグと明記）、`vf_GER_constitution_suspended` / `vf_GER_bohemia_loyalty`（戦後・ボヘミア content の受け口）など、いずれも08 §10 の契約どおり

#### 5-5-6. T-GER-5 国民精神の置換チェーン（机上検証）

| 置換 | 実装 | 前提の担保 |
|---|---|---|
| 1928年改革が3種を吸収 | NF「大改革宣言」が `idea_GER_path_to_liberalism` / `_strengthened_cabinet` / `_parliamentary_sovereignty` を remove し `idea_GER_1928_reforms` を add | 3種はいずれも「大改革宣言」より前のNFが付与する |
| 1929年憲法が1928年改革を置換 | NF「憲法改正」が `idea_GER_1928_reforms` と `idea_GER_absent_privy_council` を remove し `idea_GER_1929_constitution` を add | 「憲法改正」は「枢密院廃止」＋「二元君主の明文化」＋「連合強化」が前提。「枢密院廃止」の前提が「大改革宣言」なので**両方の精神の存在が構造的に保証される** |
| 「枢密院の不在」の除去 | 同上（憲法改正で remove） | 「枢密院廃止」が付与し「憲法改正」が除去。前提関係で担保 |
| 「自由主義の内閣」 | `event_GER_pol.2` 選択肢1の **730日 `add_timed_idea`**。吸収対象ではなく自然消滅 | 08 §6-2 の「2年限定」と一致 |
| 「未解決の遺産」の除去 | ディシジョン「帝冠領整理の完遂」が `has_idea` を確認してから remove | `event_GER_pol.4` 選択肢1が付与 |
| 「失業保険制度」→「社会国家ドイツ」 | NF「エーベルト・プラン」系で remove→add | |
| 「城内平和」＋路線精神 →「総力戦体制の完成」 | 戦時NFで3種 remove→add | |
| オストヴァル→東西の防壁→絶対的防御 | 軍事NFで3段の remove→add | |

**机上では全チェーンが正しい。** 残るのは実機での目視確認（精神欄に重複や取り残しが出ないか）。

#### 5-5-7. 静的監査で潰せなかった残り

- **実機 `error.log` の確認**（T-GER-14の本体）。静的監査は「参照の解決」までで、
  バニラ側の定義漏れ・スクリプトの構文エラー・実行時の scope 違反は検出できない
- T-GER-12（可変コストの再計算）、T-GER-4（選挙の重心3種）、T-GER-13（バルカン砲声・講和の発火）、
  T-GER-10 / 11 / 2 / 3 は**いずれも実機走行が必要**

### 5-6. T-GER-14 実機 error.log の確認結果（2026-08-28）

主宰提供の `logs/error.log`（3548行、1925.3.1〜1930.1 の走行分）を全件分類した。

#### 5-6-1. 本タスク（GER議会ルート）由来 — 2件。**いずれも修正済み**

**① `load_oob` の師団テンプレートが解決できず、騎兵4個師団が1個も生成されていなかった**

```
[1930.01.22][persistent.cpp:67]  Malformed token: Kavallerie-Brigade ... history/units/GER_mil_cavalry.txt
[1930.01.22][country.cpp:1301]   Invalid division at line 5/12/19/26
[1930.01.22][unit.cpp:3475]      Kavallerie-Brigade ( GER ) unit in 6334 has no division template set
```

原因: `GER_mil_cavalry.txt` は `GER_1925.txt` で定義された `"Kavallerie-Brigade"` を**名前で参照するだけ**で、
テンプレート定義を同梱していなかった。`load_oob` 実行時に名前を解決できず、師団が生成されない。
動作しているSER側のOOB（`history/units/SER_mountain.txt`）はテンプレートを同梱している。

引き金は §5-3-2 の `ai_templates` 追加と見られる。AIが師団設計を管理するようになった結果、
使われなくなった騎兵テンプレートが失われた。**ただし元々が壊れやすい書き方**であり、
`GER_mil_infantry.txt` / `GER_mil_reserves.txt` も同じ構造だった（当該走行ではNF未取得のためログに出ていないだけ）。

| ファイル | 対応 |
|---|---|
| `history/units/GER_mil_cavalry.txt` | `"Kavallerie-Brigade"`（騎兵4＋偵察・砲兵支援）の定義を同梱 |
| `history/units/GER_mil_infantry.txt` | `"Infanterie-Division"`（歩兵9＋工兵・砲兵支援）の定義を同梱 |
| `history/units/GER_mil_reserves.txt` | **専用の `"Reserve-Division"`（歩兵9＋工兵のみ、`priority = 0`）を新設**して使用。本NFは開戦後に発火するため、主力テンプレートを1925年仕様で上書きすると、AIが `ai_templates` で積み上げた改良（軍需工場18超での砲兵大隊追加など）を戦時に剥がしてしまう。予備役は装備・練度が劣るという設定にも合う |

**② 国民精神「勢力均衡」の desc が複数行になっていて読み込めていなかった**

```
[no_game_date][pdx_localize.cpp:1091]  Invalid key name at line 5 and column 1
                                       in localisation/japanese/VF/common/ideas/ideas_GER_l_japanese.yml
```

`idea_GER_power_balance_desc` の値が引用符の内側で改行しており（4行目で閉じず5行目で閉じる）、
HOI4のローカライズは複数行の値を許さないため5行目がキー名として解釈されて弾かれていた。
**枢密院の傾き表示（`[GER.VfGerPrivyTilt]`）が出ていなかったはず**。改行を `
` に置換して1行に統合した。

> **§5-5-1 の静的監査がこれを見逃した理由**: キー定義の検出は行頭の `キー名:` にマッチさせていたため、
> 4行目は「定義あり」と判定されてしまう。**全localisationについて行内の引用符の対応を検査する**チェックを追加し、
> 同種の混入が他に無いことを確認した（86ファイル中、該当はこの1件のみ）。

#### 5-6-2. 他タスク由来のVF製ファイル — 3件。**報告のみ（触っていない）**

| # | 内容 | 担当 |
|---|---|---|
| 1 | `history/units/SER_houhei.txt:14` — `Subunit is of support type: artillery`。`regiments` の中に支援型の `artillery` を置いている（正しくは `artillery_brigade`）。**テンプレート「Millita9a」が壊れている**。加えてこのファイルには `units = {}` ブロックが無く、テンプレート定義だけで師団を生成していない | 06/07（SER）。§2-3「SER側を書き換えないこと」に従い未着手。バルカン戦争の戦力比に直結するため要判断 |
| 2 | `events/_vf_events_greatwar.txt:242` — `SER already at war with CRO`。`vf_greatwar.6` の `declare_war_on` が二重に走っている。既に戦争状態なので**実害は無い**がログが汚れる | 06/07（大戦導線） |
| 3 | `common/national_focus/_vf_focus_ITA.txt:78` — `Missing icon shine for focus: focus_ITA_pol_dem_facta_regime_strict_guard`。アイコンに対応する `_shine` スプライトが無い。表示上の軽微な問題 | ITA担当 |

GER側のNFアイコンは全て `GFX_goal_unknown` のため、shine関連のエラーは1件も出ていない。

#### 5-6-3. 本タスク以外・Mod全体の既存エラー（参考。**未着手**）

件数の大半はGUI・マップ・バニラ由来で、GER議会ルートとは無関係。次の担当者向けに分類だけ残す。

| 件数 | 分類 | 代表例 |
|---:|---|---|
| 1772 | GUI定義の参照切れ | `interface/mapicons.gui`: `active_abilities` が `unit_counter` に無い（973件）／`interface/nationalfocusview.gui`: `overlay` が `national_focus_item` に無い（543件） |
| 1196 | エンジンのコマンドドロップ | `Dropped command: order_delete_command`（1148件）。ほぼ無害なノイズ |
| 149 | バニラ特性の参照切れ | `common/unit_leader/00_traits.txt`: `SOV_purged_junior_navy_officers_3 is not a valid Idea`（SOVタグを廃したこのModでは必ず出る） |
| 101 | タグ未定義 | `XSM` / `NXM` / `KUM` が tag list に無い |
| 87＋11 | マップデータ | 1ピクセル州、州のバウンディングボックス過大、`Map invalid X crossing` |
| 66 | 国データの不整合 | `IMP` / `IRJ` / `NTC` が history ファイル欠落。`AUS` / `CTB` / `MAP` は history はあるが country database に無い。`NTC` / `IRJ` は首都未定義 |
| 12＋8 | history/state の重複定義 | 同一州に複数の `buildings` ブロック、非保有州への建物指定 |
| 3 | **法律トークンの綴り誤り** | `history/countries/CAN`・`NZL`: `add_ideas: Invalid idea: 10_hour_workday` → 正しくは **`_10_hour_workday`**（先頭アンダースコア）。`history/countries/IST:199`: `Government_of_the_International_Control_Area` は実在しない精神。**IST は大戦導線に関わるため優先度は中** |
| 5 | バニラDLC関連 | `add_temporary_buff_to_units` 不明効果、`hq_*` サブユニットのアビリティ欠落 |

**T-GER-14 の判定**: 本タスク由来の未定義ID・欠落ローカライズは**2件**で、いずれもこのセッションで修正した。
次の走行で `GER_mil_cavalry.txt` / `ideas_GER_l_japanese.yml` に関するエラーが消えていることを確認すれば完了とする。

### 5-7. error.log の一掃（2026-08-28。GER追補のスコープ外を含む）

主宰の指示により、§5-6 で分類したエラーのうち**Mod自作コンテンツ由来で低リスクなもの**を修正した。
**削減見込み 191行 / 3548行**（GER議会ルート由来の14行を含む）。

#### 5-7-1. 修正した内容

| # | 対象 | 内容 | 削減 |
|---|---|---|---:|
| 1 | `common/unit_leader/00_traits.txt` | `SOV_purged_junior_navy_officers_3` を参照する `modifier` ブロック13箇所を無効化。このModはSOVタグを廃しており当該精神が存在しない。周囲に既存のコメントアウト済みブロックがあるため同じ書式に合わせた | **148行** |
| 2 | `common/ai_faction_theaters/ai_faction_theaters.txt` | `middle_east` / `persia` / `northern_india` の `regions` に、このModの地図に存在しないリージョン **296 / 297 / 298**（最大294）が5件あったので無効化 | 3行 |
| 3 | `history/states/` 3ファイル | 同一 `buildings` ブロック内で同じ province を2度指定しており、**後のブロックが前を上書きして建物が消えていた**。1ブロックに統合して復元: `681`（Cape 12589 の軍港4）／`518`（Hobart 5187 の軍港2）／**`763` ケーニヒスベルク 6332 のトーチカ**（GER領） | 3行 |
| 4 | `history/states/` 5ファイル | 州の切り直しで所有から外れた province への建物指定。**エンジンに無視されていた**ため挙動を変えずに無効化 | 5行 |
| 5 | `history/countries/IMP - Bhopal.txt` ほか2件 | `common/country_tags/05_South_Asia.txt` でタグは定義済みなのに history ファイルが無く、**首都未定義**でAIが機能しない状態だった。近隣国 `KAS - Kashmir.txt` の構成を踏襲した最小構成を新規作成（IMP=州437／IRJ=州433／NTC=州423。いずれも保有州のうち勝利点・インフラが上位のものを採用、`TODO(VF)` 付き） | 9行 |
| 6 | `history/countries/CAN`・`NZL` | `10_hour_workday` → **`_10_hour_workday`**（先頭アンダースコアの綴り誤り） | 2行 |
| 7 | `history/countries/IST - Istria.txt` | 未定義の `Government_of_the_International_Control_Area` を、実在する `Constitution_not_yet_enacted` に差し替え（`constitution_idea` グループの欠落。イストリアは国際共同管理下で独自憲法を持たない） | 1行 |
| 8 | `interface/_VF/goals/goals_ita_shine.gfx` | スプライト名が `..._strict_guard` になっていて **`_shine` 接尾辞が欠落**。`goals_ita.gfx` と名前が重複してもいた。`..._strict_guard_shine` に修正。同種の欠落が他に無いことも全 `*shine*.gfx` で確認済み | 1行 |
| 9 | `events/_vf_events_greatwar.txt` | `vf_greatwar.6` は `.5` から `days = 14` で遅延発火するため、その間にSERのAIが自力でCROへ宣戦していることがある。`has_war_with` で確認してからの宣戦に変更（**挙動は不変**。どちらの経路でも戦争は成立している） | 2行 |
| 10 | `history/units/GER_mil_*.txt` | §5-6-1 で修正済み（テンプレート同梱） | 12行 |
| 11 | `localisation/.../ideas_GER_l_japanese.yml` | §5-6-1 で修正済み（複数行 loc） | 1行 |

**#4 で無効化した5件の内訳**（地図担当者への申し送り）。移設先の所有国が変わるものがあるため、
**軍港を勝手に移設していない**。現在の挙動（軍港なし）と一致させただけである。

| 元の州 | 元の所有国 | province | 現在の所属州 | 現在の所有国 | 失われている建物 |
|---|---|---|---|---|---|
| 559 Somaliland | SOM | 12991 | 1022 Geledi | SOM | 軍港2 |
| 286 Indochina | DNA | 4401 | 1013 Cochinchina | DNA | **なし**（移設先に同一の `naval_base = 4` が既にある＝純粋な重複） |
| 719 Natal | SAF | 4696 | 681 Soviet Lakes | CAP | 軍港2 |
| 766 Southern Bessarabia | ROM | 6727 | 78 Bessarabia | **RUS** | 軍港3 ※移設すると**露が軍港を得る**。要判断 |
| 157 Abruzzo | ITA | 925 | 990 Marche | ITA | 軍港4 |

（`157-Abruzzo.txt` は `victory_points = { 925 1 }` も同じく非保有 province を指しているが、エラーにはなっていないため触っていない）

#### 5-7-2. 手を付けなかったもの と その理由

| 件数 | 対象 | 理由 |
|---:|---|---|
| 1772 | GUI定義の参照切れ（`interface/mapicons.gui` の `active_abilities` 973件、`interface/nationalfocusview.gui` の `overlay` 543件 ほか） | Modが取り込んだ `.gui` に、現行ゲームバージョンが要求する子要素が無い。**バニラの参照ファイルがこの環境に無く**（ゲーム本体のインストール先を特定できなかった）、正しい定義を復元できない。推測で編集するとUIが壊れるため未着手 |
| 1196＋65 | `session.cpp: Dropped command` / `gameidler.cpp: AI tried to post an invalid command` | エンジン内部のノイズ。スクリプトからは制御できない |
| 101 | 未定義タグ（84種。`SOV` / `YUG` / `TUR` / `CZE` ほか） | このModが `common/country_tags` から削除したバニラのタグを、Mod側で上書きしていないバニラファイルが参照している。タグを足すと幽霊国家が生まれるため不可。潰すには参照元のバニラファイルを全て上書きする必要があり、費用対効果が見合わない |
| 98 | マップデータ（1ピクセル州、州のバウンディングボックス過大、`Map invalid X crossing`） | `provinces.bmp` の画像編集が必要。スクリプトでは直せない |
| 5 | `common/abilities/generic_leader_abilities.txt` の `add_temporary_buff_to_units` | 効果自体が現行バージョンで未知と判定されており、当該アビリティは既に無効。コメントアウトしても挙動は変わらないが、**ゲーム本体を更新した際に永久に動かなくなる**ため、あえて残した |
| 4 | フォント・テクスチャ（`hoi_30.tga` が MAX_TEXTURE_SIZE 超過ほか） | 画像アセットの差し替えが必要 |
| 1 | `history/units/SER_houhei.txt` の `Subunit is of support type: artillery` | **要裁定**。§5-7-3 参照 |
| 3 | 孤立した history ファイル（`AUS - Australia.txt` / `CTB - ...` / `MAP - Mapuchenia.txt`） | **要裁定**。§5-7-3 参照 |

#### 5-7-3. 主宰裁定を受けて追加で修正した2件（2026-08-28）

**(a) `history/units/SER_houhei.txt` — 裁定: 砲兵を削る**

`regiments` に支援型の `artillery` を2つ置いていたため、テンプレート「Millita9a」は
歩兵9＋砲兵2のつもりで**実際には歩兵9のみとして生成されていた**（エンジンが2行を無視）。
`artillery_brigade` へ直すと設計意図どおりになるが、バルカン戦争（1927）のセルビア側戦力が上がり
`06`/`07` で実機確認済みの講和 tier が動くため、**現在の実挙動に合わせて砲兵2行を削除**した。
つまり**ゲーム内の戦力は一切変わらず、ログ1行だけが消える**。経緯はファイル冒頭のコメントに残した。

> **未対応として残した点**: このファイルには `units = {}` ブロックが無く、テンプレートを定義するだけで
> 師団を1個も生成していない。読み込み元の NF `focus_SER_eco_source_from_black_market` は
> 装備の備蓄付与（歩兵装備1万・砲兵装備5千・列車30）と併せて `load_oob` を呼んでおり、
> 師団の追加を意図していた可能性がある。師団を足すとSER側の戦力が増えるため触っていない（**要判断**）。

**(b) 孤立した history ファイル3件 — 裁定: 削除**

削除前に、3タグとも **`common/country_tags` に定義なし・保有州ゼロ・`common/` と `events/` からの参照ゼロ**
であることを再確認した（オーストラリアはこのModでは `AST` を使用）。git 追跡下のファイルなので復元可能。

| 削除したファイル | 確認結果 |
|---|---|
| `history/countries/AUS - Australia.txt` | タグ未定義・保有州0・参照0 |
| `history/countries/CTB - Chief_Commissioner_s_Territory_of_Baluchistan.txt` | 同上 |
| `history/countries/MAP - Mapuchenia.txt` | 同上 |

#### 5-7-4. 次の走行で確認すること

`error.log` から以下が消えていること。残っていれば原因が別にある:

- `Malformed token: Kavallerie-Brigade` / `has no division template set`（GER騎兵）
- `Invalid key name at line 5 ... ideas_GER_l_japanese.yml`
- `SOV_purged_junior_navy_officers_3 is not a valid Idea`（148行）
- `region list contains invalid entries`（3件）
- `Province buildings being overridden` / `Trying to set province building in state that doesn't own it`
- `IMP / IRJ / NTC is missing a history file` / `has NO capital defined`
- `Unknown history file in country database`（AUS / CTB / MAP）
- `Invalid idea: 10_hour_workday` / `Government_of_the_International_Control_Area`
- `Missing icon shine for focus: focus_ITA_pol_dem_facta_regime_strict_guard`
- `SER already at war with CRO`
- `Subunit is of support type: artillery`（SER_houhei）

あわせて **GERの騎兵4個師団が実際に増えているか**（NF「騎兵強化」の完了後）と、
**国民精神「勢力均衡」のツールチップに枢密院の傾きが表示されているか**を目視で確認すること。

### 5-8. 実機再走行での検証と、第2波の一掃（2026-08-28）

#### 5-8-1. 検証結果 — **T-GER-14 合格**

主宰の再走行により、§5-6 / §5-7 で修正した**14分類すべてが `error.log` から消滅**した。
ログは **3548行 → 863行**。あわせて実機で以下を目視確認済み:

| 確認項目 | 結果 |
|---|---|
| NF「騎兵強化」で騎兵師団が増えるか | **OK**（テンプレート同梱の修正が効いている） |
| 国民精神「勢力均衡」に枢密院の傾きが表示されるか | **OK**（複数行 loc の修正が効いている） |
| VF製ファイルに由来する新規エラー | **0件**（リグレッションなし） |

> 注記: この走行はゲーム内 1925.03.11 までのため、ロード時エラーの解消は確定。
> 中盤に出る `Kavallerie-Brigade`（1930年）と `already at war with CRO`（1929年）は
> ログ上では未到達だが、前者は上表のとおり実機で師団増加を確認済み、
> 後者は `has_war_with` による防御的なガードなので退行しない。

#### 5-8-2. 残り863行を再分類して追加修正した2件

**① 55か国が首都を保有していなかった（`country.cpp:7132`）— 修正済み**

```
Attempting to set capital state #797 for <国名>, they dont own it!
```

**51か国が `capital = 797`（OTT領のカシミール近辺）のまま**という、history ファイルのコピー由来の不具合。
加えて ACR（州2＝ローマ）・HIN（州43＝ハンガリー）・HUN（州716）・NET（州391）も他国領を指していた。
**首都が無いとAIが機能せず、降伏判定も正しく働かない**ため、影響は大きい。
とくに **HUN はバルカン戦争の当事国**であり、`event_SER_pol.9`（HUN離脱）の挙動に関わる。

各国の保有州のうち**勝利点→インフラ→州ID順で最上位**のものを機械的に採用し、55か国を修正した。
各ファイルの先頭に経緯と `TODO(VF): 各地域の担当者は本来の首都に差し替えること` を記載している。

主なもの: HUN→43ハンガリー / NET→7ホラント / MEX→277メキシコ / QIN→608北京 / MUG→439デリー /
POR→112リスボン / SAF→275南アフリカ / CHL→279チリ / HIN→429ムンバイ / NOR→110ノルウェー。

**保有州がゼロの9か国**（BRU / CAM / CHA / LUA / MAF / RHO / SAR / TST / YEM）は見送った。
領土を1つも持たないため、**どの州を首都にしてもこのエラーは消えない**。
ただし解放時に備えるなら、コア／請求権を持つ州を首都にしておくのが妥当:
CAM→741 / CHA→1014 / LUA→1015（いずれも現在THA領）、MAF→858 / YEM→906（現ENG領）、RHO→985（現KOP領）。
BRU・SAR・TST はコアも請求権も無く、首都を決める手がかりが無い。

**② PER（イラン）の動的トークン3件が未登録（`scopedvariable.cpp:551`）— 修正済み**

`PER_Shh` / `PER_Prime_Minister` / `PER_Ahmad_Shan` が `common/synchronized_dynamic_tokens/_vf_tokens.txt` に無く、
**マルチプレイでOOSを起こす恐れ**があると警告されていた。他国（GER_Geiser 等）と同じ形式で登録した。

#### 5-8-3. 残るエラーと、手を付けない理由（最終）

| 件数 | 対象 | 理由 |
|---:|---|---|
| 554 | GUI定義の参照切れ（`interface/mapicons.gui` ほか） | **バニラの参照ファイルがこの環境に無い**。ゲーム本体（`Hearts of Iron IV` フォルダ）のパスが分かれば突き合わせて修正可能 |
| 98 | 未定義タグ（`SOV` / `YUG` ほか84種） | Modが `common/country_tags` から削除したバニラタグを、上書きしていないバニラファイルが参照している。タグを足すと幽霊国家が生まれる |
| 87＋11 | マップデータ（1ピクセル州・バウンディングボックス過大・`Map invalid X crossing`） | `provinces.bmp` の画像編集が必要 |
| 16 | 国旗の欠落（**IMP・IRJ・KOR**）＋ `BUK_communism.tga` の形式不正（32bpp非圧縮パレット無しが必要） | 画像アセットの作成が必要。ゲーム内でも旗が表示されないため**要対応**（美術担当） |
| 5 | `common/abilities/generic_leader_abilities.txt` の `add_temporary_buff_to_units` | 効果が現行バージョンで未知＝アビリティは既に無効。消しても挙動は変わらないが、本体更新時に永久に動かなくなるため残置 |
| 4 | `common/units/` の `critical_parts` / `motorbike_equipment` | 同上（Modのファイルが本体より新しいバージョン由来） |
| 4＋2 | フォント・テクスチャ（`hoi_30.tga` が MAX_TEXTURE_SIZE 超過ほか） | 画像アセットの差し替えが必要 |
| 3 | `special_forces_tracks.txt` / `infantry_subdoctrines.txt` | **バニラ側のファイル**（Mod内に存在しない）。バニラがこのModで廃した focus `INS_underground_revolution` を参照している |
| 5 | `ability_database.cpp` の `hq_*` サブユニット | 同上（バニラ由来） |

#### 5-8-4. 累計

| | 内容 |
|---|---|
| 修正した分類 | **16分類**（GER議会ルート由来2、Mod全体14） |
| 削減した行 | **約250行**（148＋55＋12＋9＋8＋6＋5＋3＋3＋2＋1×5 ほか） |
| 復元した実データ | ケーニヒスベルクのトーチカ・Capeの軍港・Hobartの軍港、GER騎兵4個師団、勢力均衡の枢密院表示、55か国の首都 |
| 新規作成 | `common/ai_templates/_vf_GreatPowers.txt`、`history/countries/` の IMP・IRJ・NTC |
| 削除 | 孤立 history 3件（AUS・CTB・MAP） |

### 5-9. 本体との突き合わせによる第3波（2026-08-28）

主宰からゲーム本体のパス（`D:\SteamLibrary\steamapps\common\Hearts of Iron IV`、**1.19.2.0 / 全DLC導入済み**）
の提供を受け、Modが上書きしているバニラ由来ファイルを1本ずつ突き合わせた。
§5-8-3 で「本体バージョン差だから触らない」と判断していたものが、**実際には旧コピーによる実害**だと判明した。

#### 5-9-1. GUI定義の参照切れ（3種・旧ログ1772行）— 修正済み

Modの `.gui` が旧バージョン由来で、本体1.19系が要求する要素を欠いていた。
Mod側には独自の追加（日本語コメント等）があるため上書きはせず、**該当ブロックのみ移植**した。

| ファイル | 追加した要素 | 備考 |
|---|---|---|
| `interface/mapicons.gui` | `gridBoxType "active_abilities"`（`unit_counter` 内） | 旧ログ973行。直下にある旧版の `iconType "active_ability"`（単数）は現行エンジンが参照しない名残 |
| `interface/mapicons.gui` | `iconType "dam_icon"`（`construction_info_window` 内） | 旧ログ256行 |
| `interface/nationalfocusview.gui` | `iconType "overlay"`（`national_focus_item` 内） | 旧ログ543行 |

#### 5-9-2. `common/abilities/generic_leader_abilities.txt` — 修正済み（**実害あり**）

差分を精査した結果、**Mod独自の追加・変更は皆無**で、単に旧バージョンのコピーだった（333行 vs 本体474行）。
放置していた場合の実害は2つ:

1. `force_attack` / `last_stand` が廃止記法 `one_time_effect { add_temporary_buff_to_units }` を使っており、
   **効果が一切適用されていなかった**（本体1.19.2 では `unit_modifiers = { ... }`）
2. 新しい5アビリティ（`extra_medics` / `deeper_dig_in` / `defense_in_depth` / `front_overrun` / `rotating_reserves`）が
   丸ごと欠落し、これらを解禁する `hq_*` サブユニットが参照できずにいた

本体1.19.2 の内容で置き換えた。**将軍の能力2つが復活し、司令部ユニットの5能力が使えるようになる。**

#### 5-9-3. `common/units/critical_parts/00_critical_parts.txt` — 修正済み（**実害あり**）

バニラの途中で切れた古いコピー（**3632 / 6949バイト**）で、潜水艦・空母用の critical part 定義が丸ごと欠落していた。
`common/units/carrier.txt` が参照する `damaged_flight_deck`、`submarine.txt` が参照する `leaking_pressure_hull` /
`battery_leak` / `jammed_torpedo` などが未定義で、**海戦のクリティカルヒット処理が壊れていた**。
Mod独自の変更は空白の差のみだったため本体の内容で置き換えた。

> なお `common/units/carrier.txt` と `submarine.txt` は**本体と完全に同一**で、上書きする意味が無い。
> Modに残しておく理由が無ければ削除してよい（次の本体更新で再び古くなる）。

#### 5-9-4. `common/units/equipment/motorized.txt` — 修正済み

旧バージョンのコピーで `motorbike_equipment` / `motorbike_equipment_1` の2アーキタイプと、
`motorized_equipment_1` の `parent = motorized_equipment_0` が欠落していた。
これを参照する `common/units/military_police.txt`（本体と同一）が読み込めず、憲兵ユニットが機能していなかった。
**Modの独自変更（`year = 1936` → `1900`。開始1925に合わせたもの）は保持**し、欠落分のみ移植した
（移植した `motorbike_equipment` の `year` も同じ方針で 1900 に揃えてある。本体は 1938）。

#### 5-9-5. 手を付けられないものの最終確認

| 件数 | 対象 | 本体と照合した結果 |
|---:|---|---|
| 98 | 未定義タグ84種（`SOV` / `YUG` / `TUR` / `CZE` ほか） | **バニラの455ファイル**がこれらを参照している。Mod側で全て上書きしない限り消えない。**対応不可能と結論** |
| 87＋11＋2 | マップデータ（1ピクセル州・バウンディングボックス過大・`Map invalid X crossing`・州13254の描画位置） | `provinces.bmp` の画像編集が必要 |
| 15 | **国旗の欠落: IMP・IRJ・KOR** | Modに `.tga` が存在しない。ゲーム内でも旗が出ない。**美術担当の対応が必要**（プレースホルダ生成も可能だが、いずれも実在の歴史的旗があるため単色置きは非推奨） |
| 1 | `gfx/flags/medium/BUK_communism.tga` の形式不正 | **バニラ側のファイル**（Modは `BUK.tga` しか持たない）。本体アセットの問題 |
| 4＋2 | 日本語フォント（`hoi_mapfont4_*.fnt` の lineHeight 不一致、`hoi_30.tga` / `hoi_33.tga` が MAX_TEXTURE_SIZE 超過） | Mod独自のフォントアセット。再生成が必要 |
| 3 | `special_forces_tracks.txt` / `infantry_subdoctrines.txt` | **バニラ側のファイル**（Mod内に存在しない）。バニラがこのModで廃した focus `INS_underground_revolution` を参照している |

#### 5-9-6. 本体版への置き換えで生じた退行と、その修正

§5-9-2 の置き換え後の走行で、**新たに27行のエラーが出た**。いずれも置き換えの副作用で、同セッション内で修正済み。

| 件数 | 内容 | 対応 |
|---:|---|---|
| 25 | `generic_leader_abilities.txt` が **CHI / JAP / SPA / SWE / PHI のバニラ国家方針**を参照しており、このModにそれらのNFが無いため `Invalid focus scripted in trigger` が出た（12参照×trigger/triggerimplementation） | 該当の `OWNER` ブロック3箇所を削除。すべて `NOT = { has_completed_focus = ... }` 形式で、参照先が永久に成立しない条件のため**挙動は変わらない** |
| 2 | `motorbike_equipment` / `_1` が `common/script_enums.txt` の `script_enum_equipment_bonus_type` に未登録（§5-9-4 の移植に伴うもの）。同ファイル内でコメントアウトされていた | コメントを外して有効化 |

#### 5-9-6. 全体の累計

| | 内容 |
|---|---|
| 修正した分類 | **23分類** |
| 削減した行 | **約3300行 / 3548行**（残 約233行）。GUI 1772・特性148・首都55 ほか |
| 復元した実データ | ケーニヒスベルクのトーチカ、Cape・ホバートの軍港、GER騎兵4個師団、勢力均衡の枢密院表示、55か国の首都、**将軍の能力 force_attack / last_stand**、**司令部の5能力**、**海戦のクリティカルヒット処理**、**憲兵ユニット** |
| 残るもの | 未定義タグ98（対応不可能）／マップ100（画像編集）／国旗16（美術）／フォント6（美術）／バニラ側3 |

---

## 6. 着手順チェックリスト

- [ ] `08`／`09` を読み、実装済みの範囲を把握
- [x] §3-2: `common/ideologies/00_ideologies.txt` を読み §5-1 を記入（2026-08-27 完了。7種・`democracy` 不在を確認）
- [x] §1: 各国 history の法律を調査し §5-3 を記入 → GERに開始時の法を追加（2026-08-27 完了）
- [x] §1-2: 軍事NFの付与する法と `_vf_GreatPowers.txt` のエスカレーション幅を見直し（2026-08-27 完了。§5-3-1 に記録）
- [x] §3-3: 「民主主義」参照3箇所の読み替え案を主宰へ上程 → 裁定後に実装、§5-2 を記入（2026-08-27 完了。裁定 = 案(b)。§3-4 も併せて処理）
- [ ] **§2: AI放置で1925→1930を通し走行し §5-4 を記入**
- [ ] §2-2: 差分があれば原因を切り分けて報告（**SER側スクリプトは書き換えない**）
- [x] §4: T-GER-14 → T-GER-5 → 以下優先度順にテスト消化（2026-08-28: **T-GER-14 合格**。静的監査=§5-5、error.log=§5-6〜§5-8。T-GER-5は机上検証済み。T-GER-12/4/13/10/11/2/3 は実機走行が未実施）
- [ ] 08 §10 のフラグ表に追加・変更があれば追記
- [ ] §5 の各表を記入済みの状態でこの追補を更新し、次セッションへ引き継ぐ
