"""Hellish Quart 対戦動画タイムスタンプ抽出ツール
"""
import os
import sys
import time
from datetime import datetime
from tkinter import filedialog
import FreeSimpleGUI as sg
from constants import Constants as C
from timestamps_output import TimestampsOutput
from analyze_video import AnalyzeVideo
from analyzed_video_data import AnalyzedVideoData
from analyzed_statistics import AnalyzedStatistics


def main():
    """メイン関数
    """

    # 動画ファイルのパスを取得
    file_path = get_file_path()
    if file_path == '':
        print('ファイルが選択されていません。')
        sys.exit()

    print(f'選択されたファイル: {file_path}')

    # 動画ファイルかを判定
    analyze = AnalyzeVideo()
    try:
        result = analyze.file_open(file_path)
        if result is False:
            print('動画ファイルではありません。')
            sys.exit()
    except Exception:
        analyze.file_close()
        print('例外が発生しました。')
        sys.exit()

    # 処理データクラス初期化
    video_data = AnalyzedVideoData()
    video_data.totalframes = analyze.get_totalframes()
    video_data.set_fps( analyze.get_fps() )

    # 統計情報クラス初期化
    astats = AnalyzedStatistics()
    astats.file_name = os.path.basename(file_path)
    astats.totalframes = video_data.totalframes
    astats.timeofvideo = video_data.ts_format(video_data.totalframes)
    astats.starttime = datetime.now()

    print(f'\n処理開始：{astats.starttime.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'動画のフレームレート：{video_data.fps}')
#    print(f'動画の総フレーム数: {video_data.totalframes}')
    print(f'動画時間：  {astats.timeofvideo}')

    # ウィンドウの生成
    window = create_window()

    # テンポラリ変数初期化
    screen = C.STAT.SCRN_OTHERS
    stat_text = 'その他　　　　　　　'

    skip = video_data.skips[1]

    # 現在のフレーム番号
    frame_no = 0
    # デバッグ用
    #frame_no = (h*60*60 +  m*60 +  s) * 60
    #frame_no = (0*60*60 +  1*60 + 50) * 60   #6600


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
        progress_bar_prev = video_data.progress.bar
        progress_pct_prev = video_data.progress.pct
        video_data.set_progress(frame_no)

        if event not in (C.CANCEL_KEY, sg.WIN_CLOSED):
            if video_data.progress.bar > progress_bar_prev:
                window[C.BAR.KEY].update(video_data.progress.bar)
                window.refresh()

        # コンソール出力
        if video_data.progress.pct > progress_pct_prev:
            sys.stdout.write(f'\r{video_data.progress.txt}{stat_text}')

        # 現在のステータス（どの画面か）を取得
        screen = analyze.get_screen()
        #screen = analyze.get_screen2(screen)

        if screen == C.STAT.SCRN_CHARASELECT:
            # キャラクターセレクト画面
            # キャラクターセレクト画面である間は、「キャラ決定時のフレーム番号」を（現在のフレーム番号）で更新し続ける
            video_data.mdata.fno_eofcharasel = frame_no
            video_data.mstat = C.STAT.MSTAT_CHARASELECT

            skip, stat_text = get_nextstatus( screen, video_data, astats )
            continue


        if screen == C.STAT.SCRN_MATCHINVALID:
            # 対戦画面・試合開始後（両者とも0フラッグ）
            if video_data.mstat in ( C.STAT.MSTAT_CHARASELECT, C.STAT.MSTAT_MATFINISHED ):
                # キャラクター選択画面 → ～ → 対戦画面・試合開始後　に遷移直後（新規試合）　または
                # 試合終了　　　　　　 → ～ → 対戦画面・試合開始後　に遷移直後（リマッチ）

                if   video_data.mstat == C.STAT.MSTAT_CHARASELECT:
                    # キャラクター選択画面 → ～ → 対戦画面・試合開始後　に遷移直後（新規試合）
                    # キャラ決定時のフレーム番号でキャラクタ名（左右）を取得
                    # 画面切り替わり直前はキャラクタ名を判定しづらくなっているため、（キャラ決定時のフレーム番号 - 0.25秒）で判定する。
                    fno_temp = video_data.mdata.fno_eofcharasel - int(video_data.fps * C.PROC_SPD.INTVL_CHARASELECT)
                    video_data.mdata.name_L, video_data.mdata.name_R, maxval_L, maxval_R = analyze.get_charanames(fno_temp)
                    # 最大フラッグ数を取得
                    video_data.mdata.max_flags = analyze.get_maxflags()
                    print(f'\r{video_data.progress.txt}試合開始　　　　　　')
                elif video_data.mstat == C.STAT.MSTAT_MATFINISHED:
                    # 試合終了　　　　　　 → ～ → 対戦画面・試合開始後　に遷移直後（リマッチ）
                    # キャラクタ名・最大フラッグ数は前の試合のものを引き継ぐ
                    print(f'\r{video_data.progress.txt}リマッチ　　　　　　')

                # 3秒前のフレーム番号を「試合開始時のフレーム番号」として保存
                video_data.mdata.fno_startmatch = frame_no - int(video_data.fps * 3)
                # この時点では試合が中止される可能性があるが、コンソールには仮の試合番号で表示する
                ts_text  = video_data.ts_format(video_data.mdata.fno_startmatch)
                match_no = video_data.mdata.match_no + 1
                name_l   = video_data.mdata.name_L
                name_r   = video_data.mdata.name_R
                timestamp = f'{ts_text} M{(match_no):02d}: Player1 - {name_l} vs Player2 - {name_r}'
                print(timestamp)

                video_data.mstat = C.STAT.MSTAT_MATSTARTED
                if analyze.is_lastoneflag(video_data.mdata.max_flags):
                    video_data.mstat = C.STAT.MSTAT_LASTONEFLAG

            skip, stat_text = get_nextstatus( screen, video_data, astats )
            continue


        if screen == C.STAT.SCRN_MATCHVALID:
            # 対戦画面・試合成立後（1フラッグ以上取得）

            if video_data.mstat <  C.STAT.MSTAT_LASTONEFLAG:
                # 直前の状態が残り1フラッグになる前だった場合
                # 残り1フラッグかをチェック
                if analyze.is_lastoneflag(video_data.mdata.max_flags):
                    video_data.mstat = C.STAT.MSTAT_LASTONEFLAG

            if video_data.mstat == C.STAT.MSTAT_LASTONEFLAG:
                # 今の状態が残り1フラッグである場合
                # 試合終了かをチェック
                tmp_finished = analyze.is_matchfinished(video_data.mdata.max_flags)
                if tmp_finished != C.IMG_MATCH.WIN_N:
                    # 試合終了時の処理
                    end_match( analyze, video_data, tmp_finished )
                    video_data.mstat = C.STAT.MSTAT_MATFINISHED

            skip, stat_text = get_nextstatus( screen, video_data, astats )
            continue


        # screen が上記どれにもマッチしない場合
        skip, stat_text = get_nextstatus( screen, video_data, astats )
    # ループ末尾

    # ループ終了後処理
    if video_data.is_cancel:
        print('\nキャンセルされました。')
    else:
        # 終了処理
        ts_text = video_data.ts_format(video_data.totalframes)
        sys.stdout.write('\r                                          \r')

        print(          f'進捗:100.0%({ts_text}) 解析完了')

        output = TimestampsOutput()
        output.write(video_data.timestamps_text)
        print('タイムスタンプをファイルに書き込みました。\n')

        # 処理結果、統計情報の出力
        astats.endtime = datetime.now()
        astats_result  = astats.get_result()
        astats.write_stats(astats_result)
        print(f'{astats_result}')

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


def get_file_path() -> str:
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


def end_match( analyze: AnalyzeVideo, video_data: AnalyzedVideoData, win: int ) -> None:
    """試合終了時の処理

    Args:
        analyze (AnalyzeVideo): get_flags() を呼ぶための引数
        video_data (AnalyzedVideoData): 各種内部変数に値をセットするための引数
        win (int): 左右どちらが勝利したか
    """

    flags_L, flags_R = analyze.get_flags(video_data.mdata.max_flags, win)
    #print(f'Flags: {flags_L}:{flags_R} / {max_flags}')

    if max( flags_L, flags_R ) == video_data.mdata.max_flags:
        # 左右の獲得フラッグ数が最大フラッグ数に達していれば試合決着とする（達していない場合、試合中止とみなす）
        video_data.mdata.match_no += 1
        # フォーマットされた文字列を作成
        ts_text  = video_data.ts_format(video_data.mdata.fno_startmatch)
        match_no = video_data.mdata.match_no
        name_l   = video_data.mdata.name_L
        name_r   = video_data.mdata.name_R
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
        print(f'{video_data.progress.txt}試合終了　　　　　　\n')


def get_nextstatus( screen: str, video_data: AnalyzedVideoData, astats: AnalyzedStatistics ):
    """次ループのスキップ間隔、ステータス文字列を返す

    Args:
        screen (str): 現在の画面
        video_data (AnalyzedVideoData): 各種状態フラグを参照するための引数
        astats (AnalyzedStatistics): 処理統計情報をカウントアップするための引数
    """
    if   screen == C.STAT.SCRN_CHARASELECT:
        stat_text = 'キャラクター選択画面'
        skip = video_data.skips[1]
        astats.cnt_charaselect   += 1
    elif video_data.mstat == C.STAT.MSTAT_MATFINISHED:
        stat_text = '試合終了後　　　　　'
        skip = video_data.skips[2]
        astats.cnt_matchfinished += 1
    elif video_data.mstat == C.STAT.MSTAT_LASTONEFLAG:
        stat_text = '残り１フラッグ　　　'
        skip = video_data.skips[3]
        astats.cnt_lastoneflag   += 1
    elif video_data.mstat == C.STAT.MSTAT_MATSTARTED:
        stat_text = '試合中　　　　　　　'
        skip = video_data.skips[4]
        astats.cnt_matstarted    += 1
    elif screen == C.STAT.SCRN_BLACKOUT:
        stat_text = '暗転画面　　　　　　'
        skip = video_data.skips[5]
        astats.cnt_blackout      += 1
    else:
        stat_text = 'その他　　　　　　　'
        skip = video_data.skips[0]
        astats.cnt_other         += 1

    return skip, stat_text


if __name__ == "__main__":
    main()
