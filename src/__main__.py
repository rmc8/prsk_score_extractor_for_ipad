import os
import shutil
import datetime
from glob import glob

import pandas as pd

from local_module import score


def main():
    cur_path : str = os.path.dirname(__file__)[:-4]
    imgs : list = glob(f"{cur_path}\\img\\input\\*.???")
    table : list = []
    for n, img_path in enumerate(imgs, 1):
        sc = score.SCORE(img_path)
        record: dict = {"index": n, "file_name": os.path.basename(img_path)} | sc.get_title()
        for location_num in range(1, 6):
            record: dict = record | sc.get_score(location_num)
        print(record)
        table.append(record)
    if not table:
        exit()
    df = pd.DataFrame(table)
    print(df)
    now = datetime.datetime.now()
    os.makedirs(f"./img/input/archive/{now:%Y%m%d_%H%M%S}", exist_ok=True)
    os.makedirs("./output/", exist_ok=True)
    df.to_csv("./output/results_{now:%Y%m%d_%H%M%s}.tsv", sep="\t", index=False)


if __name__ == "__main__":
    main()
