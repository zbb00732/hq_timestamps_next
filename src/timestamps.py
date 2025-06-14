"""Hellish Quart 対戦動画タイムスタンプ抽出ツール
"""
import os
import sys
import time
from tkinter import filedialog
import FreeSimpleGUI as sg
from constants import CONSTANTS as C
from char_names import CharNames
from timestamps_output import TimestampsOutput
import cv2


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
    char_names_l = CharNames(C.CHAR_LEFT_DIR)
    char_names_r = CharNames(C.CHAR_RIGHT_DIR)

    # 動画ファイルのパスを取得
    file_path = get_file_path()
    if file_path == '':
        print('ファイルが選択されていません。')
        sys.exit()

    print(f'選択されたファイル: {file_path}')

    # 動画ファイルかを判定
    try:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            print('動画ファイルを選択してください。')
            sys.exit()
        # 動画のフレーム数を取得
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f'動画ファイルのフレーム数: {frame_count}')
        # フレーム数が1以下のもの（静止画像など）はエラーとする
        if frame_count <= 1:
            cap.release()
            print('動画ファイルを選択してください。')
            sys.exit()
    except Exception:
        cap.release()
        print('例外が発生しました。')
        sys.exit()

    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f'動画ファイルのFPS: {fps}')
    cap.release()


    # ウィンドウの生成
    window = create_window()

    # メインループ
    progress_bar = 0
    timestamps = [] # TODO ダミーの出力データ
    while True:
        # TODO ここからダミータスク>>>
        time.sleep(0.001)

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

        output = TimestampsOutput()
        output.write(timestamps)
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
        filetypes=[('すべてのファイル', '*.*')],
    )

    return file_path


if __name__ == "__main__":
    main()
