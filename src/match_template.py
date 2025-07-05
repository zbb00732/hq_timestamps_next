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
        #LOAD = os.path.join(C.MATCH_TEMPLATE.DIR,C. MATCH_TEMPLATE.LOAD)
        CHAR = os.path.join(C.MATCH_TEMPLATE.DIR, C.MATCH_TEMPLATE.CHARA)
        #ARENA = os.path.join(C.MATCH_TEMPLATE.DIR, C.MATCH_TEMPLATE.ARENA)

        #self.loadscreen  = cv2.imread(LOAD, C.MATCH_TEMPLATE.LOAD_FLG)
        self.charaselect = cv2.imread(CHAR, C.MATCH_TEMPLATE.CHARA_FLG)
        #self.arenaselect = cv2.imread(ARENA, C.MATCH_TEMPLATE.ARENA_FLG)
