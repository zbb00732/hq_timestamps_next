"""タイムスタンプ出力
"""
import os
import datetime
from constants import Constants as C

class TimestampsOutput:
    """タイムスタンプ出力クラス
    """


    def __init__(self):
        """コンストラクタ
        """
        output_dir = datetime.date.today().strftime('%Y%m%d')
        self.output_file = output_dir + C.OUTPUT_FILE
        self.statis_file = output_dir + C.STATIS_FILE

        # 出力ファイルが既に存在しているなら削除
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

        if os.path.exists(self.statis_file):
            os.remove(self.statis_file)


    def write(self, timestamps: list):
        """タイムスタンプをファイルに書き込む

        Args:
            timestamps (list): タイムスタンプのリスト
        """
        with open(self.output_file, 'w', encoding=C.OUTPUT_ENCODING) as file:
            for timestamp in timestamps:
                file.write(f'{timestamp}')


    def write_stat(self, statistics: list):
        """解析結果統計情報をファイルに書き込む

        Args:
            timestamps (list): タイムスタンプのリスト
        """
        with open(self.statis_file, 'w', encoding=C.OUTPUT_ENCODING) as file:
            for stat in statistics:
                file.write(f'{stat}')
