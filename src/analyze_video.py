import cv2
import numpy as np
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
    AREA_CHARASELECT = (174,   0,  37, 360)
    AREA_CHARNAME_L  = ( 29,  24, 122,  27)
    AREA_CHARNAME_R  = (499,  24, 122,  27)
    #AREA_ARENASELECT = (229,   0, 182,  41)
    AREA_LOADSCREEN  = (191,  99, 258, 194)
    #AREA_CHKBLACKOUT = (160,   0, 320, 180)

    AREA_FLAG1L      = ( 30,   6,   6,   6)
    AREA_FLAG1R      = (606,   6,   6,   6)

    # 白のHSV範囲
    HSV_RANGES_WH = [
        (np.array([  0,   0, 200]), np.array([180,  30, 255]))
    ]

    # 赤のHSV範囲（2つの範囲）
    HSV_RANGES_RD = [
        (np.array([  0, 200,  50]), np.array([ 10, 255, 255])),
        (np.array([170, 200,  50]), np.array([180, 255, 255]))
    ]


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
        self.img_loadscreen  = cv2.imread('matchtemplate/loadscreen.png', cv2.IMREAD_COLOR)


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


    def get_color_match_ratio(self, area, hsv_ranges):
        """現在のフレーム内で、指定した範囲のピクセルが、指定した色範囲に含まれた割合を取得

        Args:
            area (tuple): 範囲（ (x, y, w, h) 左上の座標,幅,高さ）。フレーム全体の大きさは(640×360)とする
            hsv_ranges (list of tuple): [(lower1, upper1), (lower2, upper2), ...] 形式のHSV範囲

        Returns:
            float: 色マスクにマッチしたピクセルの割合（0.0〜1.0）
        """
        x, y, w, h = area
        frame_hsv = cv2.cvtColor(self.frame[y:y+h, x:x+w], cv2.COLOR_BGR2HSV)
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


#    def is_blackout(self):
#        """現在のフレーム内で、指定した範囲が、暗転しているかを判定
#
#        Returns:
#            bool: 暗転していればTrue
#        """
#        x, y, w, h = self.AREA_CHKBLACKOUT
#        frame_gray = cv2.cvtColor(self.frame[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)
#        # 指定範囲の平均輝度を取得
#        mean_brightness = cv2.mean(frame_gray)[0]
#        if mean_brightness < 0.1:
#            #print(f'mean_brightness: {mean_brightness}')
#            return True
#
#        return False


    def is_duringmatch(self):
        """現在のフレームが、対戦画面か（画面上部左右にフラッグがあるか）を判定

        Returns:
            int: 0 対戦画面ではない。1 対戦画面・試合成立前。2 対戦画面・試合成立後。
        """
        # 左側1フラッグ目の位置の色を判定
        match_ratio_1Lw = self.get_color_match_ratio(self.AREA_FLAG1L, self.HSV_RANGES_WH)
        match_ratio_1Lr = self.get_color_match_ratio(self.AREA_FLAG1L, self.HSV_RANGES_RD)

        # 左側1フラッグ目の位置が白でも赤でもなければ、対戦画面ではない
        if max( match_ratio_1Lw, match_ratio_1Lr) <= 0.6:
            return 0

        # 右側1フラッグ目の位置の色を判定
        match_ratio_1Rw = self.get_color_match_ratio(self.AREA_FLAG1R, self.HSV_RANGES_WH)
        match_ratio_1Rr = self.get_color_match_ratio(self.AREA_FLAG1R, self.HSV_RANGES_RD)

        # 右側1フラッグ目の位置が白でも赤でもなければ、対戦画面ではない（上記if文を通過したのは誤判定とみなす）
        if max( match_ratio_1Rw, match_ratio_1Rr) <= 0.6:
            return 0

        #print(f'Lw : {match_ratio_1Lw}')
        #print(f'Lr : {match_ratio_1Lr}')
        #print(f'Rw : {match_ratio_1Rw}')
        #print(f'Rr : {match_ratio_1Rr}')

        # 左右とも白ならば試合成立前
        if (match_ratio_1Lw > match_ratio_1Lr) and (match_ratio_1Rw > match_ratio_1Rr):
            return 1

        # 左右どちらかまたは両方が赤ならば試合成立後
        return 2


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

        if self.is_matchimage(self.img_charaselect, self.AREA_CHARASELECT):
            #キャラクター選択画面
            return 'charaselect'

        if self.is_matchimage(self.img_loadscreen,  self.AREA_LOADSCREEN):
            #ロード画面
            return 'loadscreen'

        return 'nomatch'


    def get_charaname(self, left, charnames):
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
            area = self.AREA_CHARNAME_L
        else:
            area = self.AREA_CHARNAME_R

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


    def get_flags(self, fno_eofmatch: int):
        """指定したフレーム番号での獲得フラッグ数をカウント

        Args:
            fno_eofmatch (int): 獲得フラッグ数をカウントするフレーム番号

        Returns:
            int: 左プレイヤー獲得フラッグ数
            int: 右プレイヤー獲得フラッグ数
            int: 最大フラッグ数
        """
        max_flags = 7
        flags_L = 0
        flags_R = 0
        # 元のフレーム番号を退避
        fno_temp = self.frame_no
        ret = self.set_frame(fno_eofmatch)

        # 左側のフラッグ数をカウント
        for i in range(7):
            xL =  30 + 22 * i
            area = (xL, 6, 6, 6)
            match_ratio_Lw = self.get_color_match_ratio(area, self.HSV_RANGES_WH)
            match_ratio_Lr = self.get_color_match_ratio(area, self.HSV_RANGES_RD)

            #print(f'Lw({i}) : {match_ratio_Lw}')
            #print(f'Lr({i}) : {match_ratio_Lr}')

            if max( match_ratio_Lw, match_ratio_Lr) <= 0.6:
                # i+1番目のエリアが赤でも白でもない場合、max_flagsを i とし、ループを抜ける
                max_flags = i
                break;

            if match_ratio_Lr > match_ratio_Lw :
                # i+1 番目のフラッグが赤ならば、獲得フラッグ数を +1 する
                flags_L += 1
            else:
                # i+1 番目のフラッグが白ならば、これ以上 flags_L が増えることはないためループを抜ける
                break;

        # 右側のフラッグ数をカウント
        tmp = max_flags
        for i in range(tmp):
            xR = 606 - 22 * i
            area = (xR, 6, 6, 6)
            match_ratio_Rw = self.get_color_match_ratio(area, self.HSV_RANGES_WH)
            match_ratio_Rr = self.get_color_match_ratio(area, self.HSV_RANGES_RD)

            #print(f'Rw({i}) : {match_ratio_Rw}')
            #print(f'Rr({i}) : {match_ratio_Rr}')

            if max( match_ratio_Rw, match_ratio_Rr) <= 0.6:
                # i+1番目のエリアが赤でも白でもない場合、max_flagsを i とし、ループを抜ける
                max_flags = i
                break;

            if match_ratio_Rr > match_ratio_Rw :
                # i+1 番目のフラッグが赤ならば、獲得フラッグ数を +1 する
                flags_R += 1
            else:
                # i+1 番目のフラッグが白ならば、これ以上 flags_R が増えることはないためループを抜ける
                break;

        # 元のフレーム番号に戻す
        ret = self.set_frame(fno_temp)
        return flags_L, flags_R, max_flags
