"""キャラクター名およびキャラクター名画像管理
"""
import os
import cv2
from constants import CONSTANTS as C


class CharNames:
    """キャラクター名およびキャラクター名画像クラス

    Attributes:
        names (list): キャラクター名のリスト
        images (list): キャラクター名画像のリスト
    """

    def __init__(self, image_dir: str):
        """コンストラクタ

        Args:
            dirname (str): キャラクター名画像のディレクトリ名
        """
        self.names = []
        self.images = []

        # ディレクトリ内のファイルを取得
        for file in os.listdir(image_dir):
            # キャラクター名画像の拡張子が一致する場合
            if file.endswith(C.CHAR_IMG_EXT):
                # 画像を読み込み
                image = cv2.imread(os.path.join(image_dir, file))
                if image is not None:
                    self.images.append(image)

            file = file.replace(C.CHAR_IMG_EXT, '')
            file = file.replace(C.CHAR_L_PRE, '')
            file = file.replace(C.CHAR_R_PRE, '')
            self.names.append(file)
