import cv2
import numpy as np
from collections import OrderedDict

from constants import Constants as C
from char_names import CharNames
from match_template import MatchTemplate


class AnalyzeVideo:
    """動画ファイルを解析するクラス
    Attributes:
        capture (cv2.VideoCapture): 動画ファイルのキャプチャオブジェクト
        fps (float): 動画のフレームレート
        totalframes (int): 動画の総フレーム数
        frame (numpy.ndarray): 現在のフレーム情報
        frame_no (int): 現在のフレーム番号
    """


#    def __init__(self, video_data: AnalyzedVideoData):
    def __init__(self):
        """コンストラクタ
        """
        self.capture = None
        self.fps = 0.0
        self.totalframes = 0
        self.frame = None
        self.frame_no = 0
        self.frame_cache = OrderedDict()
        self.charanames = CharNames()
        self.matchtemplate = MatchTemplate()


    def file_open(self, file: str) -> bool:
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


    def get_fps(self) -> float:
        """動画のフレームレートを取得

        Returns:
            float: 動画のフレームレート
        """
#        return self.fps
        return self.capture.get(cv2.CAP_PROP_FPS)


    def get_totalframes(self) -> int:
        """動画のフレーム数を取得

        Returns:
            int: 動画のフレーム数
        """
#        return self.totalframes
        return int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))


# ここから フレーム移動関連
    def _update_cache(self, frame_no, frame):
        """フレームのデータをキャッシュに保存

        Args:
            frame_no (int): フレーム番号
            frame (numpy.ndarray): フレーム

        """
        self.frame_cache[frame_no] = frame
        if len(self.frame_cache) > C.PROC_SPD.FRAME_CACHE_SIZE:
            self.frame_cache.popitem(last=False)  # FIFOで削除


    def set_frame(self, target_fno: int) -> bool:
        """動画内の指定したフレーム番号に飛ぶ（高速化）

        Args:
            target_fno (int): フレーム番号

        Returns:
            bool: 指定したフレームに飛べればTrue、そうでなければFalse
        """
        # キャッシュにあれば即利用
        if target_fno in self.frame_cache:
            self.frame = self.frame_cache[target_fno]
            self.frame_no = target_fno
            return True

        # 現在位置取得
        current_fno = int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))
        delta = target_fno - current_fno

        if 0 < delta <= C.PROC_SPD.MAX_SEQUENTIAL_READ:
            # 近距離なら read() で進める
            for _ in range(delta):
                ret, _ = self.capture.read()
            ret, frame = self.capture.read()
        else:
            # 遠距離なら直接 set() する
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, target_fno)
            ret, frame = self.capture.read()

        if ret:
            # 解像度 640×360（16:9） に揃える
            frame_resized = cv2.resize(frame, C.IMG_MATCH.BASE_RESOLUTION[2:])
            self.frame = frame_resized
            self.frame_no = target_fno
            self._update_cache(target_fno, frame_resized)

        return ret

# ここまで フレーム移動関連

# ここから 画像照合関連
    def get_maxval(self, image, area=C.IMG_MATCH.BASE_RESOLUTION, color=cv2.IMREAD_COLOR) -> float:
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


    def is_matchimage(self, image, area=C.IMG_MATCH.BASE_RESOLUTION, color=cv2.IMREAD_COLOR, threshold=0.7) -> bool:
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

# ここまで 画像照合関連

# ここから フラッグ関連
    def get_color_match_ratio(self, frame_hsv, hsv_ranges) -> float:
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


    def is_red_or_white(self, area) -> int:
        """現在のフレーム内で、指定した範囲のピクセルが、赤か白かそれ以外かを判定

        Args:
            area (tuple): 範囲（ (x, y, w, h) 左上の座標,幅,高さ）。フレーム全体の大きさは(640×360)とする

        Returns:
            int: 2 赤、 1 白、 0 それ以外
        """
        x, y, w, h = area
        frame_hsv = cv2.cvtColor(self.frame[y:y+h, x:x+w], cv2.COLOR_BGR2HSV)

        match_ratio_wh = self.get_color_match_ratio(frame_hsv, C.IMG_MATCH.HSV_RANGES_WH)
        if match_ratio_wh > 0.7:
            return C.IMG_MATCH.FLAGCOLOR_WH

        match_ratio_rd = self.get_color_match_ratio(frame_hsv, C.IMG_MATCH.HSV_RANGES_RD)
        if match_ratio_rd > 0.7:
            return C.IMG_MATCH.FLAGCOLOR_RD

        return C.IMG_MATCH.FLAGCOLOR_NO


    def get_flagcolor(self, left: bool, n: int) -> int:
        """現在のフレーム内で、指定した位置のフラッグの色を返す

        Args:
            left (bool): 左（True）、右（False）
            n (int): 1 ～ 7 の数字

        Returns:
            int: 2 赤、 1 白、 0 それ以外
        """
        if (n < 1) or (n > C.IMG_MATCH.MAX_FLAGS):
            return C.IMG_MATCH.FLAGCOLOR_NO

        if left:
            x = C.IMG_MATCH.AREA_FLAG_XL + (C.IMG_MATCH.AREA_FLAG_SPC * (n-1))
        else:
            x = C.IMG_MATCH.AREA_FLAG_XR - (C.IMG_MATCH.AREA_FLAG_SPC * (n-1))

        area = (x, ) + C.IMG_MATCH.AREA_FLAG_YWH
        return self.is_red_or_white(area)


    def get_maxflags(self) -> int:
        """現在のフレーム内での、最大フラッグ数を取得

        Returns:
            int: 最大フラッグ数
        """

        # 左右のフラッグ位置を順にチェック
        for i in range( C.IMG_MATCH.MAX_FLAGS ):
            k = i + 1
            flagcolor_L = self.get_flagcolor(True,  k)
            flagcolor_R = self.get_flagcolor(False, k)

            if ( flagcolor_L == C.IMG_MATCH.FLAGCOLOR_NO ) or ( flagcolor_R == C.IMG_MATCH.FLAGCOLOR_NO ):
                # i+1番目のエリアの左右どちらかでもフラッグではないと判定した場合、i を max_flags として返す
                return i

        # ループを全て抜けた場合、最大フラッグ数を7とする
        return C.IMG_MATCH.MAX_FLAGS


    def is_lastoneflag(self, max_flags: int) -> bool:
        """現在のフレームが、あと1フラッグで決着する状態かを判定
        Args:
            max_flags (int): 最大フラッグ数

        Returns:
            bool: あと1フラッグで決着する状態なら True
        """
        if max_flags == 1:
            return True

        if ( max_flags < 1 ) or ( max_flags > C.IMG_MATCH.MAX_FLAGS ):
            return False

        temp_maxflags = max_flags - 1

        flagcolor_L = self.get_flagcolor(True,  temp_maxflags)
        if flagcolor_L == C.IMG_MATCH.FLAGCOLOR_RD:
            return True

        flagcolor_R = self.get_flagcolor(False, temp_maxflags)
        if flagcolor_R == C.IMG_MATCH.FLAGCOLOR_RD:
            return True

        return False


    def is_matchfinished(self, max_flags: int) -> int:
        """現在のフレームが、試合が決着した状態かを判定
        Args:
            max_flags (int): 最大フラッグ数

        Returns:
            int: 0 未決着、1 左側勝利、2 右側勝利
        """
        if ( max_flags < 1 ) or ( max_flags > C.IMG_MATCH.MAX_FLAGS ):
            return C.IMG_MATCH.WIN_N

        temp_maxflags = max_flags

        flagcolor_L = self.get_flagcolor(True,  temp_maxflags)
        if flagcolor_L == C.IMG_MATCH.FLAGCOLOR_RD:
            return C.IMG_MATCH.WIN_L

        flagcolor_R = self.get_flagcolor(False, temp_maxflags)
        if flagcolor_R == C.IMG_MATCH.FLAGCOLOR_RD:
            return C.IMG_MATCH.WIN_R

        return C.IMG_MATCH.WIN_N


    def get_flags(self, max_flags: int, win: int):
        """現在のフレームの獲得フラッグ数をカウント

        Args:
            max_flags (int): 最大フラッグ数
            win (int): 左右どちらが勝利したか

        Returns:
            int: 左プレイヤー獲得フラッグ数
            int: 右プレイヤー獲得フラッグ数
        """
        flags_L = 0
        flags_R = 0

        # 左側のフラッグ数をカウント
        if win != C.IMG_MATCH.WIN_L:
            for i in range(max_flags):
                flagcolor_L = self.get_flagcolor(True,  i+1)

                if flagcolor_L == C.IMG_MATCH.FLAGCOLOR_RD:
                    # i+1 番目のフラッグが赤ならば、獲得フラッグ数を +1 する
                    flags_L += 1
                else:
                    # i+1 番目のフラッグが赤でないならば、これ以上 flags_L が増えることはないためループを抜ける
                    break;
        else:
            flags_L = max_flags

        # 右側のフラッグ数をカウント
        if win != C.IMG_MATCH.WIN_R:
            for i in range(max_flags):
                flagcolor_R = self.get_flagcolor(False, i+1)

                if flagcolor_R == C.IMG_MATCH.FLAGCOLOR_RD:
                    # i+1 番目のフラッグが赤ならば、獲得フラッグ数を +1 する
                    flags_R += 1
                else:
                    # i+1 番目のフラッグが赤でないならば、これ以上 flags_R が増えることはないためループを抜ける
                    break;
        else:
            flags_R = max_flags

        return flags_L, flags_R

# ここまで フラッグ関連


# ここから 画面ステータス関連
    def is_duringmatch(self) -> int:
        """現在のフレームが、対戦画面か（画面上部左右にフラッグがあるか）を判定

        Returns:
            int: 0 対戦画面ではない。1 対戦画面・試合成立前。2 対戦画面・試合成立後。
        """
        # 左右1フラッグ目の位置の色を取得
        flagcolor_L1 = self.get_flagcolor(True,  1)
        flagcolor_R1 = self.get_flagcolor(False, 1)

        if ( flagcolor_L1 == C.IMG_MATCH.FLAGCOLOR_NO ) or  ( flagcolor_R1 == C.IMG_MATCH.FLAGCOLOR_NO ):
            # 0 左右どちらか一方でもフラッグではない
            return C.STAT.STATNO_ISNOTMATCH

        if ( flagcolor_L1 == C.IMG_MATCH.FLAGCOLOR_WH ) and ( flagcolor_R1 == C.IMG_MATCH.FLAGCOLOR_WH ):
            # 1 白・白
            return C.STAT.STATNO_MATCHINVALID

        #     2 赤・白、白・赤、赤・赤
        return C.STAT.STATNO_MATCHVALID


    def is_charaselect(self) -> bool:
        """現在のフレーム内が、キャラクター選択画面かを判定

        Returns:
            bool: キャラクター選択画面ならばTrue
        """
        return self.is_matchimage(self.matchtemplate.img_charaselect, C.IMG_MATCH.AREA_CHARASELECT, C.MATCH_TEMPLATE.CHARASEL_COLOR)


    def is_blackout(self) -> bool:
        """現在のフレーム内で、指定した範囲が、暗転しているかを判定

        Returns:
            bool: 暗転していればTrue
        """
        x, y, w, h = C.IMG_MATCH.AREA_CHKBLACKOUT
        frame_gray = cv2.cvtColor(self.frame[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)
        # 指定範囲の平均輝度を取得
        mean_brightness = cv2.mean(frame_gray)[0]
        if mean_brightness < 0.1:
            return True

        return False


    def get_screen(self) -> str:
        """現在のフレームのステータス（どの画面か）を取得

        Returns:
            str: ステータス文字列
        """
        ret = self.is_duringmatch()

        if ret == C.STAT.STATNO_MATCHINVALID:
            #対戦画面・試合成立前
            return C.STAT.SCRN_MATCHINVALID

        if ret == C.STAT.STATNO_MATCHVALID:
            #対戦画面・試合成立後
            return C.STAT.SCRN_MATCHVALID

        #if self.is_charaselect():
        if self.is_matchimage(self.matchtemplate.img_charaselect, C.IMG_MATCH.AREA_CHARASELECT, C.MATCH_TEMPLATE.CHARASEL_COLOR):
            #キャラクター選択画面
            return C.STAT.SCRN_CHARASELECT

        if self.is_blackout():
            #暗転画面
            return C.STAT.SCRN_BLACKOUT

        return C.STAT.SCRN_OTHERS


    def get_screen2(self, prev_status: str) -> str:
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
            C.STAT.SCRN_MATCHVALID:   lambda: ret_duringmatch() == C.STAT.STATNO_MATCHVALID,
            C.STAT.SCRN_MATCHINVALID: lambda: ret_duringmatch() == C.STAT.STATNO_MATCHINVALID,
            C.STAT.SCRN_CHARASELECT:  lambda: self.is_charaselect(),
            C.STAT.SCRN_BLACKOUT:     lambda: self.is_blackout()
        }

        # 判定順の初期値（柔軟に順番を決める）
        default_order = [
            C.STAT.SCRN_MATCHVALID,
            C.STAT.SCRN_MATCHINVALID,
            C.STAT.SCRN_CHARASELECT,
            C.STAT.SCRN_BLACKOUT
        ]

        if prev_status in default_order:
            # prev_status を先頭に移動（優先判定）
            ordered_statuses = [prev_status] + [s for s in default_order if s != prev_status]
        else:
            ordered_statuses = default_order

        # 順に評価し、最初にマッチしたものを返す
        for status in ordered_statuses:
            if check_map[status]():
                return status

        return C.STAT.SCRN_OTHERS

# ここまで 画面ステータス関連

# ここから キャラクタ名関連
    def get_charaname(self, left: bool, charnames):
        """現在のフレーム内で表示されているキャラクター名（片方）を取得

        Args:
            left (bool): 左（True）、右（False）
            charnames (CharNames): キャラクター名およびキャラクター名画像のリスト

        Returns:
            str: キャラクター名文字列
            float: 信頼度最大値
        """
        # キャラクター名画像をマッチさせる範囲(x, y, w, h)
        if left:
            area = C.IMG_MATCH.AREA_CHARNAME_L
        else:
            area = C.IMG_MATCH.AREA_CHARNAME_R

        name = C.CHAR.NOMATCH
        max_temp = 0.0

        matched_characters = []

        # 信頼度最大値（max_val）が 0.6 より大きいもののうち、最大のものを返す
        for charadata in charnames:
            max_val = self.get_maxval(charadata['image'], area, C.CHAR.COLOR)
            if max_val > max_temp:
                max_temp = max_val
                name = charadata['charname']

        if max_temp > 0.6:
            return  name, max_temp

        return C.CHAR.NOMATCH, max_temp


    def get_charanames(self, fno_eofcharasel):
        """指定したフレーム番号で表示されているキャラクター名（左右）を取得

        Args:
            fno_eofmatch (int): キャラクター名を取得するフレーム番号

        Returns:
            str: キャラクター名文字列（左）
            str: キャラクター名文字列（右）
            float: 信頼度最大値（左）
            float: 信頼度最大値（右）
        """
        # 元のフレーム番号を退避
        fno_temp = self.frame_no
        ret = self.set_frame(fno_eofcharasel)

        name_L, maxval_L = self.get_charaname(True,  self.charanames.charnames_L)
        name_R, maxval_R = self.get_charaname(False, self.charanames.charnames_R)

        # 元のフレーム番号に戻す
        ret = self.set_frame(fno_temp)
        return name_L, name_R, maxval_L, maxval_R

# ここまで キャラクタ名関連



###### デバッグ用
#            xL = C.IMG_MATCH.AREA_FLAG_XL + (C.IMG_MATCH.AREA_FLAG_SPC * i)
#            area = (xL, ) + C.IMG_MATCH.AREA_FLAG_YWH
#            x, y, w, h = area
#            frame_hsv = cv2.cvtColor(self.frame[y:y+h, x:x+w], cv2.COLOR_BGR2HSV)
#            h, s, v = cv2.split(frame_hsv)

#            # 各チャンネルの最小・最大値を取得
#            h_min, h_max = np.min(h), np.max(h)
#            s_min, s_max = np.min(s), np.max(s)
#            v_min, v_max = np.min(v), np.max(v)
#            print(f'{i}: MIN [{h_min:3d}, {s_min:3d}, {v_min:3d}]')
#            print(f'{i}: MAX [{h_max:3d}, {s_max:3d}, {v_max:3d}]')
######
