import os
import re
import sys
import configparser
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QTreeWidget, QTreeWidgetItem,
                             QLineEdit, QScrollArea, QFrame, QMenu, QAction,
                             QDialog, QListWidget, QVBoxLayout as QVBoxLayoutDialog, QPushButton as QPushButtonDialog,
                             QStackedWidget)
from PyQt5.QtCore import Qt, QPoint

class ProvinceListDialog(QDialog):
    def __init__(self, province_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("プロビンス一覧")
        layout = QVBoxLayoutDialog()

        self.province_list_widget = QListWidget()
        self.province_list_widget.addItems(province_list)
        layout.addWidget(self.province_list_widget)

        close_button = QPushButtonDialog("閉じる")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)

class OwnerCountryDialog(QDialog):
    def __init__(self, owner_country_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("領有国一覧")
        layout = QVBoxLayoutDialog()
        self.owner_country_list_widget = QListWidget()
        self.owner_country_list_widget.addItems(owner_country_list)
        layout.addWidget(self.owner_country_list_widget)
        close_button = QPushButtonDialog("閉じる")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)

class BelongingStateDialog(QDialog):
    def __init__(self, belonging_state_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("所属ステート一覧")
        layout = QVBoxLayoutDialog()
        self.belonging_state_list_widget = QListWidget()
        self.belonging_state_list_widget.addItems(belonging_state_list)
        layout.addWidget(self.belonging_state_list_widget)
        close_button = QPushButtonDialog("閉じる")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)

class ProvinceTransferDialog(QDialog):
    def __init__(self, province_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("移譲するプロビンスを選択")
        layout = QVBoxLayoutDialog()

        self.province_list_widget = QListWidget()
        self.province_list_widget.setSelectionMode(QListWidget.MultiSelection) # 複数選択を可能にする
        self.province_list_widget.addItems(province_list)
        layout.addWidget(self.province_list_widget)

        button_layout = QHBoxLayout()

        next_button = QPushButtonDialog("次へ")
        next_button.clicked.connect(self.accept) # 次へボタンでダイアログを閉じる
        button_layout.addWidget(next_button)

        cancel_button = QPushButtonDialog("キャンセル")
        cancel_button.clicked.connect(self.reject) # キャンセルボタン
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_selected_provinces(self):
        return [item.text() for item in self.province_list_widget.selectedItems()]

class TargetStateDialog(QDialog):
    def __init__(self, parent=None, source_state_info=None):
        super().__init__(parent)
        self.setWindowTitle("移譲先のステートIDを入力")
        self.source_state_info = source_state_info # 移譲元ステート情報を保存
        layout = QVBoxLayoutDialog()

        if self.source_state_info:
            source_state_name = self.source_state_info["localized_name"]
            source_state_label = QLabel(f"移譲元ステート: {source_state_name} ({self.source_state_info['state_id']})")
            layout.addWidget(source_state_label)

        self.target_state_id_entry = QLineEdit()
        self.target_state_id_entry.setPlaceholderText("移譲先ステートIDを入力")
        layout.addWidget(self.target_state_id_entry)

        button_layout = QHBoxLayout()

        transfer_button = QPushButtonDialog("移譲")
        transfer_button.clicked.connect(self.accept)
        button_layout.addWidget(transfer_button)

        back_button = QPushButtonDialog("戻る")
        back_button.clicked.connect(self.reject) # reject で ProvinceTransferDialog に戻るように修正
        button_layout.addWidget(back_button)

        cancel_button = QPushButtonDialog("キャンセル")
        # キャンセル時は QDialog.Rejected を返す標準動作で良いので接続不要（または self.reject を接続）
        # self.reject() はダイアログを閉じて Rejected シグナルを発行する
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_target_state_id(self):
        target_state_id_text = self.target_state_id_entry.text()
        if target_state_id_text.isdigit():
            return int(target_state_id_text)
        return None

class StateFileLister(QWidget):
    def __init__(self, state_dir="history/states", localisation_dir="localisation/japanese", localisation_file_name="state_names_l_japanese.yml"):
        super().__init__()

        self.config = configparser.ConfigParser()
        self.config.read('state_tool_config.ini')

        self.state_dir = self.config.get('Directories', 'state_dir', fallback='history/states')
        self.localisation_dir = self.config.get('Directories', 'localisation_dir', fallback='localisation/japanese')
        self.localisation_file_name = self.config.get('Directories', 'localisation_file_name', fallback='state_names_l_japanese.yml')
        # プロビンス関連のパスもconfigから読み込むように変更 (推奨)
        self.strategic_regions_dir = self.config.get('Directories', 'strategic_regions_dir', fallback='map/strategicregions')
        self.definition_csv_path = self.config.get('Directories', 'definition_csv', fallback='map/definition.csv')

        self.default_sort_key = self.config.get('UI', 'default_sort_key', fallback='state_id')
        self.default_sort_order_ascending = self.config.getboolean('UI', 'default_sort_order_ascending', fallback=True)

        self.state_files_info = []
        self.filtered_state_files_info = []
        self.sort_key = self.default_sort_key
        self.sort_order_ascending = self.default_sort_order_ascending
        self.localisation_strings = self.load_localisation()
        self.current_item = None

        # プロビンス関連のデータ
        self.strategic_region_files_info = []
        self.province_data = []
        self.filtered_province_data = []

        self.init_ui()
        self.load_initial_data() # データの初期読み込みをまとめる

    def load_initial_data(self):
        """アプリケーション起動時に必要なデータを読み込む"""
        self.load_localisation() # localisation は最初に読み込む
        self.load_state_files() # state data の読み込み
        self.load_province_data() # province data の読み込み (state ID 割り当てに state_files_info が必要)
        self.load_strategic_regions() # strategic region data の読み込み
        self.display_initial_view() # 初期ビューの表示

    def display_initial_view(self):
        """初期ビュー（ステートビュー）を表示する"""
        self.filtered_state_files_info = list(self.state_files_info)
        self.sort_state_files() # 初期ソート
        self.display_state_files()
        self.stacked_widget.setCurrentIndex(0) # ステートビューをデフォルトに

    def load_localisation(self):
        localisation_strings = {}
        filepath = os.path.join(self.localisation_dir, self.localisation_file_name)
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                # より堅牢な解析 (コメントや空行を無視)
                lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith('#')]
                if lines and lines[0].lower() == 'l_japanese:':
                    lines.pop(0) # BOM付きutf-8の場合 l_japanese: が行頭に来ることがある
                for line in lines:
                    if ":" in line:
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            # バージョン番号やコメントを除去
                            value_part = parts[1].split('#')[0].strip()
                            # クォーテーションを除去
                            if len(value_part) >= 2 and value_part.startswith('"') and value_part.endswith('"'):
                                value = value_part[1:-1]
                            elif len(value_part) >= 2 and value_part.startswith("'") and value_part.endswith("'"):
                                value = value_part[1:-1]
                            else:
                                # クォーテーションがない場合はそのまま (数値など)
                                value = value_part
                            localisation_strings[key] = value
        except FileNotFoundError:
            print(f"警告: ローカライズファイルが見つかりません: {filepath}")
        except Exception as e:
            print(f"ローカライズファイル読み込みエラー {filepath}: {e}")
        self.localisation_strings = localisation_strings # クラス変数にセット

    def init_ui(self):
        main_layout = QVBoxLayout() # メインレイアウトを最初に定義

        # --- ツールバー ---
        toolbar_layout = QHBoxLayout()
        self.view_combo = QComboBox()
        self.view_combo.addItem("ステートビュー")
        self.view_combo.addItem("プロビンスビュー")
        self.view_combo.addItem("戦略地域ビュー")
        self.view_combo.currentIndexChanged.connect(self.switch_view)
        toolbar_layout.addWidget(self.view_combo)
        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)

        # --- ソート設定 ---
        sort_layout = QHBoxLayout()
        sort_label = QLabel("ソート:")
        sort_layout.addWidget(sort_label)

        self.sort_combo = QComboBox()
        # 各ビューで利用可能なソートキーを設定するように変更が必要
        # ここでは一旦全キーを入れる
        self.sort_combo.addItems([
            "ステートID", "ステート名", "ローカライズ名", "領有国", "人口", # ステートビュー
            "プロビンスID", "R", "G", "B", "地形", "沿岸", # プロビンスビュー (ステートID,名,ローカライズ名は共通)
            "戦略地域ID", "戦略地域名" # 戦略地域ビュー (ローカライズ名は共通)
        ])
        # configから読み込んだデフォルトキーを設定
        try:
            self.sort_combo.setCurrentText(self.default_sort_key)
        except Exception: # 設定したキーが存在しない場合
             self.sort_combo.setCurrentIndex(0) # デフォルトで最初の項目を選択
             self.sort_key = self.sort_combo.currentText() # sort_key も更新
        self.sort_combo.currentTextChanged.connect(self.on_sort_key_changed) # ソートキー変更時の処理

        self.sort_order_button = QPushButton("昇順" if self.sort_order_ascending else "降順")
        self.sort_order_button.clicked.connect(self.toggle_sort_order)
        sort_layout.addWidget(self.sort_combo) # コンボボックスを先に追加
        sort_layout.addWidget(self.sort_order_button)
        sort_layout.addStretch()
        main_layout.addLayout(sort_layout)

        # --- 検索バー ---
        search_layout = QHBoxLayout()
        search_label = QLabel("検索:")
        search_layout.addWidget(search_label)

        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("検索語句を入力")
        self.search_entry.returnPressed.connect(self.search_data) # 関数名を変更
        search_layout.addWidget(self.search_entry)

        self.search_criteria_combo = QComboBox()
        # ここもビューごとに更新が必要
        self.search_criteria_combo.addItems([
            "ステートID", "ステート名", "ローカライズ名", "領有国", "人口", "プロビンス", # ステートビュー
            "プロビンスID", "地形", "ステートID", # プロビンスビュー
            "戦略地域ID", "戦略地域名" # 戦略地域ビュー
        ])
        search_layout.addWidget(self.search_criteria_combo)

        self.match_type_combo = QComboBox()
        self.match_type_combo.addItems(["部分一致", "完全一致"])
        search_layout.addWidget(self.match_type_combo)

        search_button = QPushButton("検索")
        search_button.clicked.connect(self.search_data) # 関数名を変更
        search_layout.addWidget(search_button)
        main_layout.addLayout(search_layout)

        # --- QStackedWidget と 各ビューの TreeWidget ---
        self.stacked_widget = QStackedWidget()

        # ステートファイルリスト (QTreeWidget)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setObjectName("state_tree_widget") # オブジェクト名設定
        self.tree_widget.setColumnCount(5)
        self.tree_widget.setHeaderLabels(["ステートID", "ステート名", "ローカライズ名", "領有国", "人口"])
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.tree_widget.setSortingEnabled(False) # 手動ソートのため Qt ソートは無効化
        self.stacked_widget.addWidget(self.tree_widget)

        # プロビンスリスト (QTreeWidget)
        self.province_tree_widget = QTreeWidget()
        self.province_tree_widget.setObjectName("province_tree_widget")
        self.province_tree_widget.setColumnCount(9)
        self.province_tree_widget.setHeaderLabels(["プロビンスID", "R", "G", "B", "地形", "沿岸", "ステートID", "ステート名", "ローカライズ名"])
        self.province_tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.province_tree_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.province_tree_widget.setSortingEnabled(False) # 手動ソートのため Qt ソートは無効化
        self.stacked_widget.addWidget(self.province_tree_widget)

        # 戦略地域リスト (QTreeWidget)
        self.strategic_region_tree_widget = QTreeWidget()
        self.strategic_region_tree_widget.setObjectName("strategic_region_tree_widget")
        self.strategic_region_tree_widget.setColumnCount(3)
        self.strategic_region_tree_widget.setHeaderLabels(["戦略地域ID", "戦略地域名", "ローカライズ名"])
        self.strategic_region_tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.strategic_region_tree_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.strategic_region_tree_widget.setSortingEnabled(False) # 手動ソートのため Qt ソートは無効化
        self.stacked_widget.addWidget(self.strategic_region_tree_widget)

        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

        # 初期表示用にソート・検索コンボボックスの内容を更新
        self._update_sort_search_options(0)


    def _update_sort_search_options(self, index):
        """ビューの切り替えに応じてソートと検索の選択肢を更新"""
        self.sort_combo.blockSignals(True) # 更新中のシグナルをブロック
        self.search_criteria_combo.blockSignals(True)

        self.sort_combo.clear()
        self.search_criteria_combo.clear()

        if index == 0: # ステートビュー
            sort_options = ["ステートID", "ステート名", "ローカライズ名", "領有国", "人口"]
            search_options = ["ステートID", "ステート名", "ローカライズ名", "領有国", "人口", "プロビンス"]
        elif index == 1: # プロビンスビュー
            sort_options = ["プロビンスID", "R", "G", "B", "地形", "沿岸", "ステートID", "ステート名", "ローカライズ名"]
            search_options = ["プロビンスID", "地形", "ステートID", "ステート名", "ローカライズ名"]
        elif index == 2: # 戦略地域ビュー
            sort_options = ["戦略地域ID", "戦略地域名", "ローカライズ名"]
            search_options = ["戦略地域ID", "戦略地域名", "ローカライズ名", "プロビンス"] # プロビンス検索追加
        else:
            sort_options = []
            search_options = []

        self.sort_combo.addItems(sort_options)
        self.search_criteria_combo.addItems(search_options)

        # 現在のソートキーが新しいオプションにあればそれを選択、なければ最初の項目を選択
        if self.sort_key in sort_options:
            self.sort_combo.setCurrentText(self.sort_key)
        elif sort_options:
            self.sort_combo.setCurrentIndex(0)
            self.sort_key = self.sort_combo.currentText() # 存在しないキーが選択されていた場合、キーも更新
        else:
            self.sort_key = ""

        self.sort_combo.blockSignals(False) # シグナルブロック解除
        self.search_criteria_combo.blockSignals(False)


    def on_sort_key_changed(self, key):
        """ソートキーコンボボックスの選択が変更されたときに呼び出される"""
        if key: # 空でないことを確認
            self.sort_key = key
            self.sort_and_display_current_view() # 現在のビューをソートして表示

    def switch_view(self):
        index = self.view_combo.currentIndex()
        self.stacked_widget.setCurrentIndex(index)
        self._update_sort_search_options(index) # ソート・検索オプションを更新

        # 必要に応じてデータを読み込み or 表示を更新
        if index == 0: # ステートビュー
            # ステートデータは最初に読み込まれているので表示のみ
            self.sort_and_display_current_view()
        elif index == 1: # プロビンスビュー
            # プロビンスデータも最初に読み込まれているので表示のみ
            # (必要ならここで再読み込み self.load_province_data())
            self.filtered_province_data = list(self.province_data) # フィルタをリセット
            self.sort_and_display_current_view()
        elif index == 2: # 戦略地域ビュー
            # 戦略地域データも最初に読み込まれているので表示のみ
            # (必要ならここで再読み込み self.load_strategic_regions())
            self.filtered_strategic_region_files_info = list(self.strategic_region_files_info) # フィルタをリセット
            self.sort_and_display_current_view()

    def load_state_files(self):
        self.state_files_info = []
        if not os.path.isdir(self.state_dir):
            print(f"エラー: ステートディレクトリが見つかりません: {self.state_dir}")
            return

        for filename in os.listdir(self.state_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(self.state_dir, filename)
                state_info = self.parse_state_file(filepath)
                if state_info:
                    self.state_files_info.append(state_info)
        # ここではフィルタリングやソートは行わない (表示時に行う)

    def parse_state_file(self, filepath):
        filename = os.path.basename(filepath)
        # ファイル名からIDと名前を取得 (より堅牢な方法)
        match = re.match(r"(\d+)[-\s]*(.*?)\.txt", filename)
        if not match:
            print(f"警告: ファイル名の形式が不正です: {filename}")
            return None
        state_id = int(match.group(1))
        state_name_from_file = match.group(2).replace("_", " ").replace("-", " ").strip().title()
        if not state_name_from_file: # IDだけのファイル名の場合
             state_name_from_file = f"State {state_id}"

        owner = "N/A"
        manpower = "0" # デフォルトを0に
        provinces = []
        localized_name = f"STATE_{state_id}" # デフォルトのローカライズキー形式
        name_key = None # name="..." で指定されたキー

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

                # state={ ... } ブロックの外側と内側の両方で検索
                owner_match = re.search(r"^\s*owner\s*=\s*([A-Z]{3})", content, re.MULTILINE)
                if owner_match:
                    owner = owner_match.group(1)

                manpower_match = re.search(r"^\s*manpower\s*=\s*(\d+)", content, re.MULTILINE)
                if manpower_match:
                    manpower = manpower_match.group(1)
                else: # add_core_of や history などに含まれる場合も考慮 (より詳細な解析が必要かも)
                    manpower_match_hist = re.search(r"^\s*add_manpower\s*=\s*(\d+)", content, re.MULTILINE) # history内の記述?
                    if manpower_match_hist:
                       manpower = manpower_match_hist.group(1)


                name_match = re.search(r"^\s*name\s*=\s*\"(.*?)\"", content, re.MULTILINE)
                if name_match:
                    name_key = name_match.group(1)
                    localized_name = self.localisation_strings.get(name_key, f"<{name_key}?>") # .getで安全に取得
                else:
                    # name=がない場合、ファイル名から生成した名前を使うか、デフォルトキーを使う
                    # ここではデフォルトキーを優先し、見つからなければファイル名由来の名前
                    default_loc_key = f"STATE_{state_id}"
                    localized_name = self.localisation_strings.get(default_loc_key, state_name_from_file)


                # プロビンスIDのリストを抽出 (複数の形式に対応)
                # 1. provinces = { 1 2 3 }
                provinces_match_block = re.search(r"^\s*provinces\s*=\s*{([\s\d]*)}", content, re.MULTILINE)
                if provinces_match_block:
                    provinces = provinces_match_block.group(1).split()
                else:
                    # 2. add_province = 1 (hoi4 vanilla では通常使われないが念のため)
                    provinces = re.findall(r"^\s*add_province\s*=\s*(\d+)", content, re.MULTILINE)

                # provinces リスト内の非数値を除去し、intに変換 (後で文字列に戻す方が扱いやすいかも)
                provinces = [p for p in provinces if p.isdigit()]

        except Exception as e:
            print(f"ステートファイル解析エラー {filepath}: {e}")
            return None

        return {
            "state_id": state_id,
            "filename": filename,
            "state_name": state_name_from_file, # ファイル名由来の名前
            "localized_name": localized_name, # ローカライズされた名前 or キー or ファイル名由来
            "name_key": name_key, # stateファイル内の name= の値
            "owner": owner,
            "manpower": manpower,
            "provinces": provinces # プロビンスIDのリスト (文字列)
        }

    def load_province_data(self):
        self.province_data = []
        if not os.path.isfile(self.definition_csv_path):
             print(f"エラー: definition.csv が見つかりません: {self.definition_csv_path}")
             return

        try:
            with open(self.definition_csv_path, 'r', encoding='utf-8') as f:
                # ヘッダー行の形式が不明なため、決め打ちせず最初の行を読む
                header = f.readline().strip().lower()
                # ヘッダーから必要な列のインデックスを見つける (より堅牢な方法)
                # 期待するヘッダー（例）: province;red;green;blue;x;y;type;continent;terrain;climate...
                # 実際の definition.csv の形式に合わせて調整が必要
                # ここでは元のコードの ';' 区切りと列順を仮定する
                # header_parts = header.split(';')
                # try:
                #     id_col = header_parts.index("province") # or "id" or "province id"
                #     r_col = header_parts.index("red")
                #     g_col = header_parts.index("green")
                #     b_col = header_parts.index("blue")
                #     type_col = header_parts.index("type") # "land" or "sea"
                #     coastal_col = header_parts.index("coastal") # or "is_coastal"
                #     terrain_col = header_parts.index("terrain")
                # except ValueError:
                #      print(f"エラー: definition.csv のヘッダーに必要な列が見つかりません。")
                #      return

                for line in f:
                    if line.strip() == "" or line.startswith('#') or line.startswith(';'): # 空行やコメント行をスキップ
                        continue
                    items = line.strip().split(';')
                    if len(items) < 7: # 必要な列数を確認 (例: id, r, g, b, type, coastal, terrain)
                        print(f"警告: definition.csv の行データが不足しています: {line.strip()}")
                        continue
                    # 元のコードに合わせて列を仮定
                    province_id, r, g, b, land_or_sea, is_coastal, terrain_type = items[:7]

                    # is_coastal が "true" かどうかで判定 (小文字に変換して比較)
                    is_coastal_bool = is_coastal.lower() == 'true'

                    # ステートIDを割り当て (プロビンスデータ読み込み後にstate_files_infoが必要)
                    state_id, state_name, localized_name = self.get_state_info_for_province(province_id)

                    province_info = {
                        "province_id": province_id,
                        "r": r,
                        "g": g,
                        "b": b,
                        "land_or_sea": land_or_sea, # "land" or "sea"
                        "is_coastal": "true" if is_coastal_bool else "false", # 文字列で保持
                        "terrain_type": terrain_type,
                        "state_id": state_id,
                        "state_name": state_name,
                        "localized_name": localized_name,
                    }
                    self.province_data.append(province_info)
        except FileNotFoundError:
             print(f"エラー: definition.csv が見つかりません: {self.definition_csv_path}")
        except Exception as e:
            print(f"definition.csv 読み込みエラー: {e}")

    def get_state_info_for_province(self, province_id_str):
        """指定されたプロビンスIDが属するステートの情報を返す"""
        # self.state_files_info がロード済みである必要がある
        for state_info in self.state_files_info:
            if province_id_str in state_info["provinces"]:
                return state_info["state_id"], state_info["state_name"], state_info["localized_name"]
        return -1, "N/A", "N/A" # 見つからない場合

    def display_province_data(self):
        self.province_tree_widget.clear()
        # filtered_province_data が空でも province_data を使うのではなく、
        # 検索結果が0件の場合は何も表示しないのが一般的
        display_data = self.filtered_province_data

        for province_info in display_data:
            # ステートIDが後から更新される可能性を考慮し、表示時に再取得する（より正確だが低速）か、
            # province_data生成時に確定させる（高速だが移譲後の表示更新が必要）か。
            # ここでは province_data 生成時の情報を信じる
            state_id_str = str(province_info["state_id"]) if province_info["state_id"] != -1 else "N/A"
            state_name = province_info["state_name"]
            localized_name = province_info["localized_name"]

            item = QTreeWidgetItem([
                province_info["province_id"],
                province_info["r"],
                province_info["g"],
                province_info["b"],
                province_info["terrain_type"],
                province_info["is_coastal"],
                state_id_str,
                state_name, # ファイル名由来 or STATE_xxx
                localized_name, # ローカライズ名 or <key?> or ファイル名由来
            ])
            self.province_tree_widget.addTopLevelItem(item)

    def display_state_files(self):
        self.tree_widget.clear()
        display_data = self.filtered_state_files_info

        for state_info in display_data:
            item = QTreeWidgetItem([
                str(state_info["state_id"]),
                state_info["state_name"], # ファイル名由来 or State xxx
                state_info["localized_name"], # ローカライズ名 or <key?> or ファイル名由来
                state_info["owner"],
                state_info["manpower"]
            ])
            self.tree_widget.addTopLevelItem(item)

    def toggle_sort_order(self):
        self.sort_order_ascending = not self.sort_order_ascending
        self.sort_order_button.setText("昇順" if self.sort_order_ascending else "降順")
        self.sort_and_display_current_view() # 現在のビューをソートして表示

    def sort_and_display_current_view(self):
        """現在のビューのデータをソートし、表示を更新する"""
        current_view_index = self.stacked_widget.currentIndex()

        if current_view_index == 0: # ステートビュー
            self.sort_state_files()
            self.display_state_files()
        elif current_view_index == 1: # プロビンスビュー
            self.sort_province_data()
            self.display_province_data()
        elif current_view_index == 2: # 戦略地域ビュー
            self.sort_strategic_region_data()
            self.display_strategic_region_data()

    def _get_sort_key_func(self, data_list_name, key_name):
        """ソート用のキー関数を生成する"""
        reverse = not self.sort_order_ascending
        key_func = None

        if key_name == "ステートID":
            key_func = lambda x: x.get("state_id", -1) # 存在しない場合も考慮
        elif key_name == "プロビンスID":
             key_func = lambda x: int(x.get("province_id", -1))
        elif key_name == "戦略地域ID":
            key_func = lambda x: x.get("strategic_region_id", -1)
        elif key_name == "ステート名":
            key_func = lambda x: x.get("state_name", "").lower()
        elif key_name == "戦略地域名":
            key_func = lambda x: x.get("strategic_region_name", "").lower()
        elif key_name == "ローカライズ名":
            key_func = lambda x: x.get("localized_name", "").lower()
        elif key_name == "領有国":
            key_func = lambda x: x.get("owner", "").lower()
        elif key_name == "人口":
            # manpower は文字列なので数値に変換して比較
            key_func = lambda x: int(x.get("manpower", "0"))
        elif key_name == "地形":
            key_func = lambda x: x.get("terrain_type", "").lower()
        elif key_name == "R":
            key_func = lambda x: int(x.get("r", "0"))
        elif key_name == "G":
            key_func = lambda x: int(x.get("g", "0"))
        elif key_name == "B":
            key_func = lambda x: int(x.get("b", "0"))
        elif key_name == "沿岸":
            key_func = lambda x: x.get("is_coastal", "").lower()

        if key_func:
            data_list = getattr(self, data_list_name) # e.g., self.filtered_state_files_info
            data_list.sort(key=key_func, reverse=reverse)

    def sort_state_files(self):
        self._get_sort_key_func('filtered_state_files_info', self.sort_key)

    def sort_province_data(self):
        self._get_sort_key_func('filtered_province_data', self.sort_key)

    def sort_strategic_region_data(self):
         self._get_sort_key_func('filtered_strategic_region_files_info', self.sort_key)

    def search_data(self):
        """現在のビューのデータを検索し、表示を更新する"""
        search_text = self.search_entry.text().strip()
        search_criteria = self.search_criteria_combo.currentText()
        match_type = self.match_type_combo.currentText()
        current_view_index = self.stacked_widget.currentIndex()

        if not search_text: # 検索語が空なら全件表示
            if current_view_index == 0:
                self.filtered_state_files_info = list(self.state_files_info)
            elif current_view_index == 1:
                self.filtered_province_data = list(self.province_data)
            elif current_view_index == 2:
                self.filtered_strategic_region_files_info = list(self.strategic_region_files_info)
            self.sort_and_display_current_view() # ソートして表示
            return

        # 大文字小文字を区別しない検索のために検索語を小文字に
        search_text_lower = search_text.lower()

        if current_view_index == 0: # ステートビューの検索
            self.filtered_state_files_info = []
            source_data = self.state_files_info
            for item_info in source_data:
                target_value = ""
                if search_criteria == "ステートID":
                    target_value = str(item_info["state_id"])
                elif search_criteria == "ステート名":
                    target_value = item_info["state_name"]
                elif search_criteria == "ローカライズ名":
                    target_value = item_info["localized_name"]
                elif search_criteria == "領有国":
                    target_value = item_info["owner"]
                elif search_criteria == "人口":
                    target_value = item_info["manpower"]
                elif search_criteria == "プロビンス":
                    # プロビンスリスト内のいずれかと一致すればマッチ
                    if any(search_text in p for p in item_info["provinces"]):
                         self.filtered_state_files_info.append(item_info)
                    continue # 通常の比較はスキップ

                # 通常のフィールド比較
                target_value_lower = target_value.lower()
                match = False
                if match_type == "完全一致":
                    if target_value_lower == search_text_lower:
                        match = True
                elif match_type == "部分一致":
                    if search_text_lower in target_value_lower:
                        match = True

                if match:
                    self.filtered_state_files_info.append(item_info)
            self.sort_and_display_current_view()

        elif current_view_index == 1: # プロビンスビューの検索
            self.filtered_province_data = []
            source_data = self.province_data
            for item_info in source_data:
                target_value = ""
                if search_criteria == "プロビンスID":
                    target_value = item_info["province_id"]
                elif search_criteria == "地形":
                    target_value = item_info["terrain_type"]
                elif search_criteria == "ステートID":
                    target_value = str(item_info["state_id"]) if item_info["state_id"] != -1 else ""
                elif search_criteria == "ステート名": # 追加
                    target_value = item_info["state_name"]
                elif search_criteria == "ローカライズ名": # 追加
                    target_value = item_info["localized_name"]

                target_value_lower = target_value.lower()
                match = False
                if match_type == "完全一致":
                    if target_value_lower == search_text_lower:
                        match = True
                elif match_type == "部分一致":
                    if search_text_lower in target_value_lower:
                        match = True

                if match:
                    self.filtered_province_data.append(item_info)
            self.sort_and_display_current_view()

        elif current_view_index == 2: # 戦略地域ビューの検索
            self.filtered_strategic_region_files_info = []
            source_data = self.strategic_region_files_info
            for item_info in source_data:
                target_value = ""
                if search_criteria == "戦略地域ID":
                    target_value = str(item_info["strategic_region_id"])
                elif search_criteria == "戦略地域名":
                    target_value = item_info["strategic_region_name"]
                elif search_criteria == "ローカライズ名":
                    target_value = item_info["localized_name"]
                elif search_criteria == "プロビンス": # 追加
                     if any(search_text in p for p in item_info["provinces"]):
                         self.filtered_strategic_region_files_info.append(item_info)
                     continue

                target_value_lower = target_value.lower()
                match = False
                if match_type == "完全一致":
                    if target_value_lower == search_text_lower:
                        match = True
                elif match_type == "部分一致":
                    if search_text_lower in target_value_lower:
                        match = True

                if match:
                    self.filtered_strategic_region_files_info.append(item_info)
            self.sort_and_display_current_view()


    def show_context_menu(self, point):
        sender_widget = self.sender() # 右クリックされたTreeWidget
        item = sender_widget.itemAt(point)
        print(f"\n--- show_context_menu called on {sender_widget.objectName() if sender_widget else 'None'} at {point} ---")

        if not item:
            print("No item at the clicked point.")
            self.current_item = None
            return

        self.current_item = item # 選択中のアイテムを保持 (これがアクション実行時に使われる)
        print(f"Item found: {item.text(0)} (Widget: {sender_widget.objectName()})")
        menu = QMenu(self)

        try: # メニュー構築中のエラーをキャッチ
            if sender_widget == self.tree_widget: # ステートビュー
                state_id_str = item.text(0)
                print(f"State tree item clicked: ID={state_id_str}")
                state_id = int(state_id_str) # ValueError の可能性
                # find_state_info_by_id は self.state_files_info を検索
                state_info = self.find_state_info_by_id(state_id)
                if not state_info:
                    print(f"Error: State info not found for ID {state_id} in context menu setup.")
                    # QMessageBox 等で通知しても良い
                    return # 情報がなければメニュー表示しない

                print("Adding state actions...")
                # アクション1: VSCodeで開く
                action_open_vscode = QAction("VSCodeで開く (State)", self)
                # ラムダはアクション実行時の state_info["filename"] を使う
                action_open_vscode.triggered.connect(lambda: self.open_file_in_vscode(self.state_dir, state_info["filename"]))
                menu.addAction(action_open_vscode)

                # アクション2: 領有国を表示
                action_show_owner = QAction("領有国を表示", self)
                # 専用メソッドがあるので直接接続
                action_show_owner.triggered.connect(self.show_owner_country_list_from_menu)
                menu.addAction(action_show_owner)

                # アクション3: プロビンス一覧
                action_show_provinces = QAction("プロビンス一覧", self)
                # 専用メソッドがあるので直接接続
                action_show_provinces.triggered.connect(self.show_state_province_list_from_menu)
                menu.addAction(action_show_provinces)

                # アクション4: プロビンス移譲
                action_transfer_provinces = QAction("プロビンス移譲...", self)
                # 専用メソッドがあるので直接接続
                action_transfer_provinces.triggered.connect(self.show_transfer_province_dialog)
                menu.addAction(action_transfer_provinces)
                print("State actions added.")

            elif sender_widget == self.province_tree_widget: # プロビンスビュー
                province_id = item.text(0)
                state_id_str = item.text(6) # ステートID列
                print(f"Province tree item clicked: ID={province_id}, StateID='{state_id_str}'")
                print("Adding province actions...")

                # アクション1: 所属ステートを開く
                if state_id_str != "N/A":
                    try:
                        state_id = int(state_id_str)
                        state_info = self.find_state_info_by_id(state_id)
                        if state_info:
                            loc_name = state_info.get('localized_name', state_info.get('state_name', 'N/A'))
                            action_open_state = QAction(f"所属ステートを開く ({loc_name})", self)
                            # filename をラムダにキャプチャさせる
                            state_filename = state_info["filename"]
                            action_open_state.triggered.connect(lambda: self.open_file_in_vscode(self.state_dir, state_filename))
                            menu.addAction(action_open_state)
                        else:
                            print(f"Warning: State info not found for state ID {state_id} (from province view).")
                    except ValueError:
                         print(f"Error: Invalid state ID '{state_id_str}' in province view.")
                else:
                     print("Province has no associated state ID (N/A).")


                # アクション2: 所属戦略地域を開く
                region_info = self.find_strategic_region_by_province(province_id)
                if region_info:
                    loc_name = region_info.get('localized_name', region_info.get('strategic_region_name', 'N/A'))
                    action_open_region = QAction(f"所属戦略地域を開く ({loc_name})", self)
                    # region_name をラムダにキャプチャさせる
                    region_filename = region_info["strategic_region_name"] + ".txt"
                    action_open_region.triggered.connect(lambda: self.open_file_in_vscode(self.strategic_regions_dir, region_filename))
                    menu.addAction(action_open_region)
                else:
                    print(f"Province {province_id} does not belong to any known strategic region.")
                print("Province actions added.")


            elif sender_widget == self.strategic_region_tree_widget: # 戦略地域ビュー
                region_id_str = item.text(0)
                print(f"Strategic region tree item clicked: ID={region_id_str}")
                region_id = int(region_id_str) # ValueError の可能性
                region_info = self.find_strategic_region_info_by_id(region_id)
                if not region_info:
                    print(f"Error: Region info not found for ID {region_id} in context menu setup.")
                    # QMessageBox 等で通知しても良い
                    return

                print("Adding strategic region actions...")
                # アクション1: VSCodeで開く
                action_open_vscode_region = QAction("VSCodeで開く (Region)", self)
                region_filename = region_info["strategic_region_name"] + ".txt"
                action_open_vscode_region.triggered.connect(lambda: self.open_file_in_vscode(self.strategic_regions_dir, region_filename))
                menu.addAction(action_open_vscode_region)

                # アクション2: 所属ステート一覧
                action_show_states = QAction("所属ステート一覧", self)
                action_show_states.triggered.connect(self.show_belonging_state_list_from_menu)
                menu.addAction(action_show_states)

                # アクション3: プロビンス一覧 (Region)
                action_show_region_provinces = QAction("プロビンス一覧 (Region)", self)
                action_show_region_provinces.triggered.connect(self.show_region_province_list_from_menu)
                menu.addAction(action_show_region_provinces)

                # アクション4: 領有国を表示 (Region)
                action_show_owner_region = QAction("領有国を表示 (Region)", self)
                action_show_owner_region.triggered.connect(self.show_owner_country_list_from_menu)
                menu.addAction(action_show_owner_region)
                print("Strategic region actions added.")

            # --- メニュー表示 ---
            if menu.actions(): # アクションが追加されていれば表示
                print(f"Executing context menu with {len(menu.actions())} actions...")
                # グローバル座標に変換して表示
                global_point = sender_widget.viewport().mapToGlobal(point)
                print(f"Showing menu at global coordinates: {global_point}")
                menu.exec_(global_point)
            else:
                print("No actions were added to the context menu.")

        except ValueError:
             # ID変換エラー (主に int(item.text(0)) で発生)
             id_str = item.text(0)
             print(f"Error: Invalid ID format '{id_str}' during context menu setup.")
             from PyQt5.QtWidgets import QMessageBox
             QMessageBox.critical(self, "データエラー", f"アイテムのIDが無効な形式です: '{id_str}'")
        except Exception as e:
             # その他の予期せぬエラー
             print(f"Error during context menu setup or execution: {e}")
             import traceback
             traceback.print_exc()
             from PyQt5.QtWidgets import QMessageBox
             QMessageBox.critical(self, "エラー", f"コンテキストメニューの表示中にエラーが発生しました:\n{e}")

    def open_file_in_vscode(self, directory, filename):
        """指定されたファイルをVSCodeで開く"""
        print(f"--- open_file_in_vscode called ---")
        print(f"Directory: {directory}, Filename: {filename}")
        if not filename:
            print("エラー: ファイル名が指定されていません。")
            # ユーザー通知 (必要なら)
            # from PyQt5.QtWidgets import QMessageBox
            # QMessageBox.warning(self, "エラー", "ファイル名が不明なため、ファイルを開けません。")
            return
        if not directory:
             print("エラー: ディレクトリが指定されていません。")
             # QMessageBox.warning(self, "エラー", "ディレクトリが不明なため、ファイルを開けません。")
             return

        filepath = os.path.join(directory, filename)
        # ファイルパスを絶対パスに変換し、クォートで囲む (スペース対策)
        absolute_filepath = os.path.abspath(filepath)
        command = f"code \"{absolute_filepath}\""
        print(f"Attempting to open: {absolute_filepath}") # デバッグ用
        print(f"Executing command: {command}") # デバッグ用
        try:
            # ファイルが存在するか確認 (任意だがあると親切)
            if not os.path.exists(absolute_filepath):
                print(f"警告: ファイルが存在しません: {absolute_filepath}")
                # ユーザーに通知
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "ファイル未検出", f"ファイルが見つかりませんでした:\n{absolute_filepath}")
                return # ファイルがない場合はここで終了する

            result = os.system(command)
            print(f"os.system returned: {result}") # 戻り値を確認
            if result != 0:
                print(f"VSCodeでのファイルオープンエラー。コマンド: {command}, 戻り値: {result}")
                # エラー時の代替処理（例：ファイルパスを表示）
                print(f"ファイルパス: {absolute_filepath}")
                # ユーザーに通知
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "VSCodeエラー", f"VSCodeでのファイル起動に失敗しました。\n(コマンド: {command})\n(戻り値: {result})\n\nVSCodeがインストールされ、PATHが通っているか確認してください。")
        except Exception as e:
             print(f"VSCodeの実行中にエラーが発生しました: {e}")
             print(f"ファイルパス: {absolute_filepath}")
             # ユーザーに通知
             from PyQt5.QtWidgets import QMessageBox
             QMessageBox.critical(self, "実行エラー", f"VSCodeの起動中にエラーが発生しました:\n{e}")

    # show_province_list_from_menu はステートビュー専用なので名前を明確化
    def show_state_province_list_from_menu(self):
        """ステートビューのコンテキストメニューからプロビンス一覧を表示"""
        print("--- show_state_province_list_from_menu called ---")
        if self.current_item: # current_item が None でないことを確認
            parent_widget = self.current_item.treeWidget()
            print(f"Current item belongs to: {parent_widget.objectName() if parent_widget else 'None'}")
            # ステートツリーのアイテムか確認
            if parent_widget == self.tree_widget:
                state_id_str = self.current_item.text(0)
                print(f"State ID string: {state_id_str}")
                try:
                    state_id = int(state_id_str)
                    # state_info はキャッシュから取得 (フィルタリングの影響を受けない)
                    state_info = self.find_state_info_by_id(state_id)
                    if state_info:
                        # プロビンスリストを取得し、数値としてソート
                        province_list = sorted([p for p in state_info["provinces"] if p.isdigit()], key=int)
                        print(f"Found {len(province_list)} provinces for state {state_id}. Showing dialog...")
                        dialog = ProvinceListDialog(province_list, self)
                        dialog.exec_()
                    else:
                        # これは通常発生しないはず (UI上のアイテムに対応するデータがない)
                        print(f"Error: State info not found for ID {state_id}.")
                        # from PyQt5.QtWidgets import QMessageBox
                        # QMessageBox.warning(self, "データエラー", f"ステートID {state_id} の内部情報が見つかりませんでした。")
                except ValueError:
                    print(f"Error: Invalid state ID format '{state_id_str}'.")
                    # from PyQt5.QtWidgets import QMessageBox
                    # QMessageBox.critical(self, "データエラー", f"ステートリストのアイテムに無効なID '{state_id_str}' が含まれています。")
                except Exception as e:
                    print(f"Error in show_state_province_list_from_menu: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("Item does not belong to the state tree.")
        else:
            print("self.current_item is None.")

    # 戦略地域ビュー用のプロビンス一覧表示
    def show_region_province_list_from_menu(self):
        """戦略地域ビューのコンテキストメニューからプロビンス一覧を表示"""
        print("--- show_region_province_list_from_menu called ---")
        if self.current_item:
            parent_widget = self.current_item.treeWidget()
            print(f"Current item belongs to: {parent_widget.objectName() if parent_widget else 'None'}")
            # 戦略地域ツリーのアイテムか確認
            if parent_widget == self.strategic_region_tree_widget:
                region_id_str = self.current_item.text(0)
                print(f"Region ID string: {region_id_str}")
                try:
                    region_id = int(region_id_str)
                    region_info = self.find_strategic_region_info_by_id(region_id)
                    if region_info:
                        # プロビンスリストを取得し、数値としてソート
                        province_list = sorted([p for p in region_info["provinces"] if p.isdigit()], key=int)
                        print(f"Found {len(province_list)} provinces for region {region_id}. Showing dialog...")
                        dialog = ProvinceListDialog(province_list, self)
                        dialog.exec_()
                    else:
                        print(f"Error: Strategic region info not found for ID {region_id}.")
                        # from PyQt5.QtWidgets import QMessageBox
                        # QMessageBox.warning(self, "データエラー", f"戦略地域ID {region_id} の内部情報が見つかりませんでした。")
                except ValueError:
                    print(f"Error: Invalid region ID format '{region_id_str}'.")
                    # from PyQt5.QtWidgets import QMessageBox
                    # QMessageBox.critical(self, "データエラー", f"戦略地域リストのアイテムに無効なID '{region_id_str}' が含まれています。")
                except Exception as e:
                     print(f"Error in show_region_province_list_from_menu: {e}")
                     import traceback
                     traceback.print_exc()
            else:
                print("Item does not belong to the strategic region tree.")
        else:
            print("self.current_item is None.")

    # show_province_list_from_menu を汎用化 (senderによって挙動を変える)
    def show_province_list_from_menu(self):
         sender_widget = self.sender()
         if not self.current_item: return

         if sender_widget == self.tree_widget: # ステートビュー
             self.show_state_province_list_from_menu()
         elif sender_widget == self.strategic_region_tree_widget: # 戦略地域ビュー
             self.show_region_province_list_from_menu()


    def load_strategic_regions(self):
        self.strategic_region_files_info = []
        if not os.path.isdir(self.strategic_regions_dir):
            print(f"警告: 戦略地域ディレクトリが見つかりません: {self.strategic_regions_dir}")
            return

        for filename in os.listdir(self.strategic_regions_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(self.strategic_regions_dir, filename)
                region_info = self.parse_strategic_region_file(filepath)
                if region_info:
                    self.strategic_region_files_info.append(region_info)

    def parse_strategic_region_file(self, filepath):
        filename = os.path.basename(filepath)
        # ファイル名から拡張子を除いた部分をデフォルトの地域名とする
        strategic_region_name = os.path.splitext(filename)[0]

        strategic_region_id = -1
        provinces = []
        name_key = strategic_region_name # デフォルトのキーはファイル名と同じと仮定
        localized_name = f"<{name_key}?>" # デフォルト表示

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # strategic_region={ ... } ブロックの内外を検索
                id_match = re.search(r"^\s*id\s*=\s*(\d+)", content, re.MULTILINE)
                if id_match:
                    strategic_region_id = int(id_match.group(1))

                name_match = re.search(r"^\s*name\s*=\s*\"(.*?)\"", content, re.MULTILINE)
                if name_match:
                    name_key = name_match.group(1)

                provinces_match = re.search(r"^\s*provinces\s*=\s*{([\s\d]*)}", content, re.MULTILINE)
                if provinces_match:
                    provinces = provinces_match.group(1).split()
                    provinces = [p for p in provinces if p.isdigit()] # 数値のみ保持

                # ローカライズキーで検索
                localized_name = self.localisation_strings.get(name_key, f"<{name_key}?>")

        except Exception as e:
            print(f"戦略地域ファイル解析エラー {filepath}: {e}")
            return None

        return {
            "strategic_region_id": strategic_region_id,
            "strategic_region_name": strategic_region_name, # ファイル名由来の名前
            "localized_name": localized_name, # ローカライズ名 or <key?>
            "name_key": name_key, # regionファイル内の name= の値
            "provinces": provinces, # プロビンスIDのリスト (文字列)
        }

    def display_strategic_region_data(self):
        self.strategic_region_tree_widget.clear()
        display_data = self.filtered_strategic_region_files_info

        for region_info in display_data:
            item = QTreeWidgetItem([
                str(region_info["strategic_region_id"]),
                region_info["strategic_region_name"], # ファイル名由来
                region_info["localized_name"] # ローカライズ名 or <key?>
            ])
            self.strategic_region_tree_widget.addTopLevelItem(item)

    def show_owner_country_list_from_menu(self):
        """コンテキストメニューから領有国一覧を表示 (ステート/戦略地域に対応)"""
        print("--- show_owner_country_list_from_menu called ---")
        if not self.current_item:
            print("self.current_item is None.")
            return

        parent_widget = self.current_item.treeWidget()
        print(f"Current item belongs to: {parent_widget.objectName() if parent_widget else 'None'}")

        owner_country_set = set() # 重複を避ける

        try:
            if parent_widget == self.tree_widget: # ステートビュー
                state_id_str = self.current_item.text(0)
                print(f"State ID string: {state_id_str}")
                state_id = int(state_id_str)
                state_info = self.find_state_info_by_id(state_id)
                if state_info and state_info["owner"] != "N/A":
                    print(f"Owner found for state {state_id}: {state_info['owner']}")
                    owner_country_set.add(state_info["owner"])
                elif state_info:
                     print(f"State {state_id} has no owner ('N/A').")
                else:
                     print(f"State info not found for ID {state_id}.") # Should not happen


            elif parent_widget == self.strategic_region_tree_widget: # 戦略地域ビュー
                region_id_str = self.current_item.text(0)
                print(f"Region ID string: {region_id_str}")
                region_id = int(region_id_str)
                region_info = self.find_strategic_region_info_by_id(region_id)
                if region_info:
                    print(f"Checking provinces for region {region_id}...")
                    found_owners = set()
                    for province_id in region_info["provinces"]:
                        state_id, _, _ = self.get_state_info_for_province(province_id)
                        if state_id != -1:
                            state_info = self.find_state_info_by_id(state_id)
                            if state_info and state_info["owner"] != "N/A":
                                found_owners.add(state_info["owner"])
                    owner_country_set.update(found_owners) # setを更新
                    print(f"Found owners in region {region_id}: {owner_country_set}")
                else:
                    print(f"Region info not found for ID {region_id}.") # Should not happen

            if owner_country_set:
                owner_list = sorted(list(owner_country_set))
                print(f"Showing owner country dialog for: {owner_list}")
                dialog = OwnerCountryDialog(owner_list, self)
                dialog.exec_()
            else:
                print("No owner countries found to display.")
                # ユーザーへの通知
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "情報", "表示できる領有国が見つかりませんでした。")

        except ValueError:
            # ID変換エラー
            id_str = self.current_item.text(0)
            print(f"Error: Invalid ID format '{id_str}'.")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "データエラー", f"アイテムのIDが無効な形式です: '{id_str}'")
        except Exception as e:
            print(f"Error in show_owner_country_list_from_menu: {e}")
            import traceback
            traceback.print_exc()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "エラー", f"領有国リストの表示中にエラーが発生しました:\n{e}")

    def show_belonging_state_list_from_menu(self):
        """戦略地域ビューのコンテキストメニューから所属ステート一覧を表示"""
        print("--- show_belonging_state_list_from_menu called ---")
        if not self.current_item:
            print("self.current_item is None.")
            return

        parent_widget = self.current_item.treeWidget()
        print(f"Current item belongs to: {parent_widget.objectName() if parent_widget else 'None'}")

        belonging_state_set = set() # 表示用文字列を格納 (例: "ステート名 (ID)")

        try:
            if parent_widget == self.strategic_region_tree_widget: # 戦略地域ビューの場合のみ
                region_id_str = self.current_item.text(0)
                print(f"Region ID string: {region_id_str}")
                region_id = int(region_id_str)
                region_info = self.find_strategic_region_info_by_id(region_id)
                if region_info:
                    print(f"Checking provinces for region {region_id}...")
                    found_states = set()
                    for province_id in region_info["provinces"]:
                        state_id, _, _ = self.get_state_info_for_province(province_id)
                        if state_id != -1:
                            state_info = self.find_state_info_by_id(state_id)
                            if state_info:
                                # get()で安全にアクセスし、なければstate_nameを使う
                                loc_name = state_info.get('localized_name', state_info.get('state_name', 'N/A'))
                                display_name = f"{loc_name} ({state_info['state_id']})"
                                found_states.add(display_name)
                    belonging_state_set.update(found_states)
                    print(f"Found belonging states in region {region_id}: {belonging_state_set}")
                else:
                    print(f"Region info not found for ID {region_id}.") # Should not happen

                if belonging_state_set:
                    state_list = sorted(list(belonging_state_set))
                    print(f"Showing belonging state dialog for: {state_list}")
                    dialog = BelongingStateDialog(state_list, self)
                    dialog.exec_()
                else:
                    print("No belonging states found to display.")
                    # ユーザーへの通知
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.information(self, "情報", "表示できる所属ステートが見つかりませんでした。")
            else:
                 print("This action is only available for the strategic region tree.")

        except ValueError:
            # ID変換エラー
            id_str = self.current_item.text(0)
            print(f"Error: Invalid ID format '{id_str}'.")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "データエラー", f"アイテムのIDが無効な形式です: '{id_str}'")
        except Exception as e:
            print(f"Error in show_belonging_state_list_from_menu: {e}")
            import traceback
            traceback.print_exc()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "エラー", f"所属ステートリストの表示中にエラーが発生しました:\n{e}")

    def show_transfer_province_dialog(self):
        # --- デバッグ出力強化 ---
        print("--- show_transfer_province_dialog called ---")
        print(f"Current item: {self.current_item}")
        parent_widget = None
        if self.current_item:
            try:
                # QTreeWidgetItemがどのTreeWidgetに属しているか取得
                parent_widget = self.current_item.treeWidget()
                print(f"Current item text(0): {self.current_item.text(0)}")
                print(f"Parent widget of current_item: {parent_widget}")
            except Exception as e:
                print(f"Error accessing current_item properties: {e}")
                self.current_item = None # 問題がある場合は None にリセット
        else:
            print("self.current_item is None.")

        # --- 条件分岐の修正 ---
        # クリックされたアイテムがステートツリーウィジェット (self.tree_widget) に属しているか確認
        if self.current_item and parent_widget == self.tree_widget:
            print("Condition met: current_item exists and belongs to the state tree.")
            state_id_str = self.current_item.text(0)
            try:
                print(f"Attempting to get state_id from: {state_id_str}")
                state_id = int(state_id_str)
                print(f"Looking for state info for ID: {state_id}")
                # find_state_info_by_id は self.state_files_info を検索するため、
                # フィルタリングされたリストではなく、元のリストを使うのが適切
                state_info = self.find_state_info_by_id(state_id)
                if state_info:
                    print(f"State info found: {state_info['filename']}")
                    # プロビンスリストを取得し、数値としてソート
                    province_list = sorted([p for p in state_info["provinces"] if p.isdigit()], key=int)
                    print(f"Provinces to show in dialog ({len(province_list)} items): {province_list[:20]}...") # Display first 20 or fewer
                    # ダイアログを表示
                    dialog = ProvinceTransferDialog(province_list, self)
                    print("ProvinceTransferDialog created. Executing...")
                    result = dialog.exec_()
                    print(f"ProvinceTransferDialog finished with result: {result} ({'Accepted' if result == QDialog.Accepted else 'Rejected'})") # 結果をわかりやすく表示

                    if result == QDialog.Accepted:
                        selected_provinces = dialog.get_selected_provinces()
                        print(f"Provinces selected: {selected_provinces}")
                        if selected_provinces:
                            # 次のダイアログへ進む前に移譲元情報を渡す
                            self.show_target_state_dialog(selected_provinces, state_info)
                        else:
                             print("No provinces selected in the dialog.")
                    else:
                        print("ProvinceTransferDialog cancelled or closed by user.")

                else:
                    # このエラーは通常発生しにくい（リストに表示されているアイテムの情報がないため）
                    print(f"エラー: ステートリスト上のアイテムに対応するステート情報 (ID: {state_id}) が内部データに見つかりません。")
                    # ユーザーへの通知
                    # QMessageBox.warning(self, "データエラー", f"ステートID {state_id} の内部情報が見つかりませんでした。")

            except ValueError:
                 print(f"エラー: ステートアイテムから有効な数値IDを取得できませんでした: '{state_id_str}'")
                 # ユーザーへの通知
                 # QMessageBox.critical(self, "データエラー", f"ステートリストのアイテムに無効なID '{state_id_str}' が含まれています。")
            except Exception as e:
                 print(f"プロビンス移譲ダイアログ表示中に予期せぬエラーが発生しました: {e}")
                 import traceback
                 traceback.print_exc() # 詳細なトレースバックを出力
                 # ユーザーへの通知
                 # from PyQt5.QtWidgets import QMessageBox
                 # QMessageBox.critical(self, "予期せぬエラー", f"ダイアログ表示中にエラーが発生しました:\n{e}")
        else:
            # 条件が満たされなかった理由を出力
            print("Condition not met to show transfer dialog.")
            if not self.current_item:
                print("Reason: No item was right-clicked (self.current_item is None).")
            elif parent_widget != self.tree_widget:
                print(f"Reason: The right-clicked item belongs to '{parent_widget.objectName() if parent_widget else 'Unknown Widget'}', not the state tree ('{self.tree_widget.objectName()}'). Transfer is only allowed from the state tree.")
            # デバッグ用にメッセージボックスを表示することも可能
            # from PyQt5.QtWidgets import QMessageBox
            # QMessageBox.information(self, "情報", "プロビンス移譲はステートビューのアイテムを右クリックした場合のみ可能です。")

    def show_target_state_dialog(self, selected_provinces, source_state_info):
        dialog = TargetStateDialog(self, source_state_info) # source_state_info を渡す
        result = dialog.exec_()
        if result == QDialog.Accepted:
            target_state_id = dialog.get_target_state_id()
            if target_state_id is not None:
                if target_state_id == source_state_info["state_id"]:
                     print("エラー: 移譲元と移譲先のステートが同じです。")
                     # 必要なら再度ダイアログを表示するなどの処理
                     # self.show_target_state_dialog(selected_provinces, source_state_info)
                     return
                # 移譲処理を実行
                self.transfer_provinces(selected_provinces, source_state_info["state_id"], target_state_id)
            else:
                 print("エラー: 無効な移譲先ステートIDが入力されました。")
                 # 必要なら再度ダイアログを表示
                 # self.show_target_state_dialog(selected_provinces, source_state_info)
        # else: # Rejected (戻る or キャンセル)
             # "戻る" が押された場合、 ProvinceTransferDialog を再表示するならここで処理
             # キャンセルの場合は何もしない

    def transfer_provinces(self, selected_provinces, source_state_id, target_state_id):
        print(f"移譲開始: {len(selected_provinces)}個のプロビンスを State {source_state_id} から State {target_state_id} へ") # Debug

        if not selected_provinces:
            print("エラー: 移譲するプロビンスが選択されていません。")
            return

        source_state_info = self.find_state_info_by_id(source_state_id)
        target_state_info = self.find_state_info_by_id(target_state_id)

        if not source_state_info:
            print(f"エラー: 移譲元ステート {source_state_id} が見つかりません。")
            return
        if not target_state_info:
            print(f"エラー: 移譲先ステート {target_state_id} が見つかりません。")
            return

        # --- 戦略地域の更新処理 ---
        print("戦略地域の更新処理を開始...")
        updated_regions = set() # 更新した戦略地域ファイル名を記録

        for province_id in selected_provinces:
            print(f"  プロビンス {province_id} の戦略地域を処理中...") # Debug
            source_region_info = self.find_strategic_region_by_province(province_id)

            # 移譲先ステートが所属する戦略地域を見つける
            # 移譲先ステートに既にプロビンスがあれば、その最初のプロビンスの地域を使う
            # なければ、移譲先ステートのIDなどから推測するか、デフォルトを決める必要がある
            target_region_info = None
            if target_state_info["provinces"]:
                # 移譲先ステートの既存プロビンスがどの地域に属するか確認
                for existing_prov_id in target_state_info["provinces"]:
                    target_region_info = self.find_strategic_region_by_province(existing_prov_id)
                    if target_region_info:
                        break # 最初に見つかった地域を使用
            # else:
                # 移譲先ステートにプロビンスがない場合のフォールバック処理が必要ならここに記述
                # 例: 首都プロビンスから地域を決定、など

            if source_region_info:
                print(f"    移譲元地域: {source_region_info['strategic_region_name']} ({source_region_info['strategic_region_id']})") # Debug
                if target_region_info:
                    print(f"    移譲先地域候補: {target_region_info['strategic_region_name']} ({target_region_info['strategic_region_id']})") # Debug
                else:
                    print("    移譲先地域候補が見つかりません。") # Debug

                # 移譲元と移譲先候補が異なる場合、または移譲先候補がない場合も移譲元からは削除する
                if not target_region_info or source_region_info["strategic_region_id"] != target_region_info["strategic_region_id"]:
                    print(f"    移譲元地域 {source_region_info['strategic_region_name']} からプロビンス {province_id} を削除します。") # Debug
                    try:
                        source_region_info["provinces"].remove(str(province_id)) # removeは要素が存在しないとValueError
                        updated_regions.add(source_region_info["strategic_region_name"])
                    except ValueError:
                        print(f"    警告: プロビンス {province_id} は移譲元地域 {source_region_info['strategic_region_name']} に見つかりませんでした（無視します）。")

                    # 移譲先地域が見つかっていれば追加
                    if target_region_info:
                        print(f"    移譲先地域 {target_region_info['strategic_region_name']} にプロビンス {province_id} を追加します。") # Debug
                        if str(province_id) not in target_region_info["provinces"]:
                            target_region_info["provinces"].append(str(province_id))
                            updated_regions.add(target_region_info["strategic_region_name"])
                        else:
                             print(f"    情報: プロビンス {province_id} は既に移譲先地域 {target_region_info['strategic_region_name']} に存在します。")
                    else:
                        # target_region_info が None の場合
                        print(f"    警告: プロビンス {province_id} の移譲先戦略地域が見つかりませんでした。"
                              f"ステート {target_state_id} にプロビンスがないか、既存プロビンスが地域に未割り当ての可能性があります。"
                              f"このプロビンスはどの戦略地域にも属さない状態になります。")
                else:
                     print(f"    情報: プロビンス {province_id} は移譲元と移譲先候補の地域が同じ ({source_region_info['strategic_region_name']}) なので、戦略地域の移動は行いません。")

            else:
                # source_region_info が None の場合
                print(f"    警告: プロビンス {province_id} は移譲元の時点でどの戦略地域にも属していませんでした。")
                # この場合でも、移譲先の地域が見つかれば追加する
                if target_region_info:
                     print(f"    移譲先地域 {target_region_info['strategic_region_name']} にプロビンス {province_id} を追加します。") # Debug
                     if str(province_id) not in target_region_info["provinces"]:
                         target_region_info["provinces"].append(str(province_id))
                         updated_regions.add(target_region_info["strategic_region_name"])
                     else:
                          print(f"    情報: プロビンス {province_id} は既に移譲先地域 {target_region_info['strategic_region_name']} に存在します。")
                else:
                     print(f"    警告: プロビンス {province_id} の移譲先戦略地域も見つかりませんでした。戦略地域の変更はありません。")


        # 更新があった戦略地域ファイルのみ書き込み
        print(f"更新が必要な戦略地域ファイル: {updated_regions}") # Debug
        for region_name in updated_regions:
             region_info_to_update = next((r for r in self.strategic_region_files_info if r["strategic_region_name"] == region_name), None)
             if region_info_to_update:
                 # provinces リストをソートしてから書き込む
                 region_info_to_update["provinces"] = sorted(list(set(region_info_to_update["provinces"])), key=int) # 数値としてソート
                 self.update_strategic_region_file(region_info_to_update)


        # --- ステートファイルの更新処理 ---
        print("ステートファイルの更新処理を開始...")

        # プロビンスを移譲元から削除
        print(f"  移譲元ステート {source_state_id} からプロビンスを削除...") # Debug
        original_source_provinces = set(source_state_info["provinces"])
        provinces_to_remove = set(selected_provinces)
        source_state_info["provinces"] = sorted(list(original_source_provinces - provinces_to_remove), key=int) # 数値としてソート
        print(f"    削除後のプロビンス数: {len(source_state_info['provinces'])}") # Debug

        # プロビンスを移譲先に追加
        print(f"  移譲先ステート {target_state_id} にプロビンスを追加...") # Debug
        original_target_provinces = set(target_state_info["provinces"])
        provinces_to_add = set(selected_provinces)
        target_state_info["provinces"] = sorted(list(original_target_provinces | provinces_to_add), key=int) # 数値としてソート
        print(f"    追加後のプロビンス数: {len(target_state_info['provinces'])}") # Debug


        # ステートファイルを更新
        print(f"  移譲元ステートファイル {source_state_info['filename']} を更新...") # Debug
        self.update_state_file(source_state_info)
        print(f"  移譲先ステートファイル {target_state_info['filename']} を更新...") # Debug
        self.update_state_file(target_state_info)

        # --- データと表示を更新 ---
        print("データと表示の更新中...")
        # 変更があった可能性のあるデータを再読み込み
        self.load_state_files() # state_files_info を最新に
        self.load_province_data() # province_data のステート割り当てを最新に
        self.load_strategic_regions() # strategic_region_files_info を最新に

        # フィルタリングリストも更新
        current_search_text = self.search_entry.text() # 検索状態を維持するため
        if not current_search_text: # 検索中でなければ全件リストで更新
            self.filtered_state_files_info = list(self.state_files_info)
            self.filtered_province_data = list(self.province_data)
            self.filtered_strategic_region_files_info = list(self.strategic_region_files_info)
        else:
            # 検索中の場合は再検索を実行してフィルタリングリストを更新
            self.search_data()
            # search_data内でソートと表示更新が行われるので、以下の呼び出しは不要

        # 現在のビューの表示を更新 (search_dataを呼ばなかった場合のみ必要)
        if not current_search_text:
            self.sort_and_display_current_view()

        print("プロビンス移譲処理完了。")


    def update_state_file(self, state_info):
        filepath = os.path.join(self.state_dir, state_info["filename"])
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content_lines = f.readlines()

            updated_lines = []
            in_provinces_block = False
            provinces_block_found = False # provinces = { が見つかったか

            for line in content_lines:
                # provinces = { } ブロックの開始行かチェック
                if re.search(r"^\s*provinces\s*=\s*{", line): # 行頭からのマッチに変更
                    provinces_block_found = True
                    # プロビンスリストが空でなければブロックを書き出す
                    if state_info["provinces"]:
                        in_provinces_block = True
                        updated_lines.append(line.split('{')[0] + '{\n') # { の前までと改行を追加
                        # 新しいプロビンスリストを追加 (ソート済み)
                        for province in state_info["provinces"]:
                            updated_lines.append(f"\t\t{province}\n") # インデント調整 (必要なら)
                        # 閉じ括弧は後で追加
                    else:
                        # プロビンスリストが空なら provinces = {} 行自体をコメントアウトまたは削除
                        # updated_lines.append("#" + line) # コメントアウトする場合
                        pass # 何も追加しない（削除する場合）
                    continue # 元の行はスキップ

                # provinces = { } ブロックの内側かチェック
                if in_provinces_block:
                    if '}' in line:
                        in_provinces_block = False
                        # 閉じ括弧を追加 (プロビンスがあった場合のみ)
                        if state_info["provinces"]:
                             updated_lines.append(line.split('}')[0].rstrip() + '\t}\n') # インデントされた閉じ括弧
                    # ブロック内の古いプロビンス行はスキップ
                    continue

                # provinces ブロック以外の行はそのまま追加
                updated_lines.append(line)

            # ファイルの最後に provinces = { } が見つからなかった場合で、
            # かつプロビンスリストが空でない場合に追加する
            if not provinces_block_found and state_info["provinces"]:
                 # state={ } ブロックの中か、ファイルのルートレベルか？
                 # 簡単のため、ファイルの末尾に追加する
                 updated_lines.append('\n\tprovinces = {\n') # state={ の中を想定したインデント
                 for province in state_info["provinces"]:
                     updated_lines.append(f'\t\t{province}\n')
                 updated_lines.append('\t}\n')


            # ファイルに書き込み
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
            print(f"    ファイル {filepath} を更新しました。")

        except Exception as e:
            print(f"ステートファイル更新エラー {filepath}: {e}")

    def find_state_info_by_id(self, state_id):
        """キャッシュされたステート情報からIDで検索"""
        return next((info for info in self.state_files_info if info["state_id"] == state_id), None)

    def find_strategic_region_by_province(self, province_id_str):
        """キャッシュされた戦略地域情報からプロビンスIDで検索"""
        # province_id_str が数値文字列であることを確認
        if not province_id_str.isdigit(): return None

        for region_info in self.strategic_region_files_info:
            # region_info["provinces"] も文字列リストのはず
            if province_id_str in region_info["provinces"]:
                return region_info
        return None

    def find_strategic_region_info_by_id(self, region_id):
         """キャッシュされた戦略地域情報からIDで検索"""
         return next((info for info in self.strategic_region_files_info if info["strategic_region_id"] == region_id), None)


    def update_strategic_region_file(self, region_info):
        filename = region_info["strategic_region_name"] + ".txt"
        filepath = os.path.join(self.strategic_regions_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content_lines = f.readlines()

            updated_lines = []
            in_provinces_block = False
            provinces_block_found = False

            for line in content_lines:
                if re.search(r"^\s*provinces\s*=\s*{", line):
                    provinces_block_found = True
                    if region_info["provinces"]: # プロビンスがある場合のみ
                        in_provinces_block = True
                        updated_lines.append(line.split('{')[0] + '{\n')
                        # 新しいプロビンスリスト (ソート済み)
                        for province in region_info["provinces"]:
                            updated_lines.append(f"\t\t{province}\n") # インデント要確認
                    else:
                        # プロビンスが空なら provinces = {} を削除 or コメントアウト
                        pass # 何も追加しない（削除）
                    continue

                if in_provinces_block:
                    if '}' in line:
                        in_provinces_block = False
                        if region_info["provinces"]:
                             updated_lines.append(line.split('}')[0].rstrip() + '\t}\n') # インデントされた閉じ括弧
                    continue # 古いプロビンス行スキップ

                updated_lines.append(line) # それ以外の行

            # provinces = {} が元々なく、プロビンスがある場合に追加 (ファイルの末尾)
            if not provinces_block_found and region_info["provinces"]:
                 # strategic_region = { } の中を想定
                 updated_lines.append('\n\tprovinces = {\n')
                 for province in region_info["provinces"]:
                     updated_lines.append(f'\t\t{province}\n')
                 updated_lines.append('\t}\n')


            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
            print(f"    戦略地域ファイル {filepath} を更新しました。")

        except Exception as e:
            print(f"戦略地域ファイル更新エラー {filepath}: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StateFileLister()
    ex.show()
    sys.exit(app.exec_())