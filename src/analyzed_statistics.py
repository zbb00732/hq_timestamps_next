"""処理結果統計情報格納クラス
"""
import os
from constants import Constants as C

class AnalyzedStatistics:
    """処理結果統計情報格納クラス
    """
    def __init__(self):
        self.file_name   = ''
        self.totalframes = 0
        self.timeofvideo = ''

        self.starttime: datetime.datetime = None
        self.endtime  : datetime.datetime = None

        self.cnt_charaselect   = 0
        self.cnt_blackout      = 0
        self.cnt_matstarted    = 0
        self.cnt_lastoneflag   = 0
        self.cnt_matchfinished = 0
        self.cnt_other         = 0


    def get_result(self) -> str:
        elapsedtime   = self.endtime - self.starttime
        total_seconds = int(elapsedtime.total_seconds())
        h =  total_seconds // 3600
        m = (total_seconds %  3600) // 60
        s =  total_seconds          %  60

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
        stats_text += f'所要時間：            {h:d}:{m:02d}:{s:02d}\n'
        stats_text += f'動画時間：            {self.timeofvideo}\n\n'

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

