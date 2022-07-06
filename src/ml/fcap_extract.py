import os
import sys

cur_path: str = os.path.dirname(__file__)[:-3]
sys.path.append(cur_path)

from glob import glob  # nopep8

from local_module import score  # nopep8


def main():
    results = glob(r".\img\train\results\*.jpg")
    for i in range(1, 6):
        for img in results:
            sc = score.SCORE(img)
            file_name = os.path.splitext(os.path.basename(img))[0]
            sc.__get_fcap(file_name, i)


if __name__ == "__main__":
    main()
