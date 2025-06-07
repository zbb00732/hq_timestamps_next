# Hellish Quart 動画からタイムスタンプを抽出するツール

## 概要 

## セットアップ

`git clone`の後、`python -m pip install -r requirements.txt`でモジュールをインストールする。

## 実行方法

### 1. 動画ファイル選択

EXEファイルをダブルクリックすると動画ファイル選択ダイアログが表示され、動画を開くと処理を開始する。

### 2. 解析、抽出

### 3. 出力

## 開発者向け情報

### Python

- Python 3.13.3
    - [FreeSimpleGUI](https://freesimplegui.readthedocs.io/en/latest/)
    - [OpenCV](https://opencv.org)
    - [PyInstaller](https://pyinstaller.org/en/stable/)
- モジュールについては`requirements.txt`も参照

### PyInstaller

```shell
% pyinstaller src/timestamps.py --onefile
```
