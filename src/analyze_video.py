import cv2
import numpy as np
#from constants import Constants as C
from analyzed_video_data import AnalyzedVideoData


# 定数
# 各種画面判定エリア
AREA_CHARASELECT = (174,   0,  37, 181)
AREA_CHARNAME_L  = ( 29,  24, 122,  27)
AREA_CHARNAME_R  = (499,  24, 122,  27)
AREA_CHKBLACKOUT = (480,   0, 160,  90)

AREA_FLAG_XL  =  30
AREA_FLAG_XR  = 606
AREA_FLAG_Y   =   6
AREA_FLAG_W   =   6
AREA_FLAG_H   =   6
AREA_FLAG_SPC =  22

# 白のHSV範囲
HSV_RANGES_WH = [
    (np.array([  0,   0, 200]), np.array([180,  30, 255]))
]

# 赤のHSV範囲（2つの範囲）
HSV_RANGES_RD = [
    (np.array([  0, 200,  50]), np.array([ 10, 255, 255])),
    (np.array([170, 200,  50]), np.array([180, 255, 255]))
]


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
        self.img_charaselect = cv2.imread('matchtemplate/charaselect.png', cv2.IMREAD_COLOR)


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
            self.frame = frame_resized
            self.frame_no = frame_no

        return ret


    def get_totalframes(self):
        """動画のフレーム数を取得

        Returns:
            int: 動画のフレーム数
        """
        return self.totalframes


# ここから 画像照合関連
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
            if len(image.shape) > 2:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

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
            #print(f'max_val: {max_val}')
            return True

        return False


    def is_blackout(self):
        """現在のフレーム内で、指定した範囲が、暗転しているかを判定

        Returns:
            bool: 暗転していればTrue
        """
        x, y, w, h = AREA_CHKBLACKOUT
        frame_gray = cv2.cvtColor(self.frame[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)
        # 指定範囲の平均輝度を取得
        mean_brightness = cv2.mean(frame_gray)[0]
        if mean_brightness < 0.1:
            return True

        return False

# ここまで 画像照合関連

# ここから フラッグ関連
    def get_color_match_ratio(self, frame_hsv, hsv_ranges):
        """指定したフレーム内のピクセルが、指定した色範囲に含まれる割合を取得

        Args:
            frame_hsv : HSV形式のフレーム（cv2.COLOR_BGR2HSV）
            hsv_ranges (list of tuple): [(lower1, upper1), (lower2, upper2), ...] 形式のHSV範囲

        Returns:
            float: 色マスクにマッチしたピクセルの割合（0.0〜1.0）
        """
        h, w = frame_hsv.shape[:2]
        combined_mask = np.zeros((h, w), dtype=np.uint8)

        for lower, upper in hsv_ranges:
            mask = cv2.inRange(frame_hsv, lower, upper)
            combined_mask = cv2.bitwise_or(combined_mask, mask)

        # 色マスクにマッチしたピクセル数カウント
        match_pixels = cv2.countNonZero(combined_mask)
        total_pixels = h * w
        if total_pixels > 0:
            return match_pixels / total_pixels

        return 0.0


    def is_red_or_white(self, area):
        """現在のフレーム内で、指定した範囲のピクセルが、赤か白かそれ以外かを判定

        Args:
            area (tuple): 範囲（ (x, y, w, h) 左上の座標,幅,高さ）。フレーム全体の大きさは(640×360)とする

        Returns:
            int: 2 赤、 1 白、 0 それ以外
        """
        x, y, w, h = area
        frame_hsv = cv2.cvtColor(self.frame[y:y+h, x:x+w], cv2.COLOR_BGR2HSV)

        match_ratio_wh = self.get_color_match_ratio(frame_hsv, HSV_RANGES_WH)
        if match_ratio_wh > 0.7:
            return 1

        match_ratio_rd = self.get_color_match_ratio(frame_hsv, HSV_RANGES_RD)
        if match_ratio_rd > 0.7:
            return 2

        return 0


    def get_flagcolor(self, left: bool, n: int):
        """現在のフレーム内で、指定した位置のフラッグの色を返す

        Args:
            left (bool): 左（True）、右（False）
            n (int): 1 ～ 7 の数字

        Returns:
            int: 2 赤、 1 白、 0 それ以外
        """
        if (n < 1) or (n > 7):
            return 0

        if left:
            x = AREA_FLAG_XL + (AREA_FLAG_SPC * (n-1))
        else:
            x = AREA_FLAG_XR - (AREA_FLAG_SPC * (n-1))

        area = (x, AREA_FLAG_Y, AREA_FLAG_W, AREA_FLAG_H)
        return self.is_red_or_white(area)


    def get_maxflags(self):
        """現在のフレーム内での、最大フラッグ数を取得

        Returns:
            int: 最大フラッグ数
        """

        # 左側のフラッグ数をカウント
        for i in range(7):
            flagcolor_L = self.get_flagcolor(True,  i+1)

            if flagcolor_L == 0:
                # i+1番目のエリアが赤でも白でもない場合、i を max_flags として返す
                return i

        # ループを全て抜けた場合、最大フラッグ数を7とする
        return 7


    def is_duringmatch(self):
        """現在のフレームが、対戦画面か（画面上部左右にフラッグがあるか）を判定

        Returns:
            int: 0 対戦画面ではない。1 対戦画面・試合成立前。2 対戦画面・試合成立後。
        """
        # 左1フラッグ目の位置の色を判定
        flagcolor_1L = self.get_flagcolor(True,  1)

        if flagcolor_1L != 1:
            return flagcolor_1L

        # 右1フラッグ目の位置の色を判定
        flagcolor_1R = self.get_flagcolor(False, 1)

        return flagcolor_1R


    def is_lastoneflag(self, max_flags: int):
        """現在のフレームが、あと1フラッグで決着する状態かを判定
        Args:
            max_flags (int): 最大フラッグ数

        Returns:
            bool: あと1フラッグで決着する状態なら True
        """
        if max_flags == 1:
            return True

        if ( max_flags < 1 ) or ( max_flags > 7 ):
            return False

        temp_maxflags = max_flags - 1

        flagcolor_L = self.get_flagcolor(True,  temp_maxflags)
        if flagcolor_L == 2:
            return True

        flagcolor_R = self.get_flagcolor(False, temp_maxflags)
        if flagcolor_R == 2:
            return True

        return False


    def get_flags(self, fno_eofmatch: int, max_flags: int):
        """指定したフレーム番号での獲得フラッグ数をカウント

        Args:
            fno_eofmatch (int): 獲得フラッグ数をカウントするフレーム番号
            max_flags (int): 最大フラッグ数

        Returns:
            int: 左プレイヤー獲得フラッグ数
            int: 右プレイヤー獲得フラッグ数
        """
        flags_L = 0
        flags_R = 0
        # 元のフレーム番号を退避
        fno_temp = self.frame_no
        ret = self.set_frame(fno_eofmatch)

        # 左側のフラッグ数をカウント
        for i in range(max_flags):
            flagcolor_L = self.get_flagcolor(True,  i+1)

            if flagcolor_L == 2:
                # i+1 番目のフラッグが赤ならば、獲得フラッグ数を +1 する
                flags_L += 1
            else:
                # i+1 番目のフラッグが赤でないならば、これ以上 flags_L が増えることはないためループを抜ける
                break;

        # 右側のフラッグ数をカウント
        for i in range(max_flags):
            flagcolor_R = self.get_flagcolor(False, i+1)

            if flagcolor_R == 2:
                # i+1 番目のフラッグが赤ならば、獲得フラッグ数を +1 する
                flags_R += 1
            else:
                # i+1 番目のフラッグが赤でないならば、これ以上 flags_R が増えることはないためループを抜ける
                break;

        # 元のフレーム番号に戻す
        ret = self.set_frame(fno_temp)
        return flags_L, flags_R

# ここまで フラッグ関連


# ここから 画面ステータス関連
    def get_status(self):
        """現在のフレームのステータス（どの画面か）を取得

        Returns:
            str: ステータス文字列
        """
        ret = self.is_duringmatch()

        if ret == 1:
            #対戦画面・試合成立前
            return 'duringmatch_invalid'

        if ret == 2:
            #対戦画面・試合成立後
            return 'duringmatch_valid'

        if self.is_matchimage(self.img_charaselect, AREA_CHARASELECT):
            #キャラクター選択画面
            return 'charaselect'

        if self.is_blackout():
            #暗転画面
            return 'blackout'

        return 'nomatch'


    def get_status2(self, prev_status: str):
        """現在のフレームのステータス（どの画面か）を取得

        Args:
            prev_status (str): 直前のステータス

        Returns:
            str: ステータス文字列
        """
        # is_duringmatch の遅延実行とキャッシュ
        _ret_duringmatch = None
        def ret_duringmatch():
            nonlocal _ret_duringmatch
            if _ret_duringmatch is None:
                _ret_duringmatch = self.is_duringmatch()
            return _ret_duringmatch

        # 判定関数マッピング（すべて遅延評価）
        check_map = {
            'duringmatch_valid':   lambda: ret_duringmatch() == 2,
            'duringmatch_invalid': lambda: ret_duringmatch() == 1,
            'charaselect':         lambda: self.is_matchimage(self.img_charaselect, AREA_CHARASELECT),
            'blackout':            lambda: self.is_blackout()
        }

        # 判定順の初期値（柔軟に順番を決める）
        default_order = ['duringmatch_valid', 'duringmatch_invalid', 'charaselect', 'blackout']

        if prev_status in default_order:
            # prev_status を先頭に移動（優先判定）
            ordered_statuses = [prev_status] + [s for s in default_order if s != prev_status]
        else:
            ordered_statuses = default_order

        # 順に評価し、最初にマッチしたものを返す
        for status in ordered_statuses:
            if check_map[status]():
                return status

        return 'nomatch'
# ここまで ステータス関連


# ここから キャラクタ名関連
    def get_charaname(self, left: bool, charnames):
        """現在のフレーム内で表示されているキャラクター名を取得

        Args:
            left (bool): 左（True）、右（False）
            charnames (CharNames): キャラクター名およびキャラクター名画像のリスト

        Returns:
            str: キャラクター名文字列
            float: 信頼度最大値
        """
        # キャラクター名画像をマッチさせる範囲(x, y, w, h)
        if left:
            area = AREA_CHARNAME_L
        else:
            area = AREA_CHARNAME_R

        name = 'nomatch'
        max_temp = 0

        # 信頼度最大値（max_val）が 0.6 より大きいもののうち、最大のものを返す
        for nm, img in zip(charnames.names, charnames.images):
            max_val = self.get_maxval(img, area, cv2.IMREAD_GRAYSCALE)
            #max_val = self.get_maxval(img, area)
            if max_val > 0.6:
                if max_val > max_temp:
                    max_temp = max_val
                    name = nm

        return name, max_temp


    def get_charanames(self, fno_eofcharasel, charnames_L, charnames_R):
        """指定したフレーム番号で表示されているキャラクター名（左右）を取得

        Args:
            fno_eofmatch (int): 獲得フラッグ数をカウントするフレーム番号
            charnames_L (CharNames): キャラクター名およびキャラクター名画像のリスト（左）
            charnames_R (CharNames): キャラクター名およびキャラクター名画像のリスト（右）

        Returns:
            str: キャラクター名文字列（左）
            str: キャラクター名文字列（右）
            float: 信頼度最大値（左）
            float: 信頼度最大値（右）
        """
        # 元のフレーム番号を退避
        fno_temp = self.frame_no
        ret = self.set_frame(fno_eofcharasel)

        name_L, maxval_L = self.get_charaname(True,  charnames_L)
        name_R, maxval_R = self.get_charaname(False, charnames_R)

        # 元のフレーム番号に戻す
        ret = self.set_frame(fno_temp)
        return name_L, name_R, maxval_L, maxval_R

# ここまで キャラクタ名関連

