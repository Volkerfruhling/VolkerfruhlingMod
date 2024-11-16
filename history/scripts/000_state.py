import pathlib
import pandas as pd
input_dir = 'history/states'
# フォルダ内に保存されているファイル一覧
state_list = list(pathlib.Path(input_dir).glob('**/*.txt'))
for i in range (len(state_list)):

    with open(state_list[i],"r",encoding="utf-8") as f:
        df = pd.Series(f.readlines())
        print(df)
        df.drop(df[df.str.contains('owner')].index,inplace=True)
        df.drop(df[df.str.contains('add_core_of')].index,inplace=True)
        df.drop(df[df.str.contains('add_claim_by')].index,inplace=True)
        df.drop(df[df.str.contains('add_to_array')].index,inplace=True)
        df.drop(df[df.str.contains('add_dynamic_modifier')].index,inplace=True)
        df.drop(df[df.str.contains('set_demilitarized_zone')].index,inplace=True)
        lines = df.to_list()

    with open(state_list[i],"w",encoding="utf-8") as f:
        
        f.write("")
        for j in range(len(lines)):
            f.write(str(lines[j]))
