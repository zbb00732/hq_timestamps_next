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

    # ここから 内部関数定義
    def end_match():
        """試合成立後 → 別ステータスに遷移直後の処理

        """
        nonlocal analyze
        nonlocal video_data
        nonlocal match_no

        flags_L, flags_R = analyze.get_flags(fno_eofmatch, max_flags)
        #print(f'Flags: {flags_L}:{flags_R} / {max_flags}')

        if max( flags_L, flags_R ) <= max_flags:
            # 左右の獲得フラッグ数が最大フラッグ数に達していれば試合決着とする（達していない場合、試合中止とみなす）
            match_no += 1
            # フォーマットされた文字列を作成
            ts_text = ts_format(fno_startmatch, video_data.fps)
            timestamp = f'{ts_text} M{match_no:02d}: Player1 - {name_l} vs Player2 - {name_r}'
            video_data.timestamps_text.append(timestamp + '\n')

            if   flags_L == flags_R:
                winner = 'Draw'
            elif flags_L >  flags_R:
                winner = 'Player1 win'
            else:
                winner = 'Player2 win'

            winnerstr = "{} by {}:{}".format(winner, flags_L, flags_R)
            video_data.timestamps_text.append(winnerstr + '\n')
            #################'\r進捗:100.00%(0:00:00) キャラクター選択画面\r')
            sys.stdout.write('\r                                          \r')
            print(winnerstr)
            print(f'{progress_txt}試合終了　　　　　　\n')

    # ここまで 内部関数定義

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
    lastoneflag_flg = False
    fno_eofcharasel = 0
    fno_startmatch  = 0
    fno_eofmatch    = 0
    status = 'nomatch'
    stat_text = 'その他'
    skip_interval = 1/4
    skip = int( video_data.fps * skip_interval )
    progress_bar = -1
    progress_pct = "  0.0"

    match_no = 0

    # デバッグ用
    cnt_charaselect = 0
    cnt_lastoneflag = 0
    cnt_blackout    = 0
    cnt_matvalid    = 0
    cnt_matinvalid  = 0
    cnt_other       = 0


    # 現在のフレーム番号
    frame_no = 0
    #frame_no = 1000
    #frame_no = (0*60*60 +  0*60 + 45) * 60   #2700
    #frame_no = (0*60*60 +  1*60 + 50) * 60   #6600
    #frame_no = (0*60*60 +  3*60 + 30) * 60   #12600
    #frame_no = (0*60*60 + 44*60 + 54) * 60
    #frame_no = (1*60*60 +  1*60 + 15) * 60
    #frame_no = (1*60*60 + 21*60 + 48) * 60
    #frame_no = (1*60*60 + 22*60 + 59) * 60

    starttime = datetime.now()
    ts_text  = 'Timestamps:\n'
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
            progress_bar_prev = progress_bar
            progress_bar = int(progress * C.BAR.MAX)
            if progress_bar > progress_bar_prev:
                window[C.BAR.KEY].update(progress_bar)
                window.refresh()

            # コンソール出力
            ts_text = ts_format(frame_no, video_data.fps)
            progress_pct_prev = progress_pct
            progress_pct = f'{progress * 100:5.1f}'
            progress_txt = f'\r進捗:{progress_pct}%({ts_text}) '
            if progress_pct > progress_pct_prev:
                sys.stdout.write(progress_txt + stat_text)

        # 現在のステータス（どの画面か）を取得
        #status = analyze.get_status2(status)
        status = analyze.get_status()

        if status == 'charaselect':
            # キャラクターセレクト画面
            if matchvalid_flg:
                # 対戦画面・試合成立後 → キャラセレクト画面 に遷移直後
                end_match()
                matchvalid_flg = False

            # キャラクターセレクト画面である間は、「キャラ決定時のフレーム番号」を（現在のフレーム番号）で更新し続ける
            fno_eofcharasel = frame_no
            charaselect_flg = True
            lastoneflag_flg = False

        elif status == 'duringmatch_invalid':
            # 対戦画面・試合成立前
            if charaselect_flg or matchvalid_flg:
                # キャラセレクト画面　 → ～ → 対戦画面　に遷移直後　または
                # 対戦画面・試合成立後 →　　→ 対戦画面・試合成立前　に遷移直後（リマッチ）

                if matchvalid_flg:
                    # 対戦画面・試合成立後 →　　→ 対戦画面　に遷移直後
                    end_match()
                    print(f'{progress_txt}リマッチ　　　　　　')
                elif charaselect_flg:
                    # キャラセレクト画面　 → ～ → 対戦画面　に遷移直後
                    # キャラ決定時のフレーム番号でキャラクタ名（左右）を取得
                    # 画面切り替わり直前はキャラクタ名を判定しづらくなっているため、（キャラ決定時のフレーム番号 - 0.1秒）で判定する。
                    fno_temp = fno_eofcharasel - int(video_data.fps * 0.1)
                    name_l, name_r, maxval_L, maxval_R = analyze.get_charanames(fno_temp, video_data.char_names_l, video_data.char_names_r)
                    max_flags = analyze.get_maxflags()
                    print(f'{progress_txt}試合開始　　　　　　')

                # 3秒前のフレーム番号を「試合開始時のフレーム番号」として保存
                fno_startmatch = frame_no - int(video_data.fps * 3)
                ts_text = ts_format(fno_startmatch, video_data.fps)
                timestamp = f"{ts_text} M{(match_no + 1):02d}: Player1 - {name_l} vs Player2 - {name_r}"
                print(timestamp)

                matchvalid_flg  = False
                charaselect_flg = False
                lastoneflag_flg = analyze.is_lastoneflag(max_flags)

        elif status == 'duringmatch_valid':
            # 対戦画面・試合成立後
            # 対戦画面である間は、「試合終了時のフレーム番号」を（現在のフレーム番号）で更新し続ける
            fno_eofmatch = frame_no
            matchvalid_flg  = True

            if not lastoneflag_flg:
                lastoneflag_flg = analyze.is_lastoneflag(max_flags)

        # 状態によって次ループのスキップ間隔（sec）を変える
        if   status == 'charaselect':
            stat_text = 'キャラクター選択画面'
            skip_interval = 0.25
            cnt_charaselect += 1
        elif lastoneflag_flg:
            stat_text = '残り１フラッグ　　　'
            skip_interval = 0.5
            cnt_lastoneflag += 1
        elif status == 'blackout':
            stat_text = '暗転画面　　　　　　'
            skip_interval = 1
            cnt_blackout    += 1
        elif status == 'duringmatch_valid':
            stat_text = '試合中　　　　　　　'
            skip_interval = 3
            cnt_matvalid    += 1
        elif status == 'duringmatch_invalid':
            stat_text = '試合中　　　　　　　'
            skip_interval = 3
            cnt_matinvalid  += 1
        else:
            stat_text = 'その他　　　　　　　'
            skip_interval = 2
            cnt_other       += 1

        skip = int( video_data.fps * skip_interval )


    # ループ終了後処理
    if video_data.is_cancel:
        print('\nキャンセルされました。')
    else:
        # 終了処理
        ts_text = ts_format(video_data.totalframes, video_data.fps)
        sys.stdout.write('\r                                          \r')

        print(          f'進捗:100.0%({ts_text}) 解析完了')

        output = TimestampsOutput()
        output.write(video_data.timestamps_text)
        print('タイムスタンプをファイルに書き込みました。\n')

        # 処理結果、統計情報の出力
        endtime       = datetime.now()
        elapsedtime   = endtime - starttime
        total_seconds = int(elapsedtime.total_seconds())
        el_h =  total_seconds // 3600
        el_m = (total_seconds %  3600) // 60
        el_s =  total_seconds          %  60

        cnt_total = cnt_charaselect + cnt_blackout + cnt_matinvalid + cnt_matvalid + cnt_lastoneflag + cnt_other

        stats_text  = f'処理開始：{starttime.strftime("%Y-%m-%d %H:%M:%S")}\n'
        stats_text += f'処理終了：{endtime.strftime("%Y-%m-%d %H:%M:%S")}\n'
        ########################：YYYY-mm-dd HH:MM:SS
        stats_text += f'所要時間：            {el_h:d}:{el_m:02d}:{el_s:02d}\n'
        stats_text += f'動画時間：            {ts_text}\n\n'

        stats_text +=  '処理結果統計\n'
        stats_text += f'キャラ選択：{cnt_charaselect:7d} ({(cnt_charaselect / cnt_total * 100):5.1f}%)\n'
        stats_text += f'暗転画面　：{cnt_blackout   :7d} ({(cnt_blackout    / cnt_total * 100):5.1f}%)\n'
        stats_text += f'試合成立前：{cnt_matinvalid :7d} ({(cnt_matinvalid  / cnt_total * 100):5.1f}%)\n'
        stats_text += f'試合成立後：{cnt_matvalid   :7d} ({(cnt_matvalid    / cnt_total * 100):5.1f}%)\n'
        stats_text += f'残１フラグ：{cnt_lastoneflag:7d} ({(cnt_lastoneflag / cnt_total * 100):5.1f}%)\n'
        stats_text += f'その他　　：{cnt_other      :7d} ({(cnt_other       / cnt_total * 100):5.1f}%)\n'
        stats_text +=  '----------------------------\n'
        stats_text += f'計　　　　：{cnt_total      :7d} (100.0%)\n'
        stats_text += f'処理フレーム/総フレーム：{cnt_total:d}/{video_data.totalframes:d} ({(cnt_total / video_data.totalframes * 100):.1f}%)'
        video_data.statistics_text.append(stats_text)
        output.write_stat(video_data.statistics_text)
        print(f'{stats_text}')

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
    h =  time_in_seconds // 3600
    m = (time_in_seconds %  3600) // 60
    s =  time_in_seconds          %  60

    # フォーマットされた文字列を返す
    return f"{h:d}:{m:02d}:{s:02d}"


if __name__ == "__main__":
    main()
