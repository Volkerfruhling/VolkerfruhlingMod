import pathlib
import pandas as pd
input_dir = 'history/countries'
base_file_path = "history/scripts/countries.txt"
# フォルダ内に保存されているファイル一覧
country_list = list(pathlib.Path(input_dir).glob('**/*.txt'))
with open(base_file_path,"r",encoding="utf-8") as b:
    base = b.read()
print(base)
for i in range (len(country_list)):

    with open(country_list[i],"r",encoding="utf-8") as f:
        file = f.readlines()
        file = [file[0]]
        file.append(base)
        print(file)


    with open(country_list[i],"w",encoding="utf-8") as f:
        
        f.write("")
        for j in range(len(file)):
            f.write(str(file[j]))