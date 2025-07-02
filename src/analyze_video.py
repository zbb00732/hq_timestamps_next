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

    # 定数
    # 各種画面判定エリア
    #AREA_CHARASELECT = (240,  70, 170, 120)
    AREA_CHARASELECT = (174,   0,  37, 360)
    AREA_CHARNAME_L  = ( 29,  24, 122,  27)
    AREA_CHARNAME_R  = (499,  24, 122,  27)
    #AREA_ARENASELECT = (230,   0, 180,  40)
    AREA_ARENASELECT = (229,   0, 182,  41)
    #AREA_LOADSCREEN  = (192, 100, 256, 192)
    AREA_LOADSCREEN  = (191,  99, 258, 194)
    AREA_CHKBLACKOUT = (160,   0, 320, 180)

    def __init__(self, video_data: AnalyzedVideoData):
        """コンストラクタ
        """
        self.capture = None
        self.fps = 0.0
        self.totalframes = 0
        self.frame = None
        self.frame_no = 0

        # 検出する画像の読み込み
        #self.img_loadscreen  = cv2.imread('matchtemplate/loadscreen.png', cv2.IMREAD_GRAYSCALE)
        self.img_loadscreen  = cv2.imread('matchtemplate/loadscreen.png', cv2.IMREAD_COLOR)
        self.img_charaselect = cv2.imread('matchtemplate/charaselect.png', cv2.IMREAD_COLOR)
        self.img_arenaselect = cv2.imread('matchtemplate/arenaselect.png', cv2.IMREAD_COLOR)


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

    def get_maxval(self, image, area=(0, 0, 640, 360), color=cv2.IMREAD_COLOR):
        """現在のフレーム内で、指定した範囲の、指定した画像とマッチした度合（信頼度最大値）を取得

        Args:
            image (ndarray): 画像（cv2.imread()で読み込んだオブジェクト）
            area (tuple): 範囲（ (x, y, w, h) 左上の座標,幅,高さ）。フレーム全体の大きさは(640×360)とする
                          cv2.matchTemplate の性質上、image よりも少し大きめに指定するとよい
            color (int): 0(cv2.IMREAD_GRAYSCALE):グレースケール、1(cv2.IMREAD_COLOR):カラー

        Returns:
            float: 信頼度最大値
        """
        x, y, w, h = area
        frame = self.frame[y:y+h, x:x+w]

        if color == cv2.IMREAD_GRAYSCALE:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        result1 = cv2.matchTemplate(frame, image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result1)

        return max_val


    def is_matchimage(self, image, area=(0, 0, 640, 360), color=cv2.IMREAD_COLOR, threshold=0.7):
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
        max_val = self.get_maxval(image, area, color)
        # 信頼度最大値（max_val）が threshold より大きければマッチしたとみなす
        if max_val > threshold:
            print(f'max_val: {max_val}')
            return True

        return False


    def is_blackout(self):
        """現在のフレーム内で、指定した範囲が、暗転しているかを判定

        Returns:
            bool: 暗転していればTrue
        """
        x, y, w, h = self.AREA_CHKBLACKOUT
        frame_gray = cv2.cvtColor(self.frame[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)
        # 指定範囲の平均輝度を取得
        mean_brightness = cv2.mean(frame_gray)[0]
        if mean_brightness < 0.1:
            #print(f'mean_brightness: {mean_brightness}')
            return True

        return False


    def get_status(self):
        """現在のフレームのステータス（どの画面か）を取得

        Returns:
            str: ステータス文字列
        """

        if   self.is_matchimage(self.img_charaselect, self.AREA_CHARASELECT):
            return 'charaselect'
        elif self.is_matchimage(self.img_arenaselect, self.AREA_ARENASELECT):
            return 'arenaselect'
        elif self.is_matchimage(self.img_loadscreen,  self.AREA_LOADSCREEN):
            return 'loadscreen'
        elif self.is_blackout():
            return 'blackout'

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
            area = self.AREA_CHARNAME_L
        else:
            area = self.AREA_CHARNAME_R

        name = 'nomatch'
        max_temp = 0

        # 信頼度最大値（max_val）が 0.9 より大きいもののうち、最大のものを返す
        for nm, img in zip(charnames.names, charnames.images):
            max_val = self.get_maxval(img, area, cv2.IMREAD_GRAYSCALE)
            if max_val > 0.9:
                if max_val > max_temp:
                    max_temp = max_val
                    name = nm

        #print(f'max_temp: {max_temp}')
        return name
