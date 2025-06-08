"""定数定義ファイル
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class CONSTANTS:
    """定数クラス
    """

    WINDOW_THEME = 'Dark Red'
    WINDOW_TITLE = 'Hellish Quartのタイムスタンプ生成'
    WINDOW_TEXT = 'Hellish Quart Timestamp'

    BAR_MAX = 100         # プログレスバーの最大値
    BAR_ORIENTATION = 'h' # プログレスバーの方向
    BAR_WIDTH = 20        # プログレスバーの幅
    BAR_HEIGHT = 20       # プログレスバーの高さ
    BAR_KEY = '-PROG-'    # プログレスバーのキー

    ONCLICK_CANCEL = 'Cancel' # キャンセルイベント
    CANCEL_KEY = '-CANCEL-'   # キャンセルボタンのキー

    CHAR_LEFT_DIR = 'name_l'  # 左側キャラクター名画像のディレクトリ名
    CHAR_RIGHT_DIR = 'name_r' # 右側キャラクター名画像のディレクトリ名
    CHAR_IMG_EXT = '.png'     # キャラクター名画像の拡張子
    CHAR_L_PRE = 'hq1_'       # 左側キャラクター名画像のプレフィックス
    CHAR_R_PRE = 'hq2_'       # 右側キャラクター名画像のプレフィックス

    OUTPUT_FILE = 'timestamps.txt' # タイムスタンプ出力ファイル名
    OUTPUT_ENCODING = 'utf-8'      # 出力ファイルのエンコーディング
