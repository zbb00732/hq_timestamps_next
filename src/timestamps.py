"""Hellish Quart 対戦動画タイムスタンプ抽出ツール
"""
import os
import sys
import time
from datetime import datetime
from tkinter import filedialog
import FreeSimpleGUI as sg
from constants import Constants as C
from char_names import CharNames
from match_template import MatchTemplate
from timestamps_output import TimestampsOutput
from analyze_video import AnalyzeVideo
from analyzed_video_data import AnalyzedVideoData


def main():
    """メイン関数
    """

    video_data = AnalyzedVideoData()

    # キャラクター名画像を取得
    video_data.char_names_l = CharNames(C.CHAR.LEFT_DIR)
    video_data.char_names_r = CharNames(C.CHAR.RIGHT_DIR)
    video_data.match_template = MatchTemplate()

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

    #フラグ、テンポラリ変数初期化
    charaselect_flg = False
    matchvalid_flg  = False
    loadscreen_flg  = False
    fno_eofcharasel = 0
    fno_startmatch  = 0
    fno_eofmatch    = 0
    status = 'nomatch'
    skip_interval = 1/4
    skip = int( video_data.fps * skip_interval )

    match_no = 0

    # 現在のフレーム番号
    frame_no = 0
    #frame_no = 1000
    #frame_no = (0*60*60 +  0*60 + 45) * 60   #2700
    #frame_no = (0*60*60 +  1*60 + 50) * 60   #6600
    #frame_no = (0*60*60 +  3*60 + 30) * 60   #12600
    #frame_no = (1*60*60 + 21*60 + 48) * 60
    #frame_no = (1*60*60 + 22*60 + 59) * 60

    starttime = datetime.now()
    ts_text  = '処理開始: ' + starttime.strftime("%Y-%m-%d %H:%M:%S") + '\n'
    ts_text += 'Timestamps:\n'
    ts_text += '0:00:00 Settings'
    video_data.timestamps_text.append(ts_text + '\n')

    # メインループ
    while True:
        frame_no += 1

        if ( frame_no % skip ) != 0:
            continue

        # 指定したフレーム番号に飛ぶ
        ret = analyze.set_frame(frame_no)
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
            progress     = frame_no / video_data.totalframes
            progress_bar = int(progress * C.BAR.MAX)
            window[C.BAR.KEY].update(progress_bar)
            window.refresh()

            # コンソール出力
            ts_text = ts_format(frame_no, video_data.fps)
            sys.stdout.write(f'\r進捗:{progress * 100:6.2f}%({ts_text}) ')

        # 現在のステータス（どの画面か）を取得
        status = analyze.get_status()

        if status == 'charaselect':
            # キャラクターセレクト画面
            #if not charaselect_flg:
            #    #print(f'現在のフレーム: {frame_no} / {video_data.totalframes} :キャラセレクト画面を検知')
            #    print('キャラクターセレクト画面を検知')

            if matchvalid_flg:
                # 対戦画面・試合成立後 → キャラセレクト画面 に遷移直後
                #print(f'試合終了時のフレーム：{fno_eofmatch}')
                # 画面切り替わり直前はフラッグの色を判定しづらくなっているため、（fno_eofmatch - 0.5秒）の画面でフラッグ数をカウントする。
                fno_temp = fno_eofmatch - int(video_data.fps * 0.5)
                flags_L, flags_R, max_flags = analyze.get_flags(fno_temp)
                #print(f'獲得フラッグ数：{flags_L} : {flags_R} / {max_flags}')

                if max( flags_L, flags_R ) == max_flags:
                    # 左右の獲得フラッグ数が最大フラッグ数に達していれば試合決着とする（達していない場合、試合中止とみなす）
                    match_no += 1
                    # フォーマットされた文字列を作成
                    ts_text = ts_format(fno_startmatch, video_data.fps)
                    timestamp = "{} M{:02d}: Player1 - {} vs Player2 - {}".format(ts_text, match_no, name_l, name_r)
                    video_data.timestamps_text.append(timestamp + '\n')
                    #print(timestamp)

                    if   flags_L == flags_R:
                        winner = 'Draw'
                    elif flags_L >  flags_R:
                        winner = 'Player1 win'
                    else:
                        winner = 'Player2 win'

                    winnerstr = winner + ' by ' + str(flags_L) + ':' + str(flags_R)
                    video_data.timestamps_text.append(winnerstr + '\n')
                    print('試合終了')
                    print(winnerstr)

                matchvalid_flg = False

            # キャラクターセレクト画面である間は、「キャラ決定時のフレーム番号」を（現在のフレーム番号）で更新し続ける
            fno_eofcharasel = frame_no
            charaselect_flg = True
            loadscreen_flg  = False

        elif status == 'duringmatch_invalid':
            # 対戦画面・試合成立前
            if charaselect_flg:
                # キャラセレクト画面 → ～ → 対戦画面　に遷移直後
                # 3秒前のフレーム番号を「試合開始時のフレーム番号」として保存
                fno_startmatch = frame_no - int(video_data.fps * 3)

                # キャラ決定時のフレーム番号でキャラクタ名（左右）を取得
                # 画面切り替わり直前はキャラクタ名を判定しづらくなっているため、（キャラ決定時のフレーム番号 - 0.1秒）で判定する。
                fno_temp = fno_eofcharasel - int(video_data.fps * 0.1)
                name_l, name_r, maxval_L, maxval_R = analyze.get_charanames(fno_temp, video_data.char_names_l, video_data.char_names_r)
                #print(f'現在のフレーム: {frame_no} / {video_data.totalframes} :対戦画面・試合成立前 を検知 Left: {name_l}, Right: {name_r}')
                #print(f'L: {name_l.ljust(10)}, {maxval_L}')
                #print(f'R: {name_r.ljust(10)}, {maxval_R}')
                ts_text = ts_format(fno_startmatch, video_data.fps)
                timestamp = "{} M{:02d}: Player1 - {} vs Player2 - {}".format(ts_text, match_no + 1, name_l, name_r)
                print('試合開始')
                print(timestamp)

                charaselect_flg = False
                loadscreen_flg  = False

        elif status == 'duringmatch_valid':
            # 対戦画面・試合成立後
            #if not matchvalid_flg:
                #print(f'現在のフレーム: {frame_no} / {video_data.totalframes} :対戦画面・試合成立後 を検知')

            # 対戦画面である間は、「試合終了時のフレーム番号」を（現在のフレーム番号）で更新し続ける
            fno_eofmatch = frame_no
            matchvalid_flg  = True

        elif status == 'loadscreen':
            loadscreen_flg  = True

        #else:
        #    print(f'現在のフレーム: {frame_no} / {video_data.totalframes}')

        # 状態によって次ループのスキップ間隔（sec）を変える
        if   status == 'charaselect':
            skip_interval = 1/4
        elif loadscreen_flg:
            skip_interval = 1
        else:
            skip_interval = 2

        skip = int( video_data.fps * skip_interval )


    # ループ終了後処理
    if video_data.is_cancel:
        print('キャンセルされました。')
    else:
        # 終了処理
        print('解析完了。')

        endtime = datetime.now()
        ts_text  = '処理終了: ' + endtime.strftime("%Y-%m-%d %H:%M:%S")
        video_data.timestamps_text.append(ts_text + '\n')

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

    sg.theme(C.WINDOW.THEME)

    # GUIレイアウト
    #   1行目: テキスト
    #   2行目: プログレスバー
    #   3段目: キャンセルボタン
    layout = [
        [sg.Text(C.WINDOW.TEXT)],
        [sg.ProgressBar(
            C.BAR.MAX,
            orientation=C.BAR.ORIENTATION,
            size=(C.BAR.WIDTH, C.BAR.HEIGHT),
            key=C.BAR.KEY,
        )],
        [sg.Button(C.ONCLICK_CANCEL, key=C.CANCEL_KEY)],
    ]

    return sg.Window(C.WINDOW.TITLE, layout, finalize=True)


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


def ts_format(frame_no: int, fps: float):
    """フレーム番号から h:mm:dd の書式の文字列を返す
    Args:
        frame_no (int): フレーム番号
        fps (float): 動画のフレームレート
    Returns:
        str: h:mm:dd の書式の文字列
    """

    time_in_seconds = int( frame_no / fps )
    hours   =  time_in_seconds // 3600
    minutes = (time_in_seconds %  3600) // 60
    seconds =  time_in_seconds          %  60
    # フォーマットされた文字列を作成
    ts_text = "{:01d}:{:02d}:{:02d}".format(hours, minutes, seconds)

    return ts_text


if __name__ == "__main__":
    main()
