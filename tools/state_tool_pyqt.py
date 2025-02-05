import os
import re
import sys
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
        self.state_dir = state_dir
        self.localisation_dir = localisation_dir
        self.localisation_file_name = localisation_file_name
        self.state_files_info = []
        self.filtered_state_files_info = [] # 検索結果を格納するリスト
        self.sort_key = "state_id"
        self.sort_order_ascending = True
        self.localisation_strings = self.load_localisation()
        self.current_item = None # 右クリックされたアイテムを保持

        self.init_ui()
        self.load_state_files()
        self.filtered_state_files_info = list(self.state_files_info) # 初期状態ではフィルタリングなし
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
        self.search_entry_id = QLineEdit()
        self.search_entry_name = QLineEdit()
        self.search_entry_localized_name = QLineEdit()
        self.search_entry_owner = QLineEdit()
        self.search_entry_manpower = QLineEdit()
        search_button = QPushButton("検索")
        search_button.clicked.connect(self.search_state_files)

        search_layout.addWidget(self.search_entry_id)
        search_layout.addWidget(self.search_entry_name)
        search_layout.addWidget(self.search_entry_localized_name)
        search_layout.addWidget(self.search_entry_owner)
        search_layout.addWidget(self.search_entry_manpower)
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

        return {"state_id": state_id, "filename": filename, "state_name": state_name_from_file, "localized_name": localized_name, "owner": owner, "manpower": manpower, "provinces": provinces} # provinces を state_info に追加

    def display_state_files(self):
        self.tree_widget.clear() # TreeWidgetの内容をクリア
        for state_info in self.filtered_state_files_info: # 検索結果リストを使用
            item = QTreeWidgetItem([
                str(state_info["state_id"]),
                state_info["state_name"],
                state_info["localized_name"],
                state_info["owner"],
                str(state_info["manpower"])
            ])
            self.tree_widget.addTopLevelItem(item)

    def sort_state_files(self):
        reverse_order = not self.sort_order_ascending
        if self.sort_key == "state_id":
            self.filtered_state_files_info.sort(key=lambda x: x["state_id"], reverse=reverse_order)
        elif self.sort_key == "state_name":
            self.filtered_state_files_info.sort(key=lambda x: x["state_name"], reverse=reverse_order)
        elif self.sort_key == "localized_name":
            self.filtered_state_files_info.sort(key=lambda x: x["localized_name"], reverse=reverse_order)
        elif self.sort_key == "owner":
            self.filtered_state_files_info.sort(key=lambda x: x["owner"], reverse=reverse_order)
        elif self.sort_key == "manpower":
            self.filtered_state_files_info.sort(key=lambda x: int(x["manpower"]) if x["manpower"] != "N/A" else -1, reverse=reverse_order)

        self.display_state_files()

    def change_sort_key(self, key):
        self.sort_key = key
        self.sort_state_files()

    def toggle_sort_order(self):
        self.sort_order_ascending = not self.sort_order_ascending
        if self.sort_order_ascending:
            self.order_button.setText("降順")
        else:
            self.order_button.setText("昇順")
        self.sort_state_files()

    def sort_by_column(self, column, order): # PyQtのTreeWidgetはヘッダークリックソートを標準でサポート
        key = ["state_id", "state_name", "localized_name", "owner", "manpower"][column]
        if self.sort_key == key:
            self.toggle_sort_order()
        else:
            self.sort_key = key
            self.sort_order_ascending = True
            self.order_button.setText("降順")
        self.sort_state_files()

    def search_state_files(self):
        search_id = self.search_entry_id.text().strip()
        search_name = self.search_entry_name.text().strip().lower()
        search_localized_name = self.search_entry_localized_name.text().strip().lower()
        search_owner = self.search_entry_owner.text().strip().upper()
        search_manpower = self.search_entry_manpower.text().strip()

        self.filtered_state_files_info = []
        for state_info in self.state_files_info:
            match = True
            if search_id and str(state_info["state_id"]) != search_id:
                match = False
            if search_name and search_name not in state_info["state_name"].lower():
                match = False
            if search_localized_name and search_localized_name not in state_info["localized_name"].lower():
                match = False
            if search_owner and search_owner != state_info["owner"]:
                match = False
            if search_manpower:
                try:
                    if str(int(search_manpower)) != state_info["manpower"]:
                        match = False
                except ValueError:
                    pass

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