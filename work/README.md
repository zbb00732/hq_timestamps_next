# Hellish Quartの対戦動画（NHK）のタイムスタンプを出力するツール類

## 概要

### 1. timestamp.exe
Hellish Quartの対戦動画から、NHK非主流派Youtubeチャンネルの概要欄に記載するタイムスタンプを出力するツールです。

### 2. rename.exe
timestamps.txt に記録されたプレイヤー名をリネームし、Youtube概要欄用のテキストを出力するツールです。

## 使い方
1. HQ_NHK_BOT で対戦結果ファイル `yyyymmdd_n_result.txt` を出力する
2. timestamp.exe で対戦動画からタイムスタンプ `yyyymmddtimestamps.txt` を出力する
3. rename.exe で上記2つのファイルからYoutube概要欄用のテキストを出力する
- `yyyymmdd_youtube_description_en.txt`
- `yyyymmdd_youtube_description_jp.txt`

それぞれのツールの使い方は、各フォルダの HOWTOUSE.md を参照してください。

以上
