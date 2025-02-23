# 表情解析くん

画像(jpg,png)から表情を解析し、その表情の説明と言いそうなセリフを自動生成する。
表情に名前をつけないといけない時用。  


## 簡単な使い方

①環境変数 GOOGLE_API_KEYにGoogle Gemini APIのキーを設定  
②requirements.txtをインストール
②run.batを実行
③画像(複数可)をドラッグアンドドロップ  
④解析実行押す  
⑤📁開くとcsv入ってる


## 機能

- 画像ファイル（JPG/JPEG）の選択（ダイアログまたはドラッグ＆ドロップ）
- 複数画像の一括解析
- 解析結果のCSV出力
- 過去の解析結果の履歴表示

## セットアップ

1. Python 3.8以上をインストール・仮想環境作りたかったら作る

3. 必要なライブラリのインストール:
   ```bash
   pip install -r requirements.txt
   ```

4. 環境変数の設定:
   - `GOOGLE_API_KEY`にGoogle Gemini APIのキーを設定
   ```bash
   # Windows:
   set GOOGLE_API_KEY=your-api-key
   # Linux/Mac:
   export GOOGLE_API_KEY=your-api-key
   ```

## 使用方法

1. アプリケーションの起動:
   ```bash
   python src/main.py
   ```

2. 画像の選択:
   - 「ファイル選択」ボタンをクリックして画像を選択
   - または画像ファイルをウィンドウにドラッグ＆ドロップ

3. 解析の実行:
   - 「解析実行」ボタンをクリックして処理を開始
   - 処理中は進捗状況が表示されます

4. 結果の確認:
   - 解析結果は画面上に表示されます
   - CSVファイルが`output`フォルダに保存されます
   - 過去の解析結果は履歴エリアで確認できます

## エラー対応

- エラーが発生した場合は、該当画像のエラー内容が表示されます
- デバッグ情報はコンソールに出力されます

## ディレクトリ構造

```
project_root/
├── src/
│   ├── main.py
│   ├── gui.py
│   ├── image_processing.py
│   ├── gemini_api.py
│   └── history_manager.py
├── output/
├── README.md
└── requirements.txt

## exeつくるとき  

pyinstaller main.spec