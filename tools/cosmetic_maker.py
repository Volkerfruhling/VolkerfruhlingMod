import pandas as pd
import os  # osモジュールをインポート

def create_hoi4_loc_file(tsv_filepath, output_filepath):
    """
    tsvファイルからHoi4のローカライズファイル（.yml）を作成する。

    Args:
        tsv_filepath (str): 入力tsvファイルのパス
        output_filepath (str): 出力ymlファイルのパス
    """

    df = pd.read_csv(tsv_filepath, sep='\t')

    with open(output_filepath, 'w', encoding='utf-8-sig') as f:
        f.write('l_japanese:\n') # BOM付きUTF-8で出力

        for index, row in df.iterrows():
            cosmetic_tag = row['cosmetic_tag']
            localization_text = row['ローカライズ']

            if pd.notna(cosmetic_tag) and pd.notna(localization_text): # cosmetic_tagとローカライズが存在する場合のみ出力
                f.write(f' {cosmetic_tag}: "{localization_text}"\n')
                f.write(f' {cosmetic_tag}_DEF: "{localization_text}"\n')

def create_hoi4_startup_script(tsv_filepath, output_filepath):
    """
    tsvファイルからHoi4のstartup_cosmetic_tagスクリプト（.txt）を作成する。

    Args:
        tsv_filepath (str): 入力tsvファイルのパス
        output_filepath (str): 出力txtファイルのパス
    """

    df = pd.read_csv(tsv_filepath, sep='\t')

    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write('startup_cosmetic_tag = {\n') # 変更: startup_cosmetic_tag 形式に変更

        for index, row in df.iterrows():
            tag = row['tag']
            cosmetic_tag = row['cosmetic_tag']

            if pd.notna(tag) and pd.notna(cosmetic_tag): # tagとcosmetic_tagが存在する場合のみ出力
                f.write(f'    {tag} = {{\n') # インデントを調整
                f.write(f'        set_cosmetic_tag = {cosmetic_tag}\n') # インデントを調整
                f.write(f'    }}\n') # インデントを調整

        f.write('}\n') # 変更: startup_cosmetic_tag 形式の閉じ括弧


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__)) # スクリプトのディレクトリを取得
    tsv_file = os.path.join(script_dir, 'input', 'input.tsv') # 入力tsvファイルパスを相対パスで指定
    loc_output_file = os.path.join(script_dir, 'output', 'hoi4_localisation.yml') # ローカライズ出力ymlファイルパスを相対パスで指定
    startup_output_file = os.path.join(script_dir, 'output', 'startup_cosmetic_tag.txt') # startup_cosmetic_tag出力txtファイルパスを相対パスで指定

    create_hoi4_loc_file(tsv_file, loc_output_file)
    print(f"{loc_output_file} を作成しました。")

    create_hoi4_startup_script(tsv_file, startup_output_file)
    print(f"{startup_output_file} を作成しました。") 