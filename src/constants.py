"""定数定義ファイル
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CONSTANTS:
    """定数クラス
    """

    WINDOW_THEME = 'Dark Red'
    WINDOW_TITLE = 'Hellish Quartのタイムスタンプ生成'
    WINDOW_TEXT = 'Hellish Quart Timestamp'

    BAR_MAX = 100             # プログレスバーの最大値
    BAR_ORIENTATION = 'h'     # プログレスバーの方向
    BAR_WIDTH = 20            # プログレスバーの幅
    BAR_HEIGHT = 20           # プログレスバーの高さ
    BAR_KEY = '-PROG-'        # プログレスバーのキー

    ONCLICK_CANCEL = 'Cancel' # キャンセルイベント
    CANCEL_KEY = '-CANCEL-'   # キャンセルボタンのキー

    CHAR_LEFT_DIR = 'name_l'
    CHAR_RIGHT_DIR = 'name_r'
    CHAR_IMG_EXT = '.png'
    CHAR_LEFT_PREFIX = 'hq1_'
    CHAR_RIGHT_PREFIX = 'hq2_'
