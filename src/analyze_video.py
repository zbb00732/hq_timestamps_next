import cv2
#from constants import CONSTANTS as C


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
        self.totalframes = 0
        self.frame = None
        self.frame_no = 0

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
        self.totalframes = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))

        # 動画のフレームレートを取得
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)

        # フレーム数が1以下のもの（静止画像など）はエラーとする
        if self.totalframes <= 1:
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

    def get_frame_next(self):
        """動画を次のフレームに進める

        Returns:
            bool: 次のフレームに進められればTrue、そうでなければ（動画終了ならば）False
            int: 次のフレーム番号
        """
        ret, self.frame = self.capture.read()
        #self.frame = cv2.resize(frame, (640, 360))

        self.frame_no += 1
        return ret, self.frame_no

    def get_totalframes(self):
        """動画のフレーム数を取得

        Returns:
            int: 動画のフレーム数
        """
        return self.totalframes

