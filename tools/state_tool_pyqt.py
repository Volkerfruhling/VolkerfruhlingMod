import os
import re
import sys
import configparser
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QTreeWidget, QTreeWidgetItem,
                             QLineEdit, QScrollArea, QFrame, QMenu, QAction,
                             QDialog, QListWidget, QVBoxLayout as QVBoxLayoutDialog, QPushButton as QPushButtonDialog)
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
        close_button.clicked.connect(self.accept) # ダイアログを閉じる
        layout.addWidget(close_button)

        self.setLayout(layout)

class StateFileLister(QWidget):
    def __init__(self, state_dir="history/states", localisation_dir="localisation/japanese", localisation_file_name="state_names_l_japanese.yml"):
        super().__init__()

        # 設定ファイルの読み込み
        self.config = configparser.ConfigParser()
        self.config.read('state_tool_config.ini') # 設定ファイル名を指定

        # 設定値の取得 (デフォルト値も指定)
        self.state_dir = self.config.get('Directories', 'state_dir', fallback='history/states')
        self.localisation_dir = self.config.get('Directories', 'localisation_dir', fallback='localisation/japanese')
        self.localisation_file_name = self.config.get('Directories', 'localisation_file_name', fallback='state_names_l_japanese.yml')
        self.default_sort_key = self.config.get('UI', 'default_sort_key', fallback='state_id')
        self.default_sort_order_ascending = self.config.getboolean('UI', 'default_sort_order_ascending', fallback=True) # boolean型で取得

        self.state_files_info = []
        self.filtered_state_files_info = []
        self.sort_key = self.default_sort_key # デフォルトソートキーを設定から読み込む
        self.sort_order_ascending = self.default_sort_order_ascending # デフォルトソート順を設定から読み込む
        self.localisation_strings = self.load_localisation()
        self.current_item = None

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

        # ソート設定
        sort_layout = QHBoxLayout()
        sort_label = QLabel("ソート:")
        sort_layout.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["state_id", "state_name", "localized_name", "owner", "manpower"])
        self.sort_combo.setCurrentText(self.sort_key)
        sort_layout.addWidget(self.sort_combo)

        sort_button = QPushButton("ソート実行")
        sort_button.clicked.connect(self.sort_state_files)
        sort_layout.addWidget(sort_button)

        self.order_button = QPushButton("降順")
        self.order_button.clicked.connect(self.toggle_sort_order)
        sort_layout.addWidget(self.order_button)

        layout.addLayout(sort_layout)

        # 検索バー
        search_layout = QHBoxLayout()
        self.search_criteria_combo = QComboBox() # 検索対象切り替えコンボボックス
        self.search_criteria_combo.addItems(["ステートID", "ステート名", "ローカライズ名", "領有国", "人口", "プロビンス"]) # 検索対象項目に「プロビンス」を追加
        search_layout.addWidget(self.search_criteria_combo)

        self.search_entry = QLineEdit() # 統合検索窓
        search_layout.addWidget(self.search_entry)

        self.match_type_combo = QComboBox() # 完全一致/部分一致切り替えコンボボックス
        self.match_type_combo.addItems(["部分一致", "完全一致"]) # 検索タイプ項目を追加
        self.match_type_combo.setCurrentText("部分一致") # デフォルトを部分一致に設定
        search_layout.addWidget(self.match_type_combo)

        search_button = QPushButton("検索")
        search_button.clicked.connect(self.search_state_files)

        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # TreeView
        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(5)
        self.tree_widget.setHeaderLabels(["ステートID", "ステート名", "ローカライズ名", "領有国", "人口"])
        self.tree_widget.setColumnWidth(0, 80)
        self.tree_widget.setColumnWidth(1, 150)
        self.tree_widget.setColumnWidth(2, 200)
        self.tree_widget.setColumnWidth(3, 80)
        self.tree_widget.setColumnWidth(4, 80)
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu) # 右クリックメニューを有効にする設定
        self.tree_widget.customContextMenuRequested.connect(self.show_context_menu) # 右クリックシグナルをスロットに接続
        layout.addWidget(self.tree_widget)

        self.setLayout(layout)
        self.setGeometry(300, 300, 1000, 700)
        self.setWindowTitle('State File Lister (PyQt)')

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
        localized_name = "N/A"
        localisation_key = None
        provinces = [] # プロビンスIDリストを追加

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

                provinces_match = re.search(r"provinces\s*=\s*{(.*?)}", content, re.DOTALL) # provinces ブロックを抽出
                if provinces_match:
                    provinces_str = provinces_match.group(1).strip()
                    provinces = [p_id.strip() for p_id in provinces_str.split()] # 空白で区切られたプロビンスIDをリスト化
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return None

        return {"state_id": state_id, "filename": filename, "state_name": state_name_from_file, "localized_name": localized_name, "owner": owner, "manpower": manpower, "provinces": provinces}

    def display_state_files(self):
        self.tree_widget.clear() # TreeWidgetの内容をクリア
        for state_info in self.filtered_state_files_info: # 検索結果リストを使用
            item = QTreeWidgetItem([
                str(state_info["state_id"]),
                state_info["state_name"],
                state_info["localized_name"],
                state_info["owner"],
                state_info["manpower"]
            ])
            self.tree_widget.addTopLevelItem(item)

    def sort_state_files(self):
        self.sort_key = self.sort_combo.currentText()
        self.filtered_state_files_info.sort(key=lambda x: x[self.sort_key], reverse=not self.sort_order_ascending)
        self.display_state_files()

    def toggle_sort_order(self):
        self.sort_order_ascending = not self.sort_order_ascending
        if self.sort_order_ascending:
            self.order_button.setText("降順")
        else:
            self.order_button.setText("昇順")
        self.sort_state_files()

    def search_state_files(self):
        search_text = self.search_entry.text().strip().lower() # 検索テキストを取得
        search_criteria = self.search_criteria_combo.currentText() # 検索対象項目を取得
        match_type = self.match_type_combo.currentText() # 一致タイプを取得 ("部分一致" or "完全一致")

        self.filtered_state_files_info = []
        for state_info in self.state_files_info:
            match = False # 初期値はマッチしない

            if search_criteria == "ステートID":
                if search_text:
                    if match_type == "完全一致":
                        if str(state_info["state_id"]) == search_text:
                            match = True
                    elif match_type == "部分一致":
                        if search_text in str(state_info["state_id"]):
                            match = True
            elif search_criteria == "ステート名":
                if search_text:
                    if match_type == "完全一致":
                        if state_info["state_name"].lower() == search_text:
                            match = True
                    elif match_type == "部分一致":
                        if search_text in state_info["state_name"].lower():
                            match = True
            elif search_criteria == "ローカライズ名":
                if search_text:
                    if match_type == "完全一致":
                        if state_info["localized_name"].lower() == search_text:
                            match = True
                    elif match_type == "部分一致":
                        if search_text in state_info["localized_name"].lower():
                            match = True
            elif search_criteria == "領有国":
                if search_text:
                    if match_type == "完全一致":
                        if state_info["owner"].upper() == search_text.upper(): # 大文字で比較
                            match = True
                    elif match_type == "部分一致":
                        if search_text.upper() in state_info["owner"].upper(): # 大文字で比較
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
                        pass # 数値変換に失敗した場合は無視
            elif search_criteria == "プロビンス": # プロビンス検索の条件を追加
                if search_text:
                    if match_type == "完全一致": # プロビンスIDは通常完全一致で検索する方が自然
                        if search_text in state_info["provinces"]: # リストにプロビンスIDが含まれているか確認
                            match = True
                    elif match_type == "部分一致": # 部分一致も実装 (例: "77" で "778" などもヒットさせる)
                        for province_id in state_info["provinces"]:
                            if search_text in province_id:
                                match = True
                                break # 一つでも部分一致があればマッチ

            if match:
                self.filtered_state_files_info.append(state_info)

        self.display_state_files()

    def show_context_menu(self, point):
        item = self.tree_widget.itemAt(point) # 右クリックされた位置のアイテムを取得
        if item:
            self.current_item = item # 現在のアイテムを保持
            menu = QMenu(self)
            open_vscode_action = QAction("VSCodeで開く", self)
            open_vscode_action.triggered.connect(self.open_state_file_from_menu) # メニューアクションをスロットに接続
            menu.addAction(open_vscode_action)
            show_provinces_action = QAction("プロビンスを表示", self) # 「プロビンスを表示」アクションを追加
            show_provinces_action.triggered.connect(self.show_province_list_from_menu) # アクションをスロットに接続
            menu.addAction(show_provinces_action) # メニューにアクションを追加
            menu.exec_(self.tree_widget.viewport().mapToGlobal(point)) # メニューを右クリック位置に表示
        else:
            self.current_item = None

    def open_state_file_from_menu(self):
        if self.current_item:
            self.open_state_file_in_vscode(self.current_item) # メニューからVSCodeで開く処理を呼び出す

    def open_state_file_in_vscode(self, item): # item を引数として受け取るように修正
        state_id_str = item.text(0) # 最初のカラム (state_id) のテキストを取得
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
            self.show_province_list_popup(self.current_item) # メニューからプロビンスリストポップアップを表示

    def show_province_list_popup(self, item):
        state_id_str = item.text(0) # 最初のカラム (state_id) のテキストを取得
        state_id = int(state_id_str)
        state_info = next((info for info in self.filtered_state_files_info if info["state_id"] == state_id), None)
        if state_info:
            province_list = state_info["provinces"] # state_info から provinces リストを取得
            dialog = ProvinceListDialog(province_list, self) # ProvinceListDialog にプロビンスリストを渡す
            dialog.exec_() # ダイアログを表示
        else:
            print("Invalid item index.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StateFileLister()
    ex.show()
    sys.exit(app.exec_()) 