# VF β実装報告書：GER追補（初期法・AI軍拡・イデオロギー整合・error.log 一掃）

> **この文書の位置づけ**
> 実装セッション（2026-08-27〜28）の成果報告。読み手は**前史・Mod計画を熟知しているが、実リポジトリの内部ファイルと実装の詳細を知らないAIエージェント**を想定する。
> 元指示書: `.doc/10_GER追補_初期法とAI軍拡の整合.md`（§5 の記入欄をすべて埋めてある。**必ず併読**）
> 前提: `.doc/06`＋`.doc/07`（SER開戦導線）、`.doc/08`＋`.doc/09`（GER議会ルート）

---

## 1. 結論サマリ

追補10 の4タスクのうち **§1・§3・§4（T-GER-14 / T-GER-5）を完了**。§2（露仏AI軍拡のリグレッション検証）は未実施。
加えて、追補の想定外だった**大国AIが軍拡しない真因**を特定・修正し、`error.log` を **3548行 → 約233行**へ削減した。

| # | タスク | 状態 |
|---|---|---|
| §1 | GERの開始時法律 ＋ 軍事NF・AI戦略の見直し | **完了**（追補10 §5-3 / §5-3-1） |
| §2 | 露仏AI軍拡によるバルカン戦争へのリグレッション検証 | **未実施**（AI放置の通し走行が必要） |
| §3 | イデオロギー「民主主義」参照の解消 ＋ 正当性の判断 | **完了**（追補10 §5-2 / §5-2-1） |
| §4 | 未実施テストの消化（T-GER-14 / T-GER-5） | **完了**（追補10 §5-5〜§5-9） |
| 追加 | **大国AI師団設計図の欠落**（44個師団問題の真因） | **完了・実機確認済み**（追補10 §5-3-2） |
| 追加 | `error.log` の一掃（23分類・約3300行削減） | **完了・実機確認済み**（追補10 §5-6〜§5-9） |

**実機確認済み**（主宰による走行、2026-08-28）:
開戦時の師団数が大幅増／NF「騎兵強化」で騎兵師団が生成される／国民精神「勢力均衡」に枢密院の傾きが表示される／
`error.log` から VF製ファイル由来のエラーが**全て消滅**（残存0件）。

---

## 2. 最重要の発見：大国AIが軍拡しなかった真因

09 §7 は44個師団問題の原因を3つ（①徴兵法なし ②AI戦略なし ③軍事NFが骨のみ）としていたが、**第4の原因**があった。

**`common/ai_templates/` に `generic.txt` 1本しか存在せず、その `blocked_for` が GER / FRA / ITA / RUS を除外していた。**

バニラでは各国専用の ai_templates ファイルが別に存在するため `blocked_for` に意味があるが、このModにはそれが無い。
結果、**4大国は infantry / armor / mountaineer / marine のどの役割の師団設計図も持たず**、AIは「何を作ればよいか」を決められない。
ENG・USA・JAP は `blocked_for` に含まれないため generic を使えており、大国間で挙動が割れていた説明もつく。

設計図が無い以上、`_vf_GreatPowers.txt` の `force_build_armies` / `ai_wanted_divisions_factor` / `role_ratio` は**すべて空振りしていた**。

**対応**: `common/ai_templates/_vf_GreatPowers.txt` を新設し、4か国共通の仮設計図を与えた（詳細は追補10 §5-3-2）。

---

## 3. ファイルマップ

### 新規作成

| ファイル | 内容 |
|---|---|
| `common/ai_templates/_vf_GreatPowers.txt` | **GER/FRA/ITA/RUS のAI師団設計図**（歩兵線・機甲線・山岳線）。国ごとの作り分けは `TODO(VF)` |
| `history/countries/IMP - Bhopal.txt` / `IRJ - Rajasthan.txt` / `NTC - Karnataka.txt` | タグはあるのに history が無く首都未定義だった3国。近隣国 `KAS - Kashmir.txt` の構成を踏襲 |
| `.doc/11_GER追補_実装報告書.md` | 本文書 |

### 削除

| ファイル | 理由 |
|---|---|
| `history/countries/AUS - Australia.txt` / `CTB - ...txt` / `MAP - Mapuchenia.txt` | タグ未定義・保有州0・参照0の死にファイル（豪州は `AST` を使用） |

### 改修（GER議会ルート関連）

| ファイル | 変更 |
|---|---|
| `history/countries/GER - Germany.txt` | 開始時の徴兵法 `limited_conscription` / 経済法 `low_economic_mobilisation` / 貿易法 `export_focus`、`set_war_support = 0.30` を明示 |
| `common/national_focus/_vf_focus_GER.txt` | 「国土防衛計画」→`extensive_conscription`／戦時「緊急動員」→`service_by_requirement`／「連合強化」を `socialism +5%` ＋ `liberalism +5%` へ／「正当性+50」を恒久削除／`NOT` の多条件バグ4箇所を `NOR` へ |
| `common/ai_strategy/_vf_GreatPowers.txt` | GER平時の `ai_wanted_divisions_factor` を 100→50。ai_templates への相互参照ヘッダを追記 |
| `history/units/GER_mil_infantry.txt` / `GER_mil_cavalry.txt` / `GER_mil_reserves.txt` | **師団テンプレートをファイル内に同梱**（`load_oob` 時に名前解決できず師団が生成されていなかった）。予備役は専用の `Reserve-Division` を新設 |
| `localisation/.../ideas_GER_l_japanese.yml` | 「勢力均衡」desc の複数行を `\n` に統合（枢密院の傾きが表示されていなかった） |

### 改修（Mod全体のエラー修正）

| ファイル | 変更 |
|---|---|
| `common/abilities/generic_leader_abilities.txt` | 本体1.19.2 の内容で置換（`force_attack`/`last_stand` が無効化されていた・新5アビリティが欠落）。存在しないバニラNFを参照する `OWNER` ブロック3箇所を削除 |
| `common/units/critical_parts/00_critical_parts.txt` | 本体1.19.2 の内容で置換（末尾が欠落し海戦のクリティカル処理が壊れていた） |
| `common/units/equipment/motorized.txt` | `motorbike_equipment` / `_1` を移植（憲兵ユニットが機能していなかった）。Mod独自の `year = 1900` は保持 |
| `common/script_enums.txt` | `motorbike_equipment` / `_1` を有効化 |
| `interface/mapicons.gui` / `nationalfocusview.gui` | 本体1.19系が要求する `active_abilities` / `dam_icon` / `overlay` を移植（旧ログ1772行） |
| `common/unit_leader/00_traits.txt` | `SOV_purged_junior_navy_officers_3` 参照13箇所を無効化（148行） |
| `common/ai_faction_theaters/ai_faction_theaters.txt` | 存在しないリージョン296〜298 の5件を無効化 |
| `common/synchronized_dynamic_tokens/_vf_tokens.txt` | PERの動的トークン3件を登録（マルチのOOS対策） |
| `history/countries/*.txt`（55件） | 首都が非保有州だったものを修正（**51か国が `capital = 797` のまま**だった） |
| `history/countries/CAN` / `NZL` / `IST` | 法律トークンの綴り誤り・未定義精神の差し替え |
| `history/states/*.txt`（8件） | 重複 `buildings` ブロックの統合（建物が消えていた）・非保有 province への指定の無効化 |
| `history/units/SER_houhei.txt` | `regiments` の支援型 `artillery` 2行を削除（**主宰裁定**。実挙動は元から歩兵9のみ） |
| `events/_vf_events_greatwar.txt` | `vf_greatwar.6` の二重宣戦を `has_war_with` でガード |
| `interface/_VF/goals/goals_ita_shine.gfx` | スプライト名の `_shine` 接尾辞欠落を修正 |

---

## 4. ゲーム挙動として復元されたもの

ログを消しただけでなく、**壊れていた機能が実際に直った**ものを列挙する。

| 内容 | 症状 |
|---|---|
| GER騎兵4個師団 | NF「騎兵強化」を取っても師団が1個も生成されていなかった |
| 国民精神「勢力均衡」の枢密院表示 | desc が読み込まれず表示されていなかった |
| ケーニヒスベルクのトーチカ／Cape・ホバートの軍港 | 同一州内の重複 `buildings` ブロックで上書きされ消えていた |
| 55か国の首都 | 首都未定義でAIが機能せず、降伏判定も正しく働かなかった（**HUNを含む**＝バルカン戦争の当事国） |
| 将軍の能力 `force_attack` / `last_stand` | 廃止記法のため効果が一切適用されていなかった |
| 司令部ユニットの5能力 | 定義が欠落し `hq_*` サブユニットが解禁できなかった |
| 海戦のクリティカルヒット処理 | 空母・潜水艦用の critical part が未定義だった |
| 憲兵ユニット | `motorbike_equipment` が未定義で読み込めていなかった |

---

## 5. 既知の問題・残TODO

### 5-1. 主宰の判断待ち

| # | 内容 |
|---|---|
| A | **師団数が多すぎる懸念**。絞る順序の推奨: ①`_vf_GreatPowers.txt` の `VF_GER_base_buildup_strategy` の `ai_wanted_divisions_factor`（現在50）→ ②各段階の `force_build_armies` → ③`ai_templates` の `vf_major_infantry_upgraded` の軍需工場しきい値（現在18）。**開始時法とAI設計図は戻さないこと**（軍拡の量を決めるノブではない） |
| B | **露仏がNFを持たず早期降伏する**。08 §3 でβスコープ外と決めた判断が、開戦後の持久力という別要求で顕在化した。選択肢は ①露仏に最小限の軍事・産業NFを与える ②history とAI戦略だけで底上げ ③降伏しやすさを許容し大戦の長さを別手段で担保 |
| C | `history/units/SER_houhei.txt` に `units = {}` ブロックが無く、テンプレート定義だけで師団を生成していない。NF側は装備備蓄と併せて師団追加を意図していた可能性がある（足すとSER側の戦力が増える） |

### 5-2. 美術・アセット担当

| 件数 | 内容 |
|---|---|
| 15 | **国旗の欠落: IMP・IRJ・KOR**。ゲーム内でも旗が出ない |
| 100 | マップデータ（1ピクセル州・バウンディングボックス過大・`Map invalid X crossing`・州13254の描画位置）。`provinces.bmp` の編集が必要 |
| 6 | 日本語フォント（`hoi_mapfont4_*.fnt` の lineHeight 不一致、`hoi_30.tga` / `hoi_33.tga` が MAX_TEXTURE_SIZE 超過） |
| 1 | `gfx/interface/factions/ui/factions_button.dds` のミップマップ不足 |

### 5-3. 対応不可能と結論したもの

| 件数 | 内容 |
|---|---|
| 98 | 未定義タグ84種（`SOV` / `YUG` / `TUR` ほか）。**バニラの455ファイル**が参照しており、Mod側で全て上書きしない限り消えない |
| 3 | `special_forces_tracks.txt` / `infantry_subdoctrines.txt`（バニラ側のファイル。Mod内に存在しない） |
| 1 | `gfx/flags/medium/BUK_communism.tga` の形式不正（バニラ側のアセット） |
| 1 | `gfx/train_gfx_database/NSB_generic.txt` の `SOV` トークン（バニラ側） |

### 5-4. その他の申し送り

- `common/units/carrier.txt` / `submarine.txt` / `military_police.txt` は**本体と完全に同一**で、上書きする意味が無い。削除してバニラに任せるほうが本体更新に強い。`00_critical_parts.txt` / `generic_leader_abilities.txt` も独自変更が無いため同様
- 保有州ゼロの9か国（BRU / CAM / CHA / LUA / MAF / RHO / SAR / TST / YEM）は**どの州を首都にしてもエラーが消えない**。解放時に備えるならコア保有州（CAM→741 / CHA→1014 / LUA→1015 / MAF→858 / YEM→906 / RHO→985）が妥当。BRU・SAR・TST は手がかり無し
- 州の切り直しで**軍港4件が失われている**（追補10 §5-7-1 の表）。移設先の所有国が変わるため（とくに `766` ROM → 州78 **RUS**）勝手に移していない
- `.doc/10` の §5 各表はすべて記入済み。フラグ・変数の契約（08 §10）に本セッションでの追加は無い

---

## 6. 次回セッションの予定

**優先度順**。上から潰す。

| 優先 | # | 内容 | 実施者 |
|---|---|---|---|
| **高** | 1 | **追補10 §2 の通し走行**（AI放置 1925.3.1 → 1930）。§5-4 の表を記入する。露仏のAI軍拡がバルカン戦争の講和 tier・`event_SER_pol.9`・アルバニア戦を壊していないか。**このタスクの本体で唯一の未実施項目** | 主宰（走行）＋ エージェント（差分の切り分け） |
| **高** | 2 | 上の走行で**開戦時の師団数**を記録し、§5-1-A（多すぎる懸念）を裁定する | 主宰 |
| 中 | 3 | T-GER-12（帝冠領再編ディシジョンの可変コスト） | 主宰 |
| 中 | 4 | T-GER-4（1926年選挙の重心3種と首相・後続イベントの分岐） | 主宰 |
| 中 | 5 | T-GER-13（GER側で「バルカンの砲声」「ベオグラードの講和」が発火するか） | 主宰 |
| 中 | 6 | 選挙が1926年内に完了するか（09 §6 のAIロック修正の再確認） | 主宰 |
| 低 | 7 | T-GER-10 / 11 / 2 / 3 | 主宰 |
| — | 8 | §5-1-B（露仏の早期降伏）の方針裁定 → 決まれば実装 | 主宰 → エージェント |
| — | 9 | §5-2 の美術タスク（国旗3件が最優先。ゲーム内で見える） | 美術担当 |
| — | 10 | 08 §18 の本リリース送りTODO（皮職人の諜報スロット、帝冠領工業ボーナス、フランクフルト再会議、「城内平和」SPD分岐、軍事独裁の体制転換、軍事・産業・戦時のdesc） | 次フェーズ |

**走行時に記録してほしいもの**（追補10 §5-4 の表）:
バルカン戦争の開戦時期／`vf_ended_balkan_war` の時期／講和 tier（`vf_SER_peace_tier_*` のどれ）／`event_SER_pol.9` の発火有無／
アルバニア戦の終結時期／`vf_greatwar_started` の時期／開戦時の師団数（GER / RUS / FRA / ENG / SER）。

**切り分けの起点**（`06`/`07` と食い違った場合）: `_vf_GreatPowers.txt` の `VF_RUS_buildup_strategy` / `VF_FRA_buildup_strategy` は
**フラグ無しで1925年から有効**（prewar 側だけが `vf_ended_balkan_war` で gate されている）。
追補10 §2-3 の推奨「露仏の軍拡開始を1928年以降に遅らせる」を採るなら、この2ブロックが対象になる。
**SER側のスクリプトは書き換えないこと。**
