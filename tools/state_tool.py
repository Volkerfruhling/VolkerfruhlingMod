import tkinter as tk
from tkinter import ttk
import os
import re

class StateFileLister(tk.Frame):
    def __init__(self, master=None, state_dir="history/states", localisation_dir="localisation/japanese"):
        super().__init__(master)
        self.master = master
        self.state_dir = state_dir
        self.localisation_dir = localisation_dir
        self.localisation_file_name = "state_names_l_japanese.yml"
        self.state_files_info = []
        self.filtered_state_files_info = [] # 検索結果を格納するリスト
        self.sort_key = "state_id"
        self.sort_order_ascending = True

        self.localisation_strings = self.load_localisation()

        self.create_widgets()
        self.load_state_files()
        self.filtered_state_files_info = list(self.state_files_info) # 初期状態ではフィルタリングなし

    def load_localisation(self):
        localisation_strings = {}
        filepath = os.path.join(self.localisation_dir, self.localisation_file_name)
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                # YAML形式を簡易的に解析
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("l_japanese:"):
                        continue
                    if ":" in line and not line.startswith("#"):
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip().strip('"') # 前後の空白とダブルクォートを除去
                        localisation_strings[key] = value
        except Exception as e:
            print(f"Error loading localisation file {filepath}: {e}")
        return localisation_strings


    def create_widgets(self):
        # ソートフレーム (変更なし)
        self.sort_frame = tk.Frame(self)
        self.sort_frame.pack(pady=5)

        sort_label = tk.Label(self.sort_frame, text="ソート:")
        sort_label.pack(side=tk.LEFT)

        self.sort_combo = ttk.Combobox(self.sort_frame, values=["state_id", "state_name", "localized_name", "owner", "manpower"])
        self.sort_combo.pack(side=tk.LEFT)
        self.sort_combo.set(self.sort_key)
        self.sort_combo.bind("<<ComboboxSelected>>", self.change_sort_key)

        self.sort_button = tk.Button(self.sort_frame, text="ソート実行", command=self.sort_state_files)
        self.sort_button.pack(side=tk.LEFT, padx=5)

        self.order_button = tk.Button(self.sort_frame, text="降順", command=self.toggle_sort_order)
        self.order_button.pack(side=tk.LEFT)


        # 検索フレーム
        self.search_frame = tk.Frame(self)
        self.search_frame.pack(fill=tk.X, pady=5)

        # 検索エントリー
        self.search_entry_id = tk.Entry(self.search_frame)
        self.search_entry_id.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        self.search_entry_name = tk.Entry(self.search_frame)
        self.search_entry_name.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        self.search_entry_localized_name = tk.Entry(self.search_frame)
        self.search_entry_localized_name.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        self.search_entry_owner = tk.Entry(self.search_frame)
        self.search_entry_owner.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        self.search_entry_manpower = tk.Entry(self.search_frame)
        self.search_entry_manpower.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        self.search_button = tk.Button(self.search_frame, text="検索", command=self.search_state_files)
        self.search_button.pack(side=tk.LEFT, padx=5)


        # ファイルリスト表示 (変更なし)
        self.tree = ttk.Treeview(self, columns=("state_id", "state_name", "localized_name", "owner", "manpower"), show="headings")
        self.tree.heading("state_id", text="ステートID", command=lambda: self.sort_by_column("state_id"))
        self.tree.heading("state_name", text="ステート名", command=lambda: self.sort_by_column("state_name"))
        self.tree.heading("localized_name", text="ローカライズ名", command=lambda: self.sort_by_column("localized_name"))
        self.tree.heading("owner", text="領有国", command=lambda: self.sort_by_column("owner"))
        self.tree.heading("manpower", text="人口", command=lambda: self.sort_by_column("manpower"))

        self.tree.column("state_id", width=80)
        self.tree.column("state_name", width=150)
        self.tree.column("localized_name", width=200)
        self.tree.column("owner", width=80)
        self.tree.column("manpower", width=80)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # スクロールバー (変更なし)
        self.scrollbar_y = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scrollbar_y.set)

        self.scrollbar_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.configure(xscrollcommand=self.scrollbar_x.set)

        self.tree.bind("<Double-1>", self.open_state_file_in_vscode) # ダブルクリックイベントをバインド

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
        state_id_match = re.match(r"(\d+)-(.+)\.txt", filename) # ファイル名からステートIDとステート名を抽出
        if not state_id_match:
            return None
        state_id = int(state_id_match.group(1))
        state_name_from_file = state_id_match.group(2) # ファイル名からステート名を取得
        state_name_from_file = state_name_from_file.replace("_", " ").title() # "_" を " " に置換してタイトルケースに

        owner = "N/A"
        manpower = "N/A"
        localized_name = "N/A" # デフォルト値
        localisation_key = None # ローカライズキーを初期化

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                owner_match = re.search(r"owner\s*=\s*([A-Z]{3})", content)
                if owner_match:
                    owner = owner_match.group(1)
                manpower_match = re.search(r"manpower\s*=\s*(\d+)", content)
                if manpower_match:
                    manpower = manpower_match.group(1)
                name_match = re.search(r"name\s*=\s*\"(.*?)\"", content) # ローカライズキーを抽出
                if name_match:
                    localisation_key = name_match.group(1)
                    if localisation_key in self.localisation_strings: # ローカライズ名を取得
                        localized_name = self.localisation_strings[localisation_key]
                    else:
                        localized_name = f"<{localisation_key} not found>" # 見つからない場合はキーを表示
                else:
                    localized_name = state_name_from_file # ローカライズキーがない場合はファイル名から生成した名前を使用

        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return None

        return {"state_id": state_id, "filename": filename, "state_name": state_name_from_file, "localized_name": localized_name, "owner": owner, "manpower": manpower}


    def display_state_files(self):
        # Treeviewの内容をクリア
        for item in self.tree.get_children():
            self.tree.delete(item)

        for state_info in self.filtered_state_files_info: # 検索結果リストを使用
            self.tree.insert("", tk.END, values=(state_info["state_id"], state_info["state_name"], state_info["localized_name"], state_info["owner"], state_info["manpower"]))


    def sort_state_files(self):
        reverse_order = not self.sort_order_ascending
        if self.sort_key == "state_id":
            self.filtered_state_files_info.sort(key=lambda x: x["state_id"], reverse=reverse_order) # 検索結果リストをソート
        elif self.sort_key == "state_name": # "state_name" でソート
            self.filtered_state_files_info.sort(key=lambda x: x["state_name"], reverse=reverse_order) # 検索結果リストをソート
        elif self.sort_key == "localized_name": # "localized_name" でソート
            self.filtered_state_files_info.sort(key=lambda x: x["localized_name"], reverse=reverse_order) # 検索結果リストをソート
        elif self.sort_key == "owner":
            self.filtered_state_files_info.sort(key=lambda x: x["owner"], reverse=reverse_order) # 検索結果リストをソート
        elif self.sort_key == "manpower":
            self.filtered_state_files_info.sort(key=lambda x: int(x["manpower"]) if x["manpower"] != "N/A" else -1, reverse=reverse_order) # 検索結果リストをソート

        self.display_state_files()


    def change_sort_key(self, event):
        self.sort_key = self.sort_combo.get()
        self.sort_state_files() # ソートキー変更時にソート実行


    def toggle_sort_order(self):
        self.sort_order_ascending = not self.sort_order_ascending
        if self.sort_order_ascending:
            self.order_button.config(text="降順")
        else:
            self.order_button.config(text="昇順")
        self.sort_state_files() # ソート順変更時にソート実行


    def sort_by_column(self, column):
        if self.sort_key == column:
            self.toggle_sort_order() # 同じ列がクリックされたら昇順/降順を切り替え
        else:
            self.sort_key = column
            self.sort_order_ascending = True # 新しい列でソートする場合は昇順にリセット
            self.order_button.config(text="降順") # ボタン表示を更新
            self.sort_state_files()


    def search_state_files(self):
        search_id = self.search_entry_id.get().strip()
        search_name = self.search_entry_name.get().strip().lower() # 検索文字列を小文字に変換
        search_localized_name = self.search_entry_localized_name.get().strip().lower() # 検索文字列を小文字に変換
        search_owner = self.search_entry_owner.get().strip().upper() # 検索文字列を大文字に変換 (領有国タグは大文字)
        search_manpower = self.search_entry_manpower.get().strip()

        self.filtered_state_files_info = [] # 検索結果リストをクリア
        for state_info in self.state_files_info:
            match = True
            if search_id and str(state_info["state_id"]) != search_id: # IDで検索
                match = False
            if search_name and search_name not in state_info["state_name"].lower(): # ステート名で検索 (小文字で比較)
                match = False
            if search_localized_name and search_localized_name not in state_info["localized_name"].lower(): # ローカライズ名で検索 (小文字で比較)
                match = False
            if search_owner and search_owner != state_info["owner"]: # 領有国で検索
                match = False
            if search_manpower: # 人口で検索
                try:
                    if str(int(search_manpower)) != state_info["manpower"]:
                        match = False
                except ValueError: # 数値に変換できない場合は検索対象外
                    pass

            if match:
                self.filtered_state_files_info.append(state_info)

        self.sort_state_files() # 検索後にソートを適用
        self.display_state_files() # 検索結果を表示


    def open_state_file_in_vscode(self, event):
        selected_item = self.tree.selection() # 選択されているアイテムのIDを取得
        if selected_item:
            item_index = int(selected_item[0][1:], 16) - 1 # TreeviewのIDからインデックスに変換 (I001 -> 0)
            if 0 <= item_index < len(self.filtered_state_files_info):
                filepath = os.path.join(self.state_dir, self.filtered_state_files_info[item_index]["filename"])
                print(f"Opening file: {filepath}") # デバッグ用: ファイルパスをコンソールに出力
                command = f"code \"{filepath}\""
                result = os.system(command) # VSCodeでファイルを開く
                if result != 0:
                    print(f"Error opening file in VSCode. Command: {command}, Return code: {result}") # エラーメッセージを詳細化
            else:
                print("Invalid item index.")
        else:
            print("No item selected.")


def main():
    root = tk.Tk()
    root.title("State File Lister")
    root.geometry("1000x700") # ウィンドウサイズを調整
    root.resizable(True, True)

    state_lister = StateFileLister(root)
    state_lister.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    root.mainloop()

if __name__ == "__main__":
    main() 