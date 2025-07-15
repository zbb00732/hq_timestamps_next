"""キャラクター選択画面など画像管理
"""
import os
import cv2
from constants import Constants as C


class MatchTemplate:
    """キャラクター選択画面など画像管理クラス
    """


    def __init__(self):
        """コンストラクタ
        """
        filepath_charasel = os.path.join(C.MATCH_TEMPLATE.DIR, C.MATCH_TEMPLATE.CHARASELECT)
        self.img_charaselect = cv2.imread(filepath_charasel, C.MATCH_TEMPLATE.CHARASEL_COLOR)
