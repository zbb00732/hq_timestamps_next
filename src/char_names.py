"""キャラクター名およびキャラクター名画像管理
"""
import os
import cv2
from constants import Constants as C


class CharNames:
    """キャラクター名およびキャラクター名画像クラス

    Attributes:
        charnames_L (list): キャラクターデータのリスト（左）
        charnames_R (list): キャラクターデータのリスト（右）

    """


    def __init__(self):
        """コンストラクタ
        """
        self.charnames_L = self._load_images(C.CHAR.NAMEDIR_L)
        self.charnames_R = self._load_images(C.CHAR.NAMEDIR_R)


    def _load_images(self, image_dir: str):
        """指定のディレクトリ内にある画像をロード

        Args:
            image_dir (str): キャラクター名画像のディレクトリ名

        Returns:
            list: 以下のような連想配列のリスト
            [
                {'filename': 'hq10_Jan.png',   'image': <画像データ>, 'charname': 'Jan'},
                {'filename': 'hq10_Dynis.png', 'image': <画像データ>, 'charname': 'Dynis'},
                ...
            ]
        """
        char_list = []

        # ディレクトリ内のファイルを取得
        for filename in os.listdir(image_dir):
            match = C.CHAR.PATTERN.match(filename)
            if match:
                # キャラクター画像ファイル名が正規表現パターンにマッチした場合、リストに追加する
                character_name = match.group(1)
                img = cv2.imread(os.path.join(image_dir, filename), C.CHAR.COLOR)

                if img is not None:
                    char_list.append({
                        'filename': filename,
                        'image': img,
                        'charname': character_name
                    })
                else:
                    print(f"[WARN] 画像の読み込みに失敗: {file_path}")

        return char_list
