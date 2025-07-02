"""定数定義ファイル
"""
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
    LEFT_DIR = 'name_l'  # 左側キャラクター名画像のディレクトリ名
    RIGHT_DIR = 'name_r' # 右側キャラクター名画像のディレクトリ名
    L_PRE = 'hq1_'       # 左側キャラクター名画像のプレフィックス
    R_PRE = 'hq2_'       # 右側キャラクター名画像のプレフィックス
    IMG_EXT = '.png'     # キャラクター名画像の拡張子


@dataclass(frozen=True)
class MatchTemplate:
    """ロード画面など画像管理定数
    """
    DIR = 'matchtemplate'     # ロード画面などの画像ディレクトリ名
    #BLACK = 'black.png'       # 暗転画面
    BLACK_FLG = 1             # 暗転画面読み込みフラグ
    LOAD = 'loadscreen.png'   # ロード画面
    LOAD_FLG = 0              # ロード画面画像読み込みフラグ
    CHARA = 'charaselect.png' # キャラクター選択画面
    CHARA_FLG = 0             # キャラクター選択画面読み込みフラグ
    ARENA = 'arenaselect.png' # ステージ選択画面
    ARENA_FLG = 0             # ステージ選択画面読み込みフラグ


@dataclass(frozen=True)
class Constants:
    """定数クラス
    """
    WINDOW = Window()                # ウィンドウ定数
    BAR = Bar()                      # プログレスバー定数
    CHAR = Char()                    # キャラクター名定数
    MATCH_TEMPLATE = MatchTemplate() # ロード画面など画像管理定数

    ONCLICK_CANCEL = 'Cancel' # キャンセルイベント
    CANCEL_KEY = '-CANCEL-'   # キャンセルボタンのキー

    OUTPUT_FILE = 'timestamps.txt' # タイムスタンプ出力ファイル名
    OUTPUT_ENCODING = 'utf-8'      # 出力ファイルのエンコーディング

    SKIP = 4                       # 指定のフレームおきに処理をスキップ
