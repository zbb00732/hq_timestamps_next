import cv2


class AnalyzeVideo:
    """動画ファイルを解析するクラス
    Attributes:
        capture (cv2.VideoCapture): 動画ファイルのキャプチャオブジェクト
    """

    def __init__(self):
        """コンストラクタ
        """
        self.capture = None
        self.fps = 0.0

    def file_open(self, file):
        """動画ファイルを開く

        Args:
            file (str): 動画ファイルのパス

        Returns:
            bool: 動画ファイルならTrue、そうでなければFalse
        """
        self.capture = cv2.VideoCapture(file)
        if not self.capture.isOpened():
            return False

        # 動画のフレーム数を取得
        self.fps = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))

        # フレーム数が1以下のもの（静止画像など）はエラーとする
        if self.fps <= 1:
            return False

        return True

    def file_close(self):
        """動画ファイルを閉じる
        """
        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def get_fps(self):
        """動画のフレームレートを取得

        Returns:
            float: 動画のフレームレート
        """
        return self.fps
