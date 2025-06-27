import cv2
#from constants import CONSTANTS as C


class AnalyzeVideo:
    """動画ファイルを解析するクラス
    Attributes:
        capture (cv2.VideoCapture): 動画ファイルのキャプチャオブジェクト
        fps (float): 動画のフレームレート
        totalframes (int): 動画の総フレーム数
        frame (ndarray): 現在のフレーム情報
        frame_no (int): 現在のフレーム番号
    """

    def __init__(self):
        """コンストラクタ
        """
        self.capture = None
        self.fps = 0.0
        self.totalframes = 0
        self.frame = None
        self.frame_no = 0

        # 検出する画像の読み込み
        self.img_blackout    = cv2.imread('matchtemplate/black.png', 1)
        self.img_loadscreen  = cv2.imread('matchtemplate/load.png', 0)
        self.img_charaselect = cv2.imread('matchtemplate/charaselect.png', 0)
        self.img_arenaselect = cv2.imread('matchtemplate/arenaselect.png', 0)


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
        ret, frame_orig = self.capture.read()
        frame_resized = cv2.resize(frame_orig, (640, 360))
        frame_gray    = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        self.frame = frame_gray

        self.frame_no += 1
        return ret, self.frame_no


    def get_totalframes(self):
        """動画のフレーム数を取得

        Returns:
            int: 動画のフレーム数
        """
        return self.totalframes


    def is_matchimage(self, image):
        """現在のフレームが、引数で指定した画像とマッチするかを判定

        Args:
            image (ndarray): 画像（cv2.imread()で読み込んだオブジェクト）

        Returns:
            bool: キャラクタセレクト画面ならばTrue
        """
        result1 = cv2.matchTemplate(self.frame, image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result1)
        # 信頼度最大値（max_val）が 0.7 より大きければマッチしたとみなす
        if max_val > 0.7:
            return True

        return False


    def get_status(self):
        """現在のフレームのステータス（どの画面か）を取得

        Returns:
            str: ステータス文字列
        """

        if self.is_matchimage(self.img_charaselect):
            return 'charaselect'
        elif self.is_matchimage(self.img_arenaselect):
            return 'arenaselect'

        return 'nomatch'
