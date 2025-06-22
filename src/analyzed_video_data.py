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
        self.timestamps_text: list[str] = []
        self.is_cancel: bool = False
