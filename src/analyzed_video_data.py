"""処理データ
"""
class AnalyzedVideoData:
    """処理データクラス
    """
    def __init__(self):
        self.fps: int = 0
        self.totalframes: int = 0
        self.char_names_l = None
        self.char_names_r = None
        self.match_template = None
        self.timestamps_text: list[str] = []
        self.statistics_text: list[str] = []
        self.is_cancel: bool = False
