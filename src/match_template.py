"""ロード画面など画像管理
"""
import os
import cv2
from constants import Constants as C


class MatchTemplate:
    """ロード画面など画像管理クラス
    """


    def __init__(self):
        """コンストラクタ
        """
        CHAR = os.path.join(C.MATCH_TEMPLATE.DIR, C.MATCH_TEMPLATE.CHARA)
        self.charaselect = cv2.imread(CHAR, C.MATCH_TEMPLATE.CHARA_FLG)
