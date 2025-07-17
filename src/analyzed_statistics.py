"""処理結果統計情報格納クラス
"""
import os
from constants import Constants as C

class AnalyzedStatistics:
    """処理結果統計情報格納クラス
    """
    def __init__(self):
        self.file_name: str   = ''
        self.fps: float       = 0.0
        self.totalframes: int = 0

        self.starttime: datetime.datetime = None
        self.endtime  : datetime.datetime = None

        self.cnt_charaselect: int   = 0
        self.cnt_blackout: int      = 0
        self.cnt_matstarted: int    = 0
        self.cnt_lastoneflag: int   = 0
        self.cnt_matchfinished: int = 0
        self.cnt_other: int         = 0


    def ts_format(self, time_in_seconds: int) -> str:
        """秒数から h:mm:ss の書式の文字列を返す
        Args:
            time_in_seconds (int): 秒数
        Returns:
            str: h:mm:ss の書式の文字列
        """
        h =  time_in_seconds // 3600
        m = (time_in_seconds %  3600) // 60
        s =  time_in_seconds          %  60

        # フォーマットされた文字列を返す
        return f'{h:d}:{m:02d}:{s:02d}'


    def get_timeofvideo(self) -> str:
        """フレーム番号から h:mm:dd の書式の文字列を返す
        Args:
            frame_no (int): フレーム番号
        Returns:
            str: h:mm:ss の書式の文字列
        """
        total_seconds = 0
        if self.fps > 0:
            total_seconds = int( self.totalframes / self.fps )

        # フォーマットされた文字列を返す
        return self.ts_format(total_seconds)


    def get_result(self) -> str:
        total_seconds = 0
        if self.fps > 0:
            total_seconds = int( self.totalframes / self.fps )

        elapsedtime   = self.endtime - self.starttime
        elaps_seconds = int(elapsedtime.total_seconds())

        cnt_total  = 0
        cnt_total += self.cnt_charaselect
        cnt_total += self.cnt_blackout
        cnt_total += self.cnt_matstarted
        cnt_total += self.cnt_lastoneflag
        cnt_total += self.cnt_matchfinished
        cnt_total += self.cnt_other

        stats_text  = f'処理対象ファイル：{self.file_name}\n\n'

        stats_text += f'処理開始：{self.starttime.strftime("%Y-%m-%d %H:%M:%S")}\n'
        stats_text += f'処理終了：{self.endtime.strftime("%Y-%m-%d %H:%M:%S")}\n'
        ########################：YYYY-mm-dd HH:MM:SS
        stats_text += f'所要時間：            {self.ts_format(elaps_seconds)}\n'
        stats_text += f'動画時間：            {self.get_timeofvideo()       } / {self.fps}fps\n\n'

        stats_text +=  '処理結果統計\n'
        stats_text += f'キャラ選択：{self.cnt_charaselect  :7d} ({(self.cnt_charaselect   / cnt_total * 100):5.1f}%)\n'
        stats_text += f'暗転画面　：{self.cnt_blackout     :7d} ({(self.cnt_blackout      / cnt_total * 100):5.1f}%)\n'
        stats_text += f'試合中　　：{self.cnt_matstarted   :7d} ({(self.cnt_matstarted    / cnt_total * 100):5.1f}%)\n'
        stats_text += f'残１フラグ：{self.cnt_lastoneflag  :7d} ({(self.cnt_lastoneflag   / cnt_total * 100):5.1f}%)\n'
        stats_text += f'試合終了後：{self.cnt_matchfinished:7d} ({(self.cnt_matchfinished / cnt_total * 100):5.1f}%)\n'
        stats_text += f'その他　　：{self.cnt_other        :7d} ({(self.cnt_other         / cnt_total * 100):5.1f}%)\n'
        ################　　　　　：1234567 (100.0%)
        stats_text +=  '----------------------------\n'
        stats_text += f'計　　　　：{cnt_total        :7d} (100.0%)\n'
        stats_text += f'処理フレーム/総フレーム：{cnt_total:d}/{self.totalframes:d} ({(cnt_total / self.totalframes * 100):.1f}%)'

        return stats_text


    def write_stats(self, stats_text: str) -> None:
        """解析結果統計情報をファイルに書き込む

        Args:
            stats_text (str): 解析結果統計情報の文字列
        """
        prefix = self.endtime.strftime('%Y%m%d')
        statis_file = prefix + C.STATIS_FILE

        # 出力ファイルが既に存在しているなら削除
        if os.path.exists(statis_file):
            os.remove(statis_file)

        with open(statis_file, 'w', encoding=C.OUTPUT_ENCODING) as file:
            file.write(f'{stats_text}\n')

