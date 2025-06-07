"""ユーティリティ関数
"""
import os
import sys
import re
from tkinter import filedialog
import FreeSimpleGUI as sg
import cv2
from constants import CONSTANTS as C


def get_char_name(image_dir):
    """キャラクター名画像を取得する

    Args:
        image_dir (str): キャラクター名画像のディレクトリ

    Returns:
        tuple:
            names (list): キャラクター名のリスト
            images (list): キャラクター名画像のリスト
    """

    names = []
    images = []
    p = re.compile('(hq1_|hq2_|.png)')

    for file in os.listdir(image_dir):
        if file.endswith(C.CHAR_IMG_EXT):
            img = cv2.imread(os.path.join(image_dir, file))
            if img is not None:
                resized = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                images.append(resized)

        file = file.replace(C.CHAR_LEFT_PREFIX, '')
        file = file.replace(C.CHAR_RIGHT_PREFIX, '')
        file = file.replace(C.CHAR_IMG_EXT, '')
        names.append(file)

    return names, images
