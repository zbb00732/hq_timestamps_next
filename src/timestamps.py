"""Hellish Quart 対戦動画タイムスタンプ抽出ツール
"""
import os
import sys
import re
import time
from tkinter import filedialog
import FreeSimpleGUI as sg
from constants import CONSTANTS as C
import utils as u

def main():
    """メイン関数
    """

    data = {
        'names_l': [],
        'imgs_l': [],
        'names_r': [],
        'imgs_r': [],
    }

    # キャラクター名画像を取得
    data['names_l'], data['imgs_l'] = u.get_char_name(C.CHAR_LEFT_DIR)
    data['names_r'], data['imgs_r'] = u.get_char_name(C.CHAR_RIGHT_DIR)

    # 動画ファイルのパスを取得
    file_path = get_file_path()
    if file_path == '':
        print('ファイルが選択されていません。')
        sys.exit()

    print(f'選択されたファイル: `{file_path}`')

    # ウィンドウの生成
    window = create_window()

    # メインループ
    progress_bar = 0
    while True:
        # TODO ここからダミータスク>>>
        time.sleep(0.1)

        # TODO ここではダミータスクとして、プログレスバーを100まで増加させる

        # プログレスバーの増加
        progress_bar += 1
        # TODO <<<ここまでダミータスク

        # キャンセルまたはウィンドウクローズでループ終了
        event, _ = window.read(timeout=100)
        if event in (C.CANCEL_KEY, sg.WIN_CLOSED):
            break

        # プログレスバーの更新
        if event not in (C.CANCEL_KEY, sg.WIN_CLOSED):
            window[C.BAR_KEY].update(progress_bar)
            window.refresh()

        # プログレスバーの真直が100以上ならループ終了
        if 100 <= progress_bar:
            break

    if progress_bar < 100:
        print('キャンセルされました。')
    else:
        # 終了処理
        print('解析完了。')
        print('タイムスタンプをファイルに書き込みました。')

    # コンソールウィンドウを見やすくするための待機
    time.sleep(1)

    # ウィンドウを閉じる
    window.close()


def create_window():
    """ウィンドウの生成

    Returns:
        sg.Window: ウィンドウオブジェクト
    """

    sg.theme(C.WINDOW_THEME)

    # GUIレイアウト
    #   1行目: テキスト
    #   2行目: プログレスバー
    #   3段目: キャンセルボタン
    layout = [
        [sg.Text(C.WINDOW_TEXT)],
        [sg.ProgressBar(
            C.BAR_MAX,
            orientation=C.BAR_ORIENTATION,
            size=(C.BAR_WIDTH, C.BAR_HEIGHT),
            key=C.BAR_KEY,
        )],
        [sg.Button(C.ONCLICK_CANCEL, key=C.CANCEL_KEY)],
    ]

    return sg.Window(C.WINDOW_TITLE, layout, finalize=True)


def get_file_path():
    """ファイルパスを取得する

    Returns:
        str: 選択されたファイルのパス
    """

    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.getcwd()

    file_path = filedialog.askopenfilename(
        initialdir=exe_dir,
        title='動画ファイルを選択',
        filetypes=[('MKVファイル', '*.mkv'), ('すべてのファイル', '*.*')],
    )

    return file_path


if __name__ == "__main__":
    main()
