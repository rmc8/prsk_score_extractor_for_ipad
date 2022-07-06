import os

import PySimpleGUI as sg


def add_path(path: str):
    if path not in os.environ["PATH"].split(os.pathsep):
        os.environ["PATH"] += path


def select_file(title: str, file_types: tuple, is_save: bool = False):
    """
    ファイルダイアログを呼び出す
    :param title: Windowのタイトル
    :param is_save: 書き込み用で使うか
    :return: ファイルパス
    """
    sg.theme("Black")
    while True:
        file_path = sg.popup_get_file(title, file_types=file_types, save_as=is_save)
        if file_path is None:
            exit()
        elif is_save or os.path.exists(file_path):
            break
        sg.popup(f"以下のファイルは存在しません。\nfile: {file_path}")
    return file_path
