"""処理データ
"""
from constants import Constants as C

class AnalyzedVideoData:
    """処理データクラス
    Attributes:
        fps (float): 動画のフレームレート
        totalframes (int): 動画の総フレーム数
        is_cancel (bool): キャンセルボタンが押されたかどうか
        timestamps_text (list[str]): タイムスタンプ文字列のリスト
        skips (dict[int, int]): スキップ間隔（フレーム）の連想配列

        mstat (int): 試合進行状況ステータス
        mdata (MatchData): 現在の試合のデータ
        progress (AnalyzedVideoProgress): 処理データ進捗状況
    """
    def __init__(self):
        self.fps: float = 0.0
        self.totalframes: int = 0
        self.is_cancel: bool = False
        self.timestamps_text: list[str] = ['Timestamps:\n', '0:00:00 Settings\n']
        self.skips: dict[int, int] = None

        self.mstat = C.STAT.MSTAT_CHARASELECT
        self.mdata = MatchData()
        self.progress = AnalyzedVideoProgress()


    def set_fps(self, fps: float) -> None:
        """fps をセットするとともにスキップ間隔（フレーム）の連想配列を生成
        Args:
            fps (float): 動画のフレームレート
        """
        self.fps = fps

        self.skips = {
            1: int( fps * C.PROC_SPD.INTVL_CHARASELECT ),
            2: int( fps * C.PROC_SPD.INTVL_MATCHFINISHED ),
            3: int( fps * C.PROC_SPD.INTVL_LASTONEFLAG ),
            4: int( fps * C.PROC_SPD.INTVL_MATCHSTARTED ),
            5: int( fps * C.PROC_SPD.INTVL_BLACKOUT ),
            0: int( fps * C.PROC_SPD.INTVL_OTHERS )
        }


    def ts_format(self, frame_no: int) -> str:
        """フレーム番号から h:mm:dd の書式の文字列を返す
        Args:
            frame_no (int): フレーム番号
        Returns:
            str: h:mm:ss の書式の文字列
        """
        time_in_seconds = 0
        if self.fps > 0:
            time_in_seconds = int( frame_no / self.fps )

        h =  time_in_seconds // 3600
        m = (time_in_seconds %  3600) // 60
        s =  time_in_seconds          %  60

        # フォーマットされた文字列を返す
        return f"{h:d}:{m:02d}:{s:02d}"


    def set_progress(self, frame_no: int) -> None:
        """フレーム番号から進捗状況の値をセット
        Args:
            frame_no (int): フレーム番号
        """
        progress = 0.0
        if self.totalframes > 0:
            progress = frame_no / self.totalframes

        ts_text = self.ts_format(frame_no)

        self.progress.value = progress
        self.progress.bar   = int(progress * C.BAR.MAX)
        self.progress.pct   = round( (progress * 100), 1 )
        self.progress.txt   = f'進捗:{self.progress.pct:5.1f}%({ts_text}) '


class MatchData:
    """現在の試合のデータ
    Attributes:
        match_no (int): 試合番号
        fno_eofcharasel (int): キャラ決定時のフレーム番号
        fno_startmatch (int): 試合開始時のフレーム番号
        name_L (str): キャラクター名（左）
        name_R (str): キャラクター名（右）
        max_flags (int): 最大フラッグ数
    """
    def __init__(self):
        """コンストラクタ
        """
        self.match_no: int        = 0
        self.fno_eofcharasel: int = 0
        self.fno_startmatch: int  = 0
        self.name_L: str          = C.CHAR.NOMATCH
        self.name_R: str          = C.CHAR.NOMATCH
        self.max_flags: int       = 0


class AnalyzedVideoProgress:
    """処理データ進捗状況クラス
    Attributes:
        value (float): 進捗（フレーム番号 / 総フレーム数）
        bar (int): プログレスバーの長さ
        pct (float): 進捗率（100.0%）
        txt (str): 進捗文字列（f'進捗:100.0%(h:mm:ss) '）
    """
    def __init__(self):
        self.value: float = 0.0
        self.bar: int     = 0
        self.pct: float   = 0.0
        self.txt: str     = ''
