# VF β実装報告書：セルビア開戦導線（バルカン戦争修正〜幕間枝〜世界大戦の発火）

> **この文書の位置づけ**
> 実装セッション（2026-08-26〜27）の成果報告。読み手は**前史・Mod計画を熟知しているが、実リポジトリの内部ファイルと実装の詳細を知らないAIエージェント**を想定する。
> したがって世界観・設定の説明は省き、「何がどのファイルでどう動くか」に絞って書く。
> 元指示書: `.doc/06_SER開戦導線_実装指示書.md`（§8のフラグ契約・§13/§14の監査表も実装セッションで記入済み。本書と併読のこと）

---

## 1. 結論サマリ

指示書のPhase 0〜3をすべて実装した。**開始1925年3月 → バルカン戦争（1927頃）→ 講和 → 幕間枝14NF → クロアチア危機（1929夏）→ 世界大戦発火**の一本道がスクリプト上つながっている。

実機確認の状況:

| 区間 | 状態 |
|---|---|
| 開始〜バルカン戦争講和（`vf_ended_balkan_war`） | **実機で完走確認済み**（主宰による走行。ALB戦泥沼化バグも修正・確認済み） |
| 幕間枝14NF・AI集結制御 | 実装済み。実機での目視確認は部分的 |
| クロアチア危機〜大戦発火（`vf_greatwar.*`） | 実装済み。**実機未検証**（T2/T8/T9/T10/T16 未実施） |
| 大戦中コンテンツ | **意図的に後回し**（主宰指示 2026-08-27）。終結処理はβ簡易版のみ |

---

## 2. リポジトリの実装規約（指示書と異なる点・暗黙の前提）

次のセッションが最初に踏む罠なので先に書く。

- **ファイル命名**: VF固有ファイルは `_vf_` 接頭辞。指示書の想定パス（`vf_focus_SER.txt` 等）とは異なる。例: `common/national_focus/_vf_focus_SER.txt`、`events/_vf_events_SER.txt`
- **ローカライズ**: `localisation/japanese/VF/` 以下に配置。**UTF-8 BOM必須**（BOM無しだとゲームが読まない。新規作成時は要注意）。日本語が第一言語で、英語locは未整備（IDE診断のCW100警告は既知・無視してよい）
- **コメント**: 全ファイル日本語コメント。新規・改修ファイルの冒頭には指示書§11-1の相互参照ヘッダを置いてある
- **トリガの罠**: Paradoxスクリプトでは同一ブロック内の複数トリガはAND。既存 `VF_balkan_strategy` はこの罠を踏んでいる（§8参照）
- **NFの `allow_branch`**: 幕間枝では**全14NFに個別に**付けてある（親だけに付けても子が隠れる保証がないため）

---

## 3. ファイルマップ

### 新規作成

| ファイル | 内容 |
|---|---|
| `events/_vf_events_greatwar.txt` | クロアチア危機〜開戦連鎖。namespace `vf_greatwar`（§5参照） |
| `common/autonomous_states/_vf_autonomy_crown_dominion.txt` | 自治レベル「自治領邦」`autonomy_vf_crown_dominion`。BOH・CRO専用（`allowed` で制限）。宗主の資源・工場アクセス、外交委任、参戦拒否不可、講和スコア全移譲、自治度可変 |
| `common/opinion_modifiers/_vf_opinion.txt` | 幕間枝#2/#4用の関係値モディファイア |
| `localisation/japanese/VF/events/events_greatwar_l_japanese.yml` | 大戦連鎖のloc（本文執筆済み） |
| `localisation/japanese/VF/events/events_HUN_l_japanese.yml` | `event_HUN_pol.1`（革命）のloc |
| `localisation/japanese/VF/common/autonomy_l_japanese.yml` | 自治領邦・自治度変動表示名 |
| `localisation/japanese/VF/common/opinion_l_japanese.yml` | 関係値モディファイア表示名 |

### 改修

| ファイル | 変更 |
|---|---|
| `events/_vf_events_SER.txt` | `.8`〜`.10` の不具合修正、`.11`（講和タイマー）`.12`（アルバニアの崩壊）新設（§4参照） |
| `common/national_focus/_vf_focus_SER.txt` | 幕間枝14NF追加、「アルバニアからの略奪」追加、「アルバニアの脅威認識」（コメントアウト）削除、「復讐の日」ガード追加、AI用フラグのhidden_effect 3箇所 |
| `common/ideas/_vf_ideas_SER.txt` | 新規idea 5本: `idea_SER_vienna_arms_limit` / `idea_SER_albania_pacification` / `idea_SER_pol_panslavic_cause` / `idea_SER_mil_general_staff_war_plan` / `idea_SER_pol_last_irredenta` |
| `common/ai_strategy/_vf_Balkan.txt` | 開戦前集結・戦中増援・攻勢強制の戦略7ブロック追加（§6参照） |
| `history/countries/GER - Germany.txt` | **英独同盟**（GER+ENG）を `create_faction` で新設 |
| `history/countries/FRA - France.txt` | **露仏協商**（FRA+RUS、盟主FRA）を新設 |
| `history/countries/CRO - Croatia.txt` / `BOH - Bohemia.txt` | `puppet` に加えて `set_autonomy = autonomy_vf_crown_dominion`（freedom_level 0.4） |
| `history/countries/SER - Serbia.txt` | 開始時国民精神に `idea_SER_vienna_arms_limit` を追加 |
| `localisation/japanese/VF/...`（SER系3ファイル） | 幕間枝NF・欠落していた既存イベント（`.5/.6/.8/.9/.10`）・新規イベントのloc追加 |
| `.doc/06_SER開戦導線_実装指示書.md` | §8フラグ表追記、§10裁定記録、§13/§14監査表を記入 |

---

## 4. バルカン戦争パート（`events/_vf_events_SER.txt`）の現在の挙動

- **`.8` 復讐の日**（NF `focus_SER_pol_day_of_revenge` から発火）: `vf_started_balkan_war` を立て、BULへ宣戦。SER陣営（救国同盟: SER+GRE+ROM）と**BUL陣営（バルカン協商: BUL+MNT+HUN）の双方を明示的に `add_to_war`** する。HUNの参戦を陣営の自動連鎖に任せると発火しないことがあるため（指示書の衝突3対策）。330日後に `.11` を予約
- **`.9` HUN離脱**: HUNが州82/83/84/764のうち2つ以上を失うと発火（従来どおり）。**BULの講和処理は削除し `.10` に一本化**（旧実装は `vf_ended_balkan_war` が立たない経路と領土二重移譲を持っていた）
- **`.10` 講和**: `tag = SER` ガードを追加（旧実装は全国で発火し得た）。日付ロック `1928.4.1` を廃止し、「開戦330日経過（`.11` が `vf_balkan_war_min_duration_passed` を立てる）＋BUL押され」または「BUL完全降伏」で発火。4段階の講和それぞれで **`vf_SER_peace_tier_1〜4`** を立てる（幕間枝が読む）
- **`.11`**: hidden。講和解禁タイマーの実体
- **`.7` アルバニア平定作戦 / `.12` アルバニアの崩壊**: ALB戦泥沼化バグの修正（実機で確認済み）。`.7` が対ALB限定時限バフ `idea_SER_albania_pacification`（対ALB攻防+50%、180日）と国家フラグ `vf_SER_albania_war` を付与し、`.12` が「ALBの `surrender_progress > 0.2`／首都陥落／**開戦120日経過**」のいずれかでALBを強制併合して戦争を打ち切る。さらに「復讐の日」の `available` に `NOT = { has_war_with = ALB }` を追加し、ALB戦がバルカン戦争へもつれ込む経路を塞いだ
- **`event_HUN_pol.1`**（`events/_vf_events_HUN.txt`）: 指示書0-5は「軽微なフレーバー」を想定していたが、実体は**ハンガリー共産革命（内戦生成）イベント**として実装済みだった。主宰裁定により革命イベントを正として維持

## 5. 幕間枝と大戦発火パート

### 幕間枝（`_vf_focus_SER.txt` 末尾、14NF）

- `allow_branch = { has_global_flag = vf_ended_balkan_war }`、`cost = 5`（14×35日≒490日で講和1928春→危機1929夏に一致）、座標はx=32〜40（既存ツリーと非干渉）、全NFに `ai_will_do = { factor = 20 }`
- 指示書§6-3の表どおりのID・効果。特記:
  - #4「露仏の保障」: **陣営加入はしない**（裁定: β共同交戦国方式）。FRA/RUSの `give_guarantee` ＋関係値＋`vf_SER_franco_russian_guarantee` のみ
  - #5「ウィーン条約軍備制限の破棄」: 該当ideaが存在しなかったため `idea_SER_vienna_arms_limit` を新規作成しSER開始時に付与。**戦闘・徴兵補正は入れていない**（軍需工場建設-10%・訓練+10%のみ。徴兵-15%を入れたらALB戦・バルカン戦争が泥沼化したため撤回済み）
  - #9/#10: 講和段階（`vf_SER_peace_tier_*`・州保有）で効果が分岐。州非保有はIFでスキップ
  - #11「最後の失地」: スレム・マチュヴァ＝**州109（東クロアチア、CRO首都州）**への請求権。白紙和平（tier_4）なら安定度-10%
  - #14「サラエボの再来」: `available = { date > 1929.6.1 }`（開戦年はβ固定）。`vf_greatwar.1` を発火するだけで宣戦しない

### クロアチア危機〜開戦（`events/_vf_events_greatwar.txt`）

口実は**国境衝突型**（裁定済み。スレム国境の銃撃戦）。`.1`(Day0 SER)→`.2`(+3 GER対応)→`.3`(+7 保障確認。`vf_SER_patronage_russia` の有無でdesc分岐)→`.4`(+14 最後通牒)→`.5`(+21 動員、`.9`で各大国へ警告)→`.6`(+35 開戦)。

- **`.4` 宥和ルート**: 受諾すると `vf_croatia_crisis_deferred` を立て安定度・戦争協力度-15%等、210日後に `.1` から再発火（回避ではなく延期。`.1` は fire_only_once にしていない）
- **`.6` 開戦**（最重要）: SER→CRO宣戦後、(a) GER・ENGの自動連鎖（自治領邦・英独同盟）を `has_war_with` で検証し、失敗なら **`vf_greatwar_chain_incomplete`**（＝バグ検出フラグ）を立てた上でフォールバックの `add_to_war` を実行、(b) RUS・FRAは陣営で表現できないため常に `add_to_war` でSER側参戦、(c) POL/OTT/ITA/ISTへ `.10` を送付
- **`.10` 参戦判定**: 幕間危機3件が立てる予定のフラグ（`vf_POL_tilt_*` / `vf_OTT_alignment_*` / `vf_ITA_regime_*`+`vf_ITA_grudge_SER` / `vf_IST_leaning_*`）を読むが、**未設定＝全員中立が既定**で必ず完走する。受け口のみで、立てる側は未実装
- **`.20`/`.21` 終結（β簡易）**: SER側勝利（GER・CRO降伏）で州109をSERへ明示移譲＋コア化。敗北はフレーバーのみ。**これ以上の大戦中・講和コンテンツは主宰指示により後回し**

## 6. AIの挙動制御（`common/ai_strategy/_vf_Balkan.txt`）

「宣戦したのに国境ががら空き／戦線が薄い」対策。NFの `hidden_effect` がグローバルフラグを立て、AI戦略がそれを読む二段構え:

| フラグ | 立てるNF | 効く戦略 |
|---|---|---|
| `vf_SER_preparing_war_ALB` | 失われたコソボ（平定作戦の2NF前） | SERが全軍をALB国境へ（`front_unit_request` 300、他国境は減点） |
| `vf_SER_preparing_war_BUL` | バルカン協商への対抗（復讐の日の1NF前） | SER→BUL/HUN国境、**ROM→HUN、GRE→BUL** も集結 |
| `vf_SER_preparing_war_CRO` | 最後の失地（開戦の3NF+5週間前） | SERが全軍をCRO国境へ |

さらに戦中は `front_unit_request` を維持し、ALB戦とCRO戦線（大戦）には `front_control`（`execution_type = rush` + `execute_order = yes`, priority 100）で**攻勢を強制**する。フラグの解除は不要（戦略側の `enable` 条件で寿命を区切ってある）。

**調整ノブ**: 張り付きが弱ければ `front_unit_request` の value（現在100〜300）を上げる。ALBが硬ければ `idea_SER_albania_pacification` の `attack_bonus_against`（現在0.5）か `.12` のタイムアウト（現在120日）を詰める。

## 7. 陣営・属国の実装状態（1925.3.1時点）

| 陣営 | 状態 |
|---|---|
| 英独同盟（GER盟主、+ENG） | **今回新設**。faction key はリテラル `"英独同盟"` |
| 露仏協商（FRA盟主、+RUS） | **今回新設**。`"露仏協商"`。SERは加入しない（共同交戦国方式） |
| バルカン協商（BUL盟主、+MNT+HUN） | 既存（`history/countries/BUL - Bulgaria.txt`）。対セルビア包囲同盟に相当。**CRO・ALBは非加盟**のため「バルカン戦争にGERが巻き込まれる」問題は構造的に起きない |
| 救国同盟（SER盟主、+GRE+ROM） | 既存。NF `focus_SER_pol_alliance_for_salvation` で生成 |
| 中央保障条約・仏伊協商・伊洪協商 | **faction化しない**（裁定済み）。ITAは無所属の天秤で開始 |

属国: GER→CRO・GER→BOHは `puppet` + `set_autonomy` で**自治領邦**。GER→LITは属国ではなく保障のみ（既存）。

## 8. 既知の問題・未対応（次セッションへの引き継ぎ）

1. **大戦連鎖の実機テスト未了**: T2（放置で大戦到達）・T8（CRO宣戦→GER/ENG参戦）・T9（宥和）・T10（フラグ皆無で完走）・T16（`vf_greatwar_chain_incomplete` が立たないこと）。T16でフラグが立っていたら自治領邦の自動参戦が機能していないサイン（大戦自体はフォールバックで成立する）
2. **`VF_balkan_strategy` は死んでいる**（既存バグ・裁定待ち）: `allowed` 内に `original_tag` が7行並んでおりAND判定で常に偽。`OR = { }` で包めば有効化できるが、全バルカン諸国の師団数が激変するため**勝手に直さないこと**（ファイル冒頭ヘッダにも注記済み）
3. **師団テンプレート名 `"Militiaaaa"`**: `.8` と `event_HUN_pol.1` で使用中の仮置き名。リネームは両ファイル同時修正が必要（裁定待ちのまま）
4. **既存NFのdescはほぼ全て仮置き**（`"〜" # Descは仮置き`）。幕間枝の新規分は本文執筆済み
5. **アイコン**: 新規NFは全て `GFX_goal_unknown`（指示書どおり）
6. **`vf_greatwar.10` の受け口フラグ群**は読むだけで、立てる側（ローマ進軍1925・波立危機1927・オスマン危機1929・GER「帝国の岐路」）は未実装
7. **MNTがバルカン協商に加盟したまま `event_SER_pol.4` で併合される**: `annex_country` は強制実行されるので動作するが、未併合のまま復讐の日に達するとMNTもBUL側で参戦する（設定に反しないため許容）
8. コミットは未実施。全変更が作業ツリー（ブランチ `feature/history`）にある

## 9. フラグ契約（完全版）

指示書§8の表が正。今回の追加分のみ再掲:

| 名前 | 種別 | 立てる場所 |
|---|---|---|
| `vf_balkan_war_min_duration_passed` | global | `event_SER_pol.11`（開戦330日後） |
| `vf_SER_peace_tier_1〜4` | global | `event_SER_pol.10`（1が最大戦果） |
| `vf_SER_patronage_russia` / `vf_SER_agitating_croatia` / `vf_SER_franco_russian_guarantee` | global | 幕間枝NF #2 / #12 / #4 |
| `vf_croatia_crisis_started` / `vf_croatia_crisis_deferred` / `vf_greatwar_started` / `vf_greatwar_chain_incomplete` | global | `vf_greatwar.1` / `.4` / `.6` / `.6`（検証失敗＝バグ） |
| `vf_SER_albania_war` | **country (SER)** | `event_SER_pol.7`（`.12` が経過日数判定に使用） |
| `vf_SER_preparing_war_ALB` / `_BUL` / `_CRO` | global | NF hidden_effect（AI集結制御用） |
