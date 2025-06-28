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
from analyze_video import AnalyzeVideo
from analyzed_video_data import AnalyzedVideoData


def main():
    """メイン関数
    """

    video_data = AnalyzedVideoData()

    # キャラクター名画像を取得
    video_data.char_names_l = CharNames(C.CHAR_LEFT_DIR)
    video_data.char_names_r = CharNames(C.CHAR_RIGHT_DIR)

    # 動画ファイルのパスを取得
    file_path = get_file_path()
    if file_path == '':
        print('ファイルが選択されていません。')
        sys.exit()

    print(f'選択されたファイル: {file_path}')

    # 動画ファイルかを判定
    analyze = AnalyzeVideo(video_data)
    try:
        result = analyze.file_open(file_path)
        if result is False:
            print('動画ファイルではありません。')
            sys.exit()
    except Exception:
        analyze.file_close()
        print('例外が発生しました。')
        sys.exit()

    video_data.fps = analyze.get_fps()
    print(f'動画のフレームレート: {video_data.fps}')

    video_data.totalframes = analyze.get_totalframes()
    print(f'動画の総フレーム数: {video_data.totalframes}')

    # ウィンドウの生成
    window = create_window()

    # メインループ
    while True:
        # フレームの解析
        ret, frame_no = analyze.get_frame_next()
        if not ret:
            break

        # キャンセルまたはウィンドウクローズでループ終了
        event, _ = window.read(timeout=100)
        if event in (C.CANCEL_KEY, sg.WIN_CLOSED):
            # キャンセルフラグ
            video_data.is_cancel = True
            break

        # プログレスバーの更新
        if event not in (C.CANCEL_KEY, sg.WIN_CLOSED):
            progress_bar = int(frame_no / video_data.totalframes * C.BAR_MAX)
            window[C.BAR_KEY].update(progress_bar)
            window.refresh()

        # 現在のステータス（どの画面か）を取得
        status = analyze.get_status()
        if status == 'charaselect':
            print(f'現在のフレーム: {frame_no} / {video_data.totalframes} :キャラセレクト画面')
        elif status == 'arenaselect':
            print(f'現在のフレーム: {frame_no} / {video_data.totalframes} :マップ選択画面')
        #else:
        #    print(f'現在のフレーム: {frame_no} / {video_data.totalframes}')

    # ループ終了後処理
    if video_data.is_cancel:
        print('キャンセルされました。')
    else:
        # 終了処理
        print('解析完了。')

        output = TimestampsOutput()
        output.write(video_data.timestamps_text)
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
