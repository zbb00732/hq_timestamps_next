"""定数定義ファイル
"""
import re
import cv2
import numpy as np
from dataclasses import dataclass


@dataclass(frozen=True)
class Window:
    """ウィンドウ定数クラス
    """
    THEME = 'Dark Red'
    TITLE = 'Hellish Quartのタイムスタンプ生成'
    TEXT = 'Hellish Quart Timestamp'


@dataclass(frozen=True)
class Bar:
    """プログレスバー定数クラス
    """
    MAX = 100         # プログレスバーの最大値
    ORIENTATION = 'h' # プログレスバーの方向
    WIDTH = 20        # プログレスバーの幅
    HEIGHT = 20       # プログレスバーの高さ
    KEY = '-PROG-'    # プログレスバーのキー


@dataclass(frozen=True)
class Char:
    """キャラクター名定数クラス
    """
    NAMEDIR_L = 'name_l'          # 左側キャラクター名画像のディレクトリ名
    NAMEDIR_R = 'name_r'          # 右側キャラクター名画像のディレクトリ名
    PATTERN = re.compile(r'^hq\d_(.+)_\d+\.png$', re.IGNORECASE)  # キャラクター名画像の正規表現マッチパターン
    COLOR = cv2.IMREAD_GRAYSCALE  # キャラクター名画像をカラーかグレースケールのどちらで扱うか
    NOMATCH = 'nomatch'           # キャラクター名がマッチしなかった場合に返す文字列


@dataclass(frozen=True)
class MatchTemplate:
    """ロード画面など画像管理定数
    """
    DIR = 'matchtemplate'              # ロード画面などの画像ディレクトリ名
    CHARASELECT = 'charaselect.png'    # キャラクター選択画面
    CHARASEL_COLOR = cv2.IMREAD_COLOR  # キャラクター選択画面をカラーかグレースケールのどちらで扱うか


@dataclass(frozen=True)
class ImageMatching:
    """画像照合定数
    """
    BASE_RESOLUTION  = (  0,   0, 640, 360)  # フレームの解像度を揃える

    AREA_CHARASELECT = (174,   0,  37, 181)  # キャラクター選択画面の画像
    AREA_CHARNAME_L  = ( 29,  24, 122,  27)  # キャラクター名・左
    AREA_CHARNAME_R  = (499,  24, 122,  27)  # キャラクター名・右
    AREA_CHKBLACKOUT = (480,   0, 160,  90)  # 暗転

    AREA_FLAG_XL     =   30                  # 左1番目フラッグ X 座標
    AREA_FLAG_XR     =  606                  # 右1番目フラッグ X 座標
    AREA_FLAG_YWH    = (       6,   6,   6)  # フラッグ Y 座標、幅width、高さheight
    AREA_FLAG_SPC    =   22                  # フラッグが並ぶ間隔

    HSV_RANGES_WH = [                        # 白のHSV範囲
        (np.array([  0,   0, 150]), np.array([180,  30, 255]))
    ]

    HSV_RANGES_RD = [                        # 赤のHSV範囲（2つの範囲）
        (np.array([  0, 200,  50]), np.array([ 10, 255, 255])),
        (np.array([170, 200,  50]), np.array([180, 255, 255]))
    ]

    FLAGCOLOR_RD  = 2  # 赤
    FLAGCOLOR_WH  = 1  # 白
    FLAGCOLOR_NO  = 0  # フラッグではない

    MAX_FLAGS     = 7  # フラッグ表示される最大数

    WIN_R = 2  # 右プレイヤー勝利
    WIN_L = 1  # 左プレイヤー勝利
    WIN_N = 0  # 未決着


@dataclass(frozen=True)
class ProcessSpeed:
    """処理速度関連定数
    """
    FRAME_CACHE_SIZE    = 30   # フレームをキャッシュする件数
    MAX_SEQUENTIAL_READ = 40   # VideoCapture.set() でなく read() を使う最大値

    # 処理をスキップする間隔（秒）
    INTVL_CHARASELECT   = 1/4  # キャラクター選択画面
    INTVL_MATCHFINISHED = 2    # 試合終了後
    INTVL_LASTONEFLAG   = 1/2  # 残り１フラッグ
    INTVL_MATCHSTARTED  = 3    # 対戦画面
    INTVL_BLACKOUT      = 1    # 暗転画面
    INTVL_OTHERS        = 2    # その他画面


@dataclass(frozen=True)
class StateTransition:
    """状態遷移定数
    """
    STATNO_MATCHVALID   = 2  # 対戦画面・試合成立後
    STATNO_MATCHINVALID = 1  # 対戦画面・試合開始後
    STATNO_ISNOTMATCH   = 0  # 対戦画面ではない

    SCRN_CHARASELECT    = 'charaselect'          # キャラクター選択画面
    SCRN_MATCHINVALID   = 'duringmatch_invalid'  # 対戦画面・試合開始後
    SCRN_MATCHVALID     = 'duringmatch_valid'    # 対戦画面・試合成立後
    SCRN_BLACKOUT       = 'blackout'             # 暗転
    SCRN_OTHERS         = 'nomatch'              # その他



@dataclass(frozen=True)
class Constants:
    """定数クラス
    """
    WINDOW         = Window()           # ウィンドウ定数
    BAR            = Bar()              # プログレスバー定数
    CHAR           = Char()             # キャラクター名定数
    MATCH_TEMPLATE = MatchTemplate()    # ロード画面など画像管理定数
    IMG_MATCH      = ImageMatching()    # 画像照合定数
    PROC_SPD       = ProcessSpeed()     # 処理速度関連定数
    SCREEN         = StateTransition()  # 画面状態定数

    ONCLICK_CANCEL = 'Cancel' # キャンセルイベント
    CANCEL_KEY = '-CANCEL-'   # キャンセルボタンのキー

    OUTPUT_FILE = 'timestamps.txt' # タイムスタンプ出力ファイル名
    STATIS_FILE = 'statistics.txt' # 処理結果統計情報出力ファイル名
    OUTPUT_ENCODING = 'utf-8'      # 出力ファイルのエンコーディング
