# naopy


# 目的
ITCファイルのデータ可視化,既存ソフトウェアの出力と同じような動作をするコードを作る.

# 現状

✅ ITCファイルを読み込んで, データの前処理、可視化までは形にした.

✅ ファイルごとにoutput配下にフィルだを作成し、そこにCSVファイルや図を出力するように修正.

✅ 図のタイトルなどに使われている日本語を英語に修正.

✅ itc_file_data_visualization関数でsplit_experimental_dataのパスを返すように修正.

   → singular_value_decomposition関数の引数用
   
✅ split_experimental_dataフォルダにあるCSVファイルのデータ（滴定ごとの電圧の変化）を特異値分解し、ピーク成分とノイズ成分を分ける.

✅ 特異値分解で抽出したピーク成分とノイズ成分をプロット.

----------New------------------------------------------------

✅ 210107C_ITC_experimental_data.csv(全実験データ)に最初から[sec],[μcal/sec]に変換して保存するように修正.
   
   → 至る所に "/ 60" をしなくて良くなった🙆
   
✅ ステップ数で分解していたピーク部分と時間との対応づけ（x軸がステップ数のままだと積分値が電力量にならない）.

✅ 滴定ごとのピーク成分とノイズ成分の積分値の差をプロットできるようにした(/output/210107C/diff_peak_noise.png).

✅ 実験データが少ない場合、特異値分解ができず、積分結果を出せない（欠損値が存在する）ことがあるので,プロットの際にスプライン補完などを使って,欠損値に対する処理を行うようにした.

⚠️ scipy.integrateで積分のところ実装してて、もしかしたらscipyのインストールorアップデートがいるかも.

自分がコーディングをする際にメモしたこと（メモ帳.pdf）も共有しておきます.

# ディレクトリの説明
this_project/data: 入力用のITCファイルを保存しておく

this_project/output/ITCファイル名: このコードで出力されるファイルが格納される

this_project/output/ITCファイル名/split_experimental_data: ITCファイルのうちの分割した実験データの出力に使う

this_project/output/ITCファイル名/singular_value_decomposition: 特異値分解の結果の出力に使う

今回はthis_project = naopyで作業を行なわせていただいております.

# 参考
[異常検知（４）時系列信号の変化の検知、特異スペクトル変換法など](https://qiita.com/makotoito/items/1bb062e4264394e1c2da)

[Scipy 数値積分](https://python.atelierkobato.com/scipy_integrate/)
# 動作環境
MacOS Big Monterey

Python 3.7.6

numpy                     1.19.5  

pandas                    1.0.1     

scipy                     1.4.1  

# 実行方法
```
$ python3 main.py
```

不要なところは適宜コメントアウトして使ってね
