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
        cancel_button.clicked.connect(self.reject) # キャンセルボタン
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
        self.default_sort_key = self.config.get('UI', 'default_sort_key', fallback='state_id')
        self.default_sort_order_ascending = self.config.getboolean('UI', 'default_sort_order_ascending', fallback=True)

        self.state_files_info = []
        self.filtered_state_files_info = []
        self.sort_key = self.default_sort_key
        self.sort_order_ascending = self.default_sort_order_ascending
        self.localisation_strings = self.load_localisation()
        self.current_item = None

        # プロビンス関連のデータ
        self.strategic_regions_dir = "map/strategicregions" # 戦略地域のディレクトリ (フォルダ名修正)
        self.strategic_region_files_info = []
        self.province_data = []
        self.filtered_province_data = []
        self.definition_csv_path = "map/definition.csv" # パスは適宜変更してください

        self.init_ui()
        self.load_state_files()
        self.filtered_state_files_info = list(self.state_files_info)
        self.display_state_files()

    def load_localisation(self):
        localisation_strings = {}
        filepath = os.path.join(self.localisation_dir, self.localisation_file_name)
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("l_japanese:"):
                        continue
                    if ":" in line and not line.startswith("#"):
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip().strip('"')
                        localisation_strings[key] = value
        except Exception as e:
            print(f"Error loading localisation file {filepath}: {e}")
        return localisation_strings

    def init_ui(self):
        layout = QVBoxLayout()

        # ビュー切り替え用コンボボックス
        self.view_combo = QComboBox()
        self.view_combo.addItem("ステートビュー")
        self.view_combo.addItem("プロビンスビュー")
        self.view_combo.addItem("戦略地域ビュー")
        self.view_combo.currentIndexChanged.connect(self.switch_view)

        # ツールバー
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(self.view_combo) # ビュー切り替えコンボボックスを追加
        toolbar_layout.addStretch()

        # ソート設定
        sort_layout = QHBoxLayout()
        sort_label = QLabel("ソート:")
        sort_layout.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["ステートID", "ステート名", "ローカライズ名", "領有国", "人口", "戦略地域ID", "戦略地域名", "ローカライズ名"])
        self.sort_combo.setCurrentText(self.sort_key) # 設定からデフォルト値を設定

        self.sort_order_button = QPushButton("昇順" if self.sort_order_ascending else "降順")
        self.sort_order_button.clicked.connect(self.toggle_sort_order)
        sort_layout.addWidget(self.sort_order_button)

        # 検索バー
        search_layout = QHBoxLayout()
        search_label = QLabel("検索:")
        search_layout.addWidget(search_label)

        self.search_entry = QLineEdit()
        self.search_entry.returnPressed.connect(self.search_state_files)
        search_layout.addWidget(self.search_entry)

        self.search_criteria_combo = QComboBox()
        self.search_criteria_combo.addItems(["ステートID", "ステート名", "ローカライズ名", "領有国", "人口", "プロビンス", "戦略地域ID", "戦略地域名", "ローカライズ名"])
        search_layout.addWidget(self.search_criteria_combo)

        self.match_type_combo = QComboBox()
        self.match_type_combo.addItems(["部分一致", "完全一致"])
        search_layout.addWidget(self.match_type_combo)

        search_button = QPushButton("検索")
        search_button.clicked.connect(self.search_state_files)
        search_layout.addWidget(search_button)

        # ステートファイルリスト (QTreeWidget)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(5)
        self.tree_widget.setHeaderLabels(["ステートID", "ステート名", "ローカライズ名", "領有国", "人口"])
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu) # コンテキストメニューを有効化
        self.tree_widget.customContextMenuRequested.connect(self.show_context_menu) # シグナルを接続

        # プロビンスリスト (QTreeWidget) - 初期状態では非表示
        self.province_tree_widget = QTreeWidget()
        self.province_tree_widget.setObjectName("province_tree_widget")
        self.province_tree_widget.setColumnCount(9)  # 列数を9に設定
        self.province_tree_widget.setHeaderLabels(["プロビンスID", "R", "G", "B", "地形", "沿岸", "ステートID", "ステート名", "ローカライズ名"])
        self.province_tree_widget.hide() # 最初は隠しておく

        # 戦略地域リスト (QTreeWidget) - 初期状態では非表示
        self.strategic_region_tree_widget = QTreeWidget()
        self.strategic_region_tree_widget.setObjectName("strategic_region_tree_widget")
        self.strategic_region_tree_widget.setColumnCount(3)
        self.strategic_region_tree_widget.setHeaderLabels(["戦略地域ID", "戦略地域名", "ローカライズ名"])
        self.strategic_region_tree_widget.hide() # 最初は隠しておく

        # QStackedWidget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.tree_widget)
        self.stacked_widget.addWidget(self.province_tree_widget)
        self.stacked_widget.addWidget(self.strategic_region_tree_widget) # StackedWidget に戦略地域ビューを追加

        # メインレイアウト
        main_layout = QVBoxLayout()
        main_layout.addLayout(toolbar_layout)
        main_layout.addLayout(sort_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.stacked_widget) # QStackedWidget を追加

        self.setLayout(main_layout)

    def switch_view(self):
        index = self.view_combo.currentIndex()
        self.stacked_widget.setCurrentIndex(index)
        if index == 1:  # プロビンスビュー
            self.load_province_data()
            self.filtered_province_data = list(self.province_data)
            self.display_province_data()
        elif index == 2: # 戦略地域ビュー
            self.load_strategic_regions()
            self.filtered_strategic_region_files_info = list(self.strategic_region_files_info) # 検索結果リストを初期化
            self.display_strategic_region_data()
        elif index == 0: # ステートビュー
            self.display_state_files()

    def load_state_files(self):
        self.state_files_info = []
        for filename in os.listdir(self.state_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(self.state_dir, filename)
                state_info = self.parse_state_file(filepath)
                if state_info:
                    self.state_files_info.append(state_info)
        self.filtered_state_files_info = list(self.state_files_info) # 検索結果リストも初期化
        self.sort_state_files()

    def parse_state_file(self, filepath):
        filename = os.path.basename(filepath)
        state_id_match = re.match(r"(\d+)-(.+)\.txt", filename)
        if not state_id_match:
            return None
        state_id = int(state_id_match.group(1))
        state_name_from_file = state_id_match.group(2)
        state_name_from_file = state_name_from_file.replace("_", " ").title()

        owner = "N/A"
        manpower = "N/A"
        provinces = [] # プロビンスリストを初期化
        localized_name = "N/A"

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                owner_match = re.search(r"owner\s*=\s*([A-Z]{3})", content)
                if owner_match:
                    owner = owner_match.group(1)
                manpower_match = re.search(r"manpower\s*=\s*(\d+)", content)
                if manpower_match:
                    manpower = manpower_match.group(1)
                name_match = re.search(r"name\s*=\s*\"(.*?)\"", content)
                if name_match:
                    localisation_key = name_match.group(1)
                    if localisation_key in self.localisation_strings:
                        localized_name = self.localisation_strings[localisation_key]
                    else:
                        localized_name = f"<{localisation_key} not found>"
                else:
                    localized_name = state_name_from_file

                # プロビンスIDのリストを抽出
                provinces_match = re.findall(r"add_province\s*=\s*(\d+)", content)
                provinces = [id for id in provinces_match]
                if not provinces:
                    provinces_match = re.findall(r"provinces\s*=\s*{\s*([\d\s]+)\s*}", content)
                    if provinces_match:
                        provinces = provinces_match[0].split()

        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return None

        return {"state_id": state_id, "filename": filename, "state_name": state_name_from_file, "localized_name": localized_name, "owner": owner, "manpower": manpower, "provinces": provinces}

    def load_province_data(self):
        self.province_data = []
        try:
            with open(self.definition_csv_path, 'r', encoding='utf-8') as f:
                # CSVファイルをパース (ヘッダー行はスキップ)
                next(f)  # 1行目をスキップ
                for line in f:
                    items = line.strip().split(';')
                    if len(items) < 6: # データが足りない場合はスキップ
                        continue
                    province_id, r, g, b, terrain_type, is_coastal = items[:6]
                    # 7列目が "true" または "false" の場合のみ処理
                    if is_coastal == "true" or is_coastal == "false":
                      province_info = {
                          "province_id": province_id,
                          "r": r,
                          "g": g,
                          "b": b,
                          "terrain_type": terrain_type,
                          "is_coastal": is_coastal,
                          "state_id": self.get_state_id_for_province(province_id), # ステートIDを取得
                      }
                      self.province_data.append(province_info)
        except Exception as e:
            print(f"Error loading province data from {self.definition_csv_path}: {e}")

    def get_state_id_for_province(self, province_id):
        for state_info in self.state_files_info:
            if province_id in state_info["provinces"]:
                return state_info["state_id"]
        return -1 # 見つからない場合は-1を返す

    def display_province_data(self):
        self.province_tree_widget.clear()
        display_data = self.filtered_province_data if self.filtered_province_data else self.province_data
        for province_info in display_data:
            state_id = province_info["state_id"]
            state_id_str = str(state_id) if state_id != -1 else "N/A"
            state_name = "N/A"
            localized_name = "N/A"
            if state_id != -1:
                # ステートIDからステート名を検索
                for state in self.state_files_info:
                    if state["state_id"] == state_id:
                        state_name = state["localized_name"]
                        localized_name = state["state_name"]
                        break

            item = QTreeWidgetItem([
                province_info["province_id"],
                province_info["r"],
                province_info["g"],
                province_info["b"],
                province_info["terrain_type"],
                province_info["is_coastal"],
                str(state_id),
                state_name,
                localized_name,
            ])
            self.province_tree_widget.addTopLevelItem(item)

    def display_state_files(self):
        self.tree_widget.clear()
        for state_info in self.filtered_state_files_info:
            item = QTreeWidgetItem([str(state_info["state_id"]), state_info["state_name"], state_info["localized_name"], state_info["owner"], state_info["manpower"]])
            self.tree_widget.addTopLevelItem(item)

    def toggle_sort_order(self):
        self.sort_order_ascending = not self.sort_order_ascending
        self.sort_order_button.setText("昇順" if self.sort_order_ascending else "降順")
        current_view_index = self.view_combo.currentIndex()
        if current_view_index == 0: # ステートビュー
            self.sort_state_files()
            self.display_state_files()
        elif current_view_index == 1: # プロビンスビュー
            self.sort_province_data()
            self.display_province_data()
        elif current_view_index == 2: # 戦略地域ビュー
            self.sort_strategic_region_data()
            self.display_strategic_region_data()

    def sort_state_files(self):
        self.sort_key = self.sort_combo.currentText()
        if self.sort_key == "ステートID":
            self.filtered_state_files_info.sort(key=lambda x: x["state_id"], reverse=not self.sort_order_ascending)
        elif self.sort_key == "ステート名":
            self.filtered_state_files_info.sort(key=lambda x: x["state_name"].lower(), reverse=not self.sort_order_ascending)
        elif self.sort_key == "ローカライズ名":
            self.filtered_state_files_info.sort(key=lambda x: x["localized_name"].lower(), reverse=not self.sort_order_ascending)
        elif self.sort_key == "領有国":
            self.filtered_state_files_info.sort(key=lambda x: x["owner"].lower(), reverse=not self.sort_order_ascending)
        elif self.sort_key == "人口":
            self.filtered_state_files_info.sort(key=lambda x: int(x["manpower"]), reverse=not self.sort_order_ascending)

    def sort_province_data(self):
        self.sort_key = self.sort_combo.currentText()
        if self.sort_key == "プロビンスID":
            self.filtered_province_data.sort(key=lambda x: int(x["province_id"]), reverse=not self.sort_order_ascending)
        elif self.sort_key == "地形":
            self.filtered_province_data.sort(key=lambda x: x["terrain_type"].lower(), reverse=not self.sort_order_ascending)
        elif self.sort_key == "ステートID":
            self.filtered_province_data.sort(key=lambda x: int(x["state_id"]) if x["state_id"] != -1 else -1, reverse=not self.sort_order_ascending)
        elif self.sort_key == "R":
            self.filtered_province_data.sort(key=lambda x: int(x["r"]), reverse=not self.sort_order_ascending)
        elif self.sort_key == "G":
            self.filtered_province_data.sort(key=lambda x: int(x["g"]), reverse=not self.sort_order_ascending)
        elif self.sort_key == "B":
            self.filtered_province_data.sort(key=lambda x: int(x["b"]), reverse=not self.sort_order_ascending)
        elif self.sort_key == "沿岸":
            self.filtered_province_data.sort(key=lambda x: x["is_coastal"].lower(), reverse=not self.sort_order_ascending)

    def search_state_files(self):
        search_text = self.search_entry.text().strip()
        search_criteria = self.search_criteria_combo.currentText()
        match_type = self.match_type_combo.currentText()
        current_view_index = self.view_combo.currentIndex()

        if current_view_index == 0: # ステートビューの検索
            self.filtered_state_files_info = [] # 検索結果リストをクリア
            for state_info in self.state_files_info:
                match = False
                if search_criteria == "ステートID":
                    if match_type == "完全一致":
                        if str(state_info["state_id"]) == search_text:
                            match = True
                    elif match_type == "部分一致":
                        if search_text in str(state_info["state_id"]):
                            match = True
                elif search_criteria == "ステート名":
                    if match_type == "完全一致":
                        if state_info["state_name"].lower() == search_text.lower():
                            match = True
                    elif match_type == "部分一致":
                        if search_text.lower() in state_info["state_name"].lower():
                            match = True
                elif search_criteria == "ローカライズ名":
                    if match_type == "完全一致":
                        if state_info["localized_name"].lower() == search_text.lower():
                            match = True
                    elif match_type == "部分一致":
                        if search_text.lower() in state_info["localized_name"].lower():
                            match = True
                elif search_criteria == "領有国":
                    if search_text:
                        if match_type == "完全一致":
                            if state_info["owner"].upper() == search_text.upper():
                                match = True
                        elif match_type == "部分一致":
                            if search_text.upper() in state_info["owner"].upper():
                                match = True
                elif search_criteria == "人口":
                    if search_text:
                        try:
                            if match_type == "完全一致":
                                if str(int(search_text)) == state_info["manpower"]:
                                    match = True
                            elif match_type == "部分一致":
                                if search_text in str(state_info["manpower"]):
                                    match = True
                        except ValueError:
                            pass
                elif search_criteria == "プロビンス":
                    if search_text:
                        if match_type == "完全一致":
                            if search_text in state_info["provinces"]:
                                match = True
                        elif match_type == "部分一致":
                            for province_id in state_info["provinces"]:
                                if search_text in province_id:
                                    match = True
                                    break

                if match:
                    self.filtered_state_files_info.append(state_info)

            self.display_state_files()

        elif current_view_index == 1: # プロビンスビューの検索
            self.filtered_province_data = [] # 検索結果リストをクリア
            for province_info in self.province_data:
                match = False
                if search_criteria == "プロビンスID":
                    if match_type == "完全一致":
                        if str(province_info["province_id"]) == search_text:
                            match = True
                    elif match_type == "部分一致":
                        if search_text in str(province_info["province_id"]):
                            match = True
                elif search_criteria == "地形":
                    if match_type == "完全一致":
                        if province_info["terrain_type"].lower() == search_text.lower():
                            match = True
                    elif match_type == "部分一致":
                        if search_text.lower() in province_info["terrain_type"].lower():
                            match = True
                elif search_criteria == "ステートID":
                    if search_text:
                        if match_type == "完全一致":
                            if str(province_info["state_id"]) == search_text:
                                match = True
                        elif match_type == "部分一致":
                            if search_text in str(province_info["state_id"]):
                                match = True

                if match:
                    self.filtered_province_data.append(province_info)

            self.display_province_data()

        elif current_view_index == 2: # 戦略地域ビューの検索
            self.filtered_strategic_region_files_info = [] # 検索結果リストをクリア
            for region_info in self.strategic_region_files_info:
                match = False
                if search_criteria == "戦略地域ID":
                    if match_type == "完全一致":
                        if str(region_info["strategic_region_id"]) == search_text:
                            match = True
                    elif match_type == "部分一致":
                        if search_text in str(region_info["strategic_region_id"]):
                            match = True
                elif search_criteria == "戦略地域名":
                    if match_type == "完全一致":
                        if region_info["strategic_region_name"].lower() == search_text.lower():
                            match = True
                    elif match_type == "部分一致":
                        if search_text.lower() in region_info["strategic_region_name"].lower():
                            match = True
                if match:
                    self.filtered_strategic_region_files_info.append(region_info)
            self.display_strategic_region_data()

    def show_context_menu(self, point):
        item_tree_widget = self.sender() # sender() でイベントを送信したウィジェットを取得
        item = item_tree_widget.itemAt(point)

        if item:
            self.current_item = item
            menu = QMenu(self)
            if item_tree_widget == self.tree_widget: # ステートツリーの場合
                open_vscode_action = QAction("VSCodeで開く", self)
                open_vscode_action.triggered.connect(self.open_state_file_from_menu)
                menu.addAction(open_vscode_action)
                show_owner_countries_action = QAction("領有国を表示", self)
                show_owner_countries_action.triggered.connect(self.show_owner_country_list_from_menu)
                menu.addAction(show_owner_countries_action)
                show_provinces_action = QAction("プロビンスを表示", self)
                show_provinces_action.triggered.connect(self.show_province_list_from_menu)
                menu.addAction(show_provinces_action)
                transfer_provinces_action = QAction("プロビンス移譲", self)
                transfer_provinces_action.triggered.connect(self.show_transfer_province_dialog)
                menu.addAction(transfer_provinces_action)
            elif self.strategic_region_tree_widget.itemAt(point):  # strategic_region_tree_widget 上で右クリックされた場合
                menu = QMenu(self)
                open_vscode_action = QAction("VSCodeで開く", self)
                open_vscode_action.triggered.connect(self.open_strategic_region_file_from_menu)
                menu.addAction(open_vscode_action)
                show_belonging_states_action = QAction("所属ステートを表示", self)
                show_belonging_states_action.triggered.connect(self.show_belonging_state_list_from_menu)
                menu.addAction(show_belonging_states_action)
                show_provinces_action = QAction("プロビンスを表示", self)
                show_provinces_action.triggered.connect(self.show_province_list_from_menu)
                menu.addAction(show_provinces_action)
                transfer_provinces_action = QAction("プロビンス移譲", self)
                transfer_provinces_action.triggered.connect(self.show_transfer_province_dialog)
                menu.addAction(transfer_provinces_action)
            menu.exec_(self.tree_widget.viewport().mapToGlobal(point))
        else:
            self.current_item = None

    def open_state_file_from_menu(self):
        if self.current_item:
            self.open_state_file_in_vscode(self.current_item)

    def open_state_file_in_vscode(self, item):
        state_id_str = item.text(0)
        state_id = int(state_id_str)
        state_info = next((info for info in self.filtered_state_files_info if info["state_id"] == state_id), None)
        if state_info:
            filepath = os.path.join(self.state_dir, state_info["filename"])
            command = f"code \"{filepath}\""
            result = os.system(command)
            if result != 0:
                print(f"Error opening file in VSCode. Command: {command}, Return code: {result}")
        else:
            print("Invalid item index.")

    def show_province_list_from_menu(self):
        if self.current_item:
            self.show_province_list_popup(self.current_item)

    def show_province_list_popup(self, item):
        state_id_str = item.text(0)
        state_id = int(state_id_str)
        state_info = next((info for info in self.filtered_state_files_info if info["state_id"] == state_id), None)
        if state_info:
            province_list = state_info["provinces"]
            dialog = ProvinceListDialog(province_list, self)
            dialog.exec_()
        else:
            print("Invalid item index.")

    def load_strategic_regions(self):
        self.strategic_region_files_info = []
        if not os.path.exists(self.strategic_regions_dir):
            print(f"エラー：戦略地域ディレクトリが見つかりません: {self.strategic_regions_dir}")
            return  # ディレクトリが存在しない場合はここで処理を中断

        for filename in os.listdir(self.strategic_regions_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(self.strategic_regions_dir, filename)
                region_info = self.parse_strategic_region_file(filepath)
                if region_info:
                    self.strategic_region_files_info.append(region_info)
        self.filtered_strategic_region_files_info = list(self.strategic_region_files_info) # 検索結果リストも初期化

    def parse_strategic_region_file(self, filepath):
        filename = os.path.basename(filepath)
        strategic_region_name_match = re.match(r"(.+)\.txt", filename) # ファイル名から拡張子を除いた部分を取得
        if not strategic_region_name_match:
            return None

        strategic_region_name = strategic_region_name_match.group(1)
        strategic_region_id = -1 # IDはファイル名から取得できないため、-1 で初期化
        provinces = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                strategic_region_id_match = re.search(r"id\s*=\s*(\d+)", content)
                if strategic_region_id_match:
                    strategic_region_id = int(strategic_region_id_match.group(1))
                provinces_match = re.search(r"provinces\s*=\s*{(.*?)}", content, re.DOTALL) # provinces を抽出
                if provinces_match:
                    provinces_text = provinces_match.group(1)
                    provinces = [province.strip() for province in provinces_text.split()] # スペース区切りでプロビンスIDを取得
                localisation_key = strategic_region_name # 戦略地域名はlocalisation keyと同一と仮定
                if localisation_key in self.localisation_strings:
                    localized_name = self.localisation_strings[localisation_key]
                else:
                    localized_name = f"<{localisation_key} not found>"

        except Exception as e:
            print(f"Error parsing strategic region file {filepath}: {e}")
            return None

        return {
            "strategic_region_id": strategic_region_id,
            "strategic_region_name": strategic_region_name, # ファイル名 (拡張子なし) を戦略地域名とする
            "localized_name": localized_name,
            "provinces": provinces, # プロビンスリストを追加
        }

    def display_strategic_region_data(self):
        self.strategic_region_tree_widget.clear()
        display_data = self.filtered_strategic_region_files_info if self.filtered_strategic_region_files_info else self.strategic_region_files_info
        for region_info in display_data:
            item = QTreeWidgetItem([
                str(region_info["strategic_region_id"]),
                region_info["strategic_region_name"],
                region_info["localized_name"]
            ])
            self.strategic_region_tree_widget.addTopLevelItem(item)

    def sort_strategic_region_data(self):
        self.sort_key = self.sort_combo.currentText()
        if self.sort_key == "戦略地域ID":
            self.filtered_strategic_region_files_info.sort(key=lambda x: x["strategic_region_id"], reverse=not self.sort_order_ascending)
        elif self.sort_key == "戦略地域名":
            self.filtered_strategic_region_files_info.sort(key=lambda x: x["strategic_region_name"].lower(), reverse=not self.sort_order_ascending)
        elif self.sort_key == "ローカライズ名":
            self.filtered_strategic_region_files_info.sort(key=lambda x: x["localized_name"].lower(), reverse=not self.sort_order_ascending)

    def show_owner_country_list_from_menu(self):
        if self.current_item:
            self.show_owner_country_list_popup(self.current_item)

    def show_owner_country_list_popup(self, item):
        item_tree_widget = self.sender() # sender() でイベントを送信したウィジェットを取得
        if item_tree_widget == self.tree_widget: # ステートビューの場合 (既存の処理)
            state_id_str = item.text(0)
            state_id = int(state_id_str)
            state_info = next((info for info in self.filtered_state_files_info if info["state_id"] == state_id), None)
            if state_info:
                owner_country_list = [state_info["owner"]] # owner をリストに
                dialog = OwnerCountryDialog(owner_country_list, self)
                dialog.exec_()
            else:
                print("Invalid item index.")
        elif item_tree_widget == self.strategic_region_tree_widget: # 戦略地域ビューの場合 (新規処理)
            strategic_region_id_str = item.text(0)
            strategic_region_id = int(strategic_region_id_str)
            strategic_region_info = next((info for info in self.filtered_strategic_region_files_info if info["strategic_region_id"] == strategic_region_id), None)
            if strategic_region_info:
                owner_country_list = set() # 重複を避けるため set を使用
                if strategic_region_info["provinces"]: # provinces が存在する場合のみ処理
                    for province_id in strategic_region_info["provinces"]:
                        province_id = str(province_id) # province_id は文字列に変換
                        province_info = next((p_info for p_info in self.province_data if p_info["province_id"] == province_id), None)
                        if province_info and province_info["state_id"] != -1:
                            state_id = province_info["state_id"]
                            state_info = next((s_info for s_info in self.state_files_info if s_info["state_id"] == state_id), None)
                            if state_info:
                                owner_country_list.add(state_info["owner"]) # 領有国をsetに追加
                dialog = OwnerCountryDialog(list(owner_country_list), self) # set を list に変換
                dialog.exec_()
            else:
                print("Invalid item index.")

    def open_strategic_region_file_from_menu(self):
        current_item = self.strategic_region_tree_widget.currentItem() # strategic_region_tree_widget の currentItem を取得
        if current_item:
            self.open_strategic_region_file_in_vscode(current_item)

    def open_strategic_region_file_in_vscode(self, item):
        strategic_region_id_str = item.text(0)
        strategic_region_id = int(strategic_region_id_str)
        strategic_region_info = next((info for info in self.filtered_strategic_region_files_info if info["strategic_region_id"] == strategic_region_id), None)
        if strategic_region_info:
            filepath = os.path.join(self.strategic_regions_dir, strategic_region_info["strategic_region_name"] + ".txt")
            command = f"code \"{filepath}\""
            result = os.system(command)
            if result != 0:
                print(f"Error opening file in VSCode. Command: {command}, Return code: {result}")
        else:
            print("Invalid item index.")

    def show_belonging_state_list_from_menu(self):
        if self.current_item:
            self.show_belonging_state_list_popup(self.current_item)

    def show_belonging_state_list_popup(self, item):
        item_tree_widget = self.sender() # sender() でイベントを送信したウィジェットを取得
        if item_tree_widget == self.strategic_region_tree_widget: # 戦略地域ビューの場合
            strategic_region_id_str = item.text(0)
            strategic_region_id = int(strategic_region_id_str)
            strategic_region_info = next((info for info in self.filtered_strategic_region_files_info if info["strategic_region_id"] == strategic_region_id), None)
            if strategic_region_info:
                belonging_state_list = set() # 重複を避けるため set を使用
                if strategic_region_info["provinces"]: # provinces が存在する場合のみ処理
                    for province_id in strategic_region_info["provinces"]:
                        province_id = str(province_id) # province id を文字列に変換
                        province_info = next((p_info for p_info in self.province_data if p_info["province_id"] == province_id), None)
                        if province_info and province_info["state_id"] != -1:
                            state_id = province_info["state_id"]
                            state_info = next((s_info for s_info in self.state_files_info if s_info["state_id"] == state_id), None)
                            if state_info:
                                belonging_state_list.add(state_info["localized_name"]) # ステート名 (localized_name) を set に追加
                dialog = BelongingStateDialog(list(belonging_state_list), self) # set を list に変換
                dialog.exec_()
            else:
                print("Invalid item index.")

    def show_transfer_province_dialog(self):
        if self.current_item:
            state_id_str = self.current_item.text(0)
            state_id = int(state_id_str)
            state_info = next((info for info in self.filtered_state_files_info if info["state_id"] == state_id), None)
            if state_info:
                province_list = state_info["provinces"]
                dialog = ProvinceTransferDialog(province_list, self)
                result = dialog.exec_()
                if result == QDialog.Accepted:
                    selected_provinces = dialog.get_selected_provinces()
                    if selected_provinces:
                        self.show_target_state_dialog(selected_provinces, state_info)
            else:
                print("Invalid item index.")

    def show_target_state_dialog(self, selected_provinces, source_state_info):
        dialog = TargetStateDialog(self, source_state_info)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            target_state_id = dialog.get_target_state_id()
            if target_state_id:
                self.transfer_provinces(selected_provinces, source_state_info["state_id"], target_state_id)

    def transfer_provinces(self, selected_provinces, source_state_id, target_state_id):
        if not selected_provinces or not target_state_id:
            return

        source_state_info = self.find_state_info_by_id(source_state_id)
        target_state_info = self.find_state_info_by_id(target_state_id)

        if not source_state_info or not target_state_info:
            print("Error: Source or target state not found.")
            return

        # 戦略地域の更新処理
        for province_id in selected_provinces:
            source_region_info = self.find_strategic_region_by_province(province_id)
            # 移譲先ステートの最初のプロビンスが属する戦略地域を取得 (存在する場合)
            target_region_info = None
            if target_state_info["provinces"]:
                target_region_info = self.find_strategic_region_by_province(target_state_info["provinces"][0])

            if source_region_info and target_region_info != source_region_info: # 異なる戦略地域に移動する場合のみ更新
                # 移譲元戦略地域からプロビンスを削除
                source_region_info["provinces"] = [p for p in source_region_info["provinces"] if p != str(province_id)] # 文字列比較
                self.update_strategic_region_file(source_region_info)

                # 移譲先戦略地域にプロビンスを追加
                target_region_info["provinces"].append(str(province_id))
                target_region_info["provinces"] = sorted(list(set(target_region_info["provinces"]))) # 重複削除とソート
                self.update_strategic_region_file(target_region_info)

        # プロビンスを移譲元から削除 (ステートファイルの provinces リストを更新)
        updated_source_provinces = [p for p in source_state_info["provinces"] if p not in selected_provinces]
        source_state_info["provinces"] = updated_source_provinces

        # プロビンスを移譲先に追加 (ステートファイルの provinces リストを更新)
        target_state_info["provinces"].extend(selected_provinces)
        target_state_info["provinces"] = sorted(list(set(target_state_info["provinces"]))) # 重複削除とソート

        # ステートファイルを更新
        self.update_state_file(source_state_info)
        self.update_state_file(target_state_info)

        # データと表示を更新
        self.load_state_files() # ファイルを再読み込みして state_files_info を更新
        self.filtered_state_files_info = list(self.state_files_info) # フィルタリングリストも更新
        self.display_state_files() # ステートリストを再表示
        self.load_province_data() # プロビンスデータも再読み込み
        self.filtered_province_data = list(self.province_data)
        self.display_province_data() # プロビンスリストも再表示
        self.load_strategic_regions() # 戦略地域データも再読み込み
        self.filtered_strategic_region_files_info = list(self.strategic_region_files_info)
        self.display_strategic_region_data() # 戦略地域リストも再表示

    def update_state_file(self, state_info):
        filepath = os.path.join(self.state_dir, state_info["filename"])
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content_lines = f.readlines()

            updated_lines = []
            provinces_started = False
            existing_provinces_section_lines = [] # 既存の provinces セクションの行を保持

            for line in content_lines:
                if re.search(r'provinces\s*=\s*\{', line): # 正規表現で provinces = { を検索 (空白を考慮)
                    provinces_started = True
                    updated_lines.append(line) # provinces = { 行はそのまま
                    continue
                if provinces_started:
                    if '}' in line:
                        provinces_started = False
                        if state_info["provinces"]: # プロビンスがある場合のみ provinces = { ... } を書き出す
                            updated_lines.extend([f'\t\t\t{province}\n' for province in sorted(state_info["provinces"])]) # プロビンスIDをソートして追加
                        updated_lines.append('\t\t}\n') # 閉じ括弧を追加
                        existing_provinces_section_lines = [] # provinces セクションの処理が終わったらクリア
                        continue
                    else:
                        existing_provinces_section_lines.append(line) # 既存の provinces セクションの行を保持
                        continue # 既存のプロビンス行はスキップ
                updated_lines.append(line) # provinces セクション以外の行はそのまま

            # provinces = {} がない場合の処理 (ファイルの末尾に追加)
            if not any(re.search(r'provinces\s*=\s*\{', line) for line in content_lines) and state_info["provinces"]: # 正規表現で provinces = { を検索 (空白を考慮)
                updated_lines.append('\tprovinces = {\n')
                updated_lines.extend([f'\t\t\t{province}\n' for province in sorted(state_info["provinces"])])
                updated_lines.append('\t\t}\n')

            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)

        except Exception as e:
            print(f"Error updating state file {filepath}: {e}")

    def find_state_info_by_id(self, state_id):
        return next((info for info in self.state_files_info if info["state_id"] == state_id), None)

    def find_strategic_region_by_province(self, province_id):
        for region_info in self.strategic_region_files_info:
            if str(province_id) in region_info["provinces"]: # province_id は文字列として比較
                return region_info
        return None # 見つからない場合は None を返す

    def update_strategic_region_file(self, region_info):
        filepath = os.path.join(self.strategic_regions_dir, region_info["strategic_region_name"] + ".txt")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content_lines = f.readlines()

            updated_lines = []
            provinces_started = False

            for line in content_lines:
                if re.search(r'provinces\s*=\s*\{', line): # 正規表現で provinces = { を検索 (空白を考慮)
                    provinces_started = True
                    updated_lines.append(line)
                    continue
                if provinces_started:
                    if '}' in line:
                        provinces_started = False
                        if region_info["provinces"]:
                            updated_lines.extend([f'\t\t\t{province}\n' for province in sorted(region_info["provinces"])]) # プロビンスIDをソートして追加
                        updated_lines.append('\t\t}\n')
                        continue
                    else:
                        continue # 既存のプロビンス行はスキップ
                updated_lines.append(line)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)

        except Exception as e:
            print(f"Error updating strategic region file {filepath}: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StateFileLister()
    ex.show()
    sys.exit(app.exec_())