# Hellish Quartの対戦動画（NHK）のタイムスタンプを出力するツール

## 1. timestamp.exe

### 概要

Hellish Quartの対戦動画から、NHK非主流派Youtubeチャンネルの概要欄に記載するタイムスタンプを出力するツールです。

### 前提条件

#### 動画ファイル

- 動画の形式
  mp4、mkv など、OpenCVライブラリが対応している形式に対応。

- 動画の解像度
  アスペクト比 16:9 の動画に対応。

- フレームレート
  60fps、30fps など、視聴可能な範囲であれば使用可能です。

#### 動画の内容

- フラッグ数
  1〜7フラッグ先取に対応。8フラッグ以上は非対応（表示形式が異なるため）。

- 試合成立条件
  どちらかが最大フラッグ数に到達した場合を試合成立とみなし、タイムスタンプに出力します（例：5/5）。
  到達前にメニューに戻った場合などは試合としてカウントされません。

- リマッチ対応
  リマッチにも対応しています。

- オーバーレイ表示などの注意
  以下の画面情報を元に試合情報を検出します：
  -- キャラクター選択画面の顔画像左側の縦帯
  -- キャラクター名の表示（青・黄色の文字）
  -- 試合画面のフラッグ表示（画面上部左右）

  これらにオーバーレイや Parsec のアイコンなどが重なると、正しく検出できない場合があります。

- 編集された動画について
  試合前のキャラクター選択画面がカットされていると、キャラクター情報を正しく取得できない可能性があります。

### 使い方

1. timestamp.exe を起動
2. 対戦動画を選択
3. コンソールと進捗バーが表示される
4. 処理完了後、以下のファイルが同じフォルダに出力されます：

   - `（日付）_timestamps.txt`（タイムスタンプ）
   - `（日付）_statistics.txt`（統計情報）

※ 処理中に CANCEL した場合は何も出力されません。

### 注意事項

- matchtemplate フォルダ、および `name_l`、`name_r` フォルダ内の画像は削除しないでください。
- 新キャラクターの名前画像が不足している場合、その試合のキャラクター名は nomatch として出力されます。
  名前画像を追加後、再度ツールを実行するか、人間が目視で修正してください。

## 2. rename.exe

### 概要

timestamps.txt に記録されたプレイヤー名をリネームし、Youtube概要欄向けの文章を生成するツールです。

### 使い方

1. rename.exe を起動
2. timestamp.exe で生成したタイムスタンプファイルを選択
3. BOT から出力された result ファイルを選択
4. 以下のファイルが生成されます：

   - `timestamps_rename_en.txt`（英語）
   - `timestamps_rename_jp.txt`（日本語）

### 注意事項

- result ファイルにはプレイヤーの Discord アカウント名が記載されています。

- Discord アカウント名と Youtube 用プレイヤー名との対応表は `replace_info.txt` に記述します。

- Youtube 概要欄の文章は、対戦結果ファイルの日付から曜日を取得し、週例対戦会か道場かを自動判別します。

- 概要欄テンプレートは `youtube_comment.txt` に以下の順で記載されています：

  -- 英文（週例対戦会）
  -- 英文（道場）
  -- 日本語（週例対戦会）
  -- 日本語（道場）

以上
