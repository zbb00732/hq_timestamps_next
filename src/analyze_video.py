import cv2
#from constants import Constants as C
from analyzed_video_data import AnalyzedVideoData


class AnalyzeVideo:
    """動画ファイルを解析するクラス
    Attributes:
        capture (cv2.VideoCapture): 動画ファイルのキャプチャオブジェクト
        fps (float): 動画のフレームレート
        totalframes (int): 動画の総フレーム数
        frame (ndarray): 現在のフレーム情報
        frame_no (int): 現在のフレーム番号
    """

    def __init__(self, video_data: AnalyzedVideoData):
        """コンストラクタ
        """
        self.capture = None
        self.fps = 0.0
        self.totalframes = 0
        self.frame = None
        self.frame_no = 0

        # 検出する画像の読み込み
        self.img_blackout    = cv2.imread('matchtemplate/black.png', cv2.IMREAD_COLOR)
        self.img_loadscreen  = cv2.imread('matchtemplate/load.png', cv2.IMREAD_GRAYSCALE)
        self.img_charaselect = cv2.imread('matchtemplate/charaselect.png', cv2.IMREAD_GRAYSCALE)
        self.img_arenaselect = cv2.imread('matchtemplate/arenaselect.png', cv2.IMREAD_GRAYSCALE)


    def file_open(self, file: str):
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


    def set_frame(self, frame_no: int):
        """動画内の指定したフレーム番号に飛ぶ

        Args:
            frame_no (int): フレーム番号

        Returns:
            bool: 指定したフレームに飛べればTrue、そうでなければFalse
        """
        # 指定したフレーム位置に移動
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, frame_no)

        # フレームを1枚読み込み
        ret, frame_orig = self.capture.read()
        if ret:
            frame_resized = cv2.resize(frame_orig, (640, 360))
#            frame_gray    = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
            self.frame = frame_resized
            self.frame_no = frame_no

        return ret


    def get_totalframes(self):
        """動画のフレーム数を取得

        Returns:
            int: 動画のフレーム数
        """
        return self.totalframes


    def is_matchimage(self, image, area=(0, 0, 640, 360), color=cv2.IMREAD_GRAYSCALE, threshold=0.7):
        """現在のフレーム内で、指定した範囲が、指定した画像とマッチするかを判定

        Args:
            image (ndarray): 画像（cv2.imread()で読み込んだオブジェクト）
            area (tuple): 範囲（ (x, y, w, h) 左上の座標,幅,高さ）。フレーム全体の大きさは(640×360)とする
                          cv2.matchTemplate の性質上、image よりも少し大きめに指定するとよい
            color (int): 0(cv2.IMREAD_GRAYSCALE):グレースケール、1(cv2.IMREAD_COLOR):カラー
            threshold (float): 閾値

        Returns:
            bool: マッチしていればTrue
        """
        x, y, w, h = area
        frame = self.frame[y:y+h, x:x+w]

        if color == cv2.IMREAD_GRAYSCALE:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        result1 = cv2.matchTemplate(frame, image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result1)
        # 信頼度最大値（max_val）が threshold より大きければマッチしたとみなす
        if max_val > threshold:
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


    def get_charaname(self, left, charnames):
        """現在のフレーム内で表示されているキャラクター名を取得

        Args:
            left (bool): 左（True）、右（False）
            charnames (CharNames): キャラクター名およびキャラクター名画像のリスト

        Returns:
            str: キャラクター名文字列
        """
        # キャラクター名画像をマッチさせる範囲(x, y, w, h)
        if left:
            area = ( 29, 24, 122, 27)
        else:
            area = (499, 24, 122, 27)

        name = 'nomatch'

        # 信頼度最大値（max_val）が 0.9 より大きければマッチしたとみなす
        for nm, img in zip(charnames.names, charnames.images):
            if self.is_matchimage(img, area, cv2.IMREAD_GRAYSCALE, 0.9):
                name = nm
                break

        return name
