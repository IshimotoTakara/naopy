'''
% 目的
ITCファイルのデータ可視化,既存ソフトウェアの出力と同じような動作をするコードを作る.

% 現状
✅ ITCファイルを読み込んで, データの前処理、可視化までは形にした.
✅ ファイルごとにoutput配下にフィルだを作成し、そこにCSVファイルや図を出力するように修正
✅ 図のタイトルなどに使われている日本語を英語に修正
✅ itc_file_data_visualization関数でsplit_experimental_dataのパスを返すように修正
   → singular_value_decomposition関数の引数用
✅ split_experimental_dataフォルダにあるCSVファイルのデータ（滴定ごとの電圧の変化）を
   特異値分解し、ピーク成分とノイズ成分を分ける.
✅ 特異値分解で抽出したピーク成分とノイズ成分をプロット.
----------New------------------------------------------------
✅ 210107C_ITC_experimental_data.csv(全実験データ)に最初から[sec],[μcal/sec]に変換して保存するように修正
   → 至る所に "/ 60" をしなくて良くなった🙆
✅ ステップ数で分解していたピーク部分と時間との対応づけ（x軸がステップ数のままだと積分値が電力量にならない）
✅ 滴定ごとのピーク成分とノイズ成分の積分値の差をプロットできるようにした(/output/210107C/diff_peak_noise.png)
✅ 実験データが少ない場合、特異値分解ができず、積分結果を出せない（欠損値が存在する）ことがあるので、
   プロットの際にスプライン補完などを使って、欠損値に対する処理を行うようにした。
⬜️ 始点を０からにする？？→これ以上時間取れそうにない🙏 ← 多分そんなに難しくない
⚠️ scipy.integrateで積分のところ実装してて、もしかしたらscipyのインストールorアップデートがいるかも。
自分がコーディングをする際にメモしたこと（メモ帳.pdf）も共有しておきます

% ディレクトリの説明
this_project/data: 入力用のITCファイルを保存しておく
this_project/output/ITCファイル名: このコードで出力されるファイルが格納される
this_project/output/ITCファイル名/split_experimental_data: ITCファイルのうちの分割した実験データの出力に使う
this_project/output/ITCファイル名/singular_value_decomposition: 特異値分解の結果の出力に使う
今回はthis_project = naopyで作業を行なわせていただいております.

% コードの要修正箇所
不要なところは適宜コメントアウトして使ってね

% 参考
https://qiita.com/makotoito/items/1bb062e4264394e1c2da（異常検知（４）時系列信号の変化の検知、特異スペクトル変換法など）

%動作環境
MacOS Big Monterey
Python 3.7.6

% 実行方法
$ python3 main.py
'''
import os

# ITC_file_data_visualization.pyのitc_file_data_visualization関数をitsとしてimport
from ITC_file_data_visualization import itc_file_data_visualization as itc
# nitpic_file_data_visualization.pyのnitpic_file_data_visualization関数をnitpicとしてimport
from nitpic_file_data_visualization import nitpic_file_data_visualization as nitpic
# singular_value_decomposition.pyのsingular_value_decomposition関数をsvdとしてimport
from singular_value_decomposition import singular_value_decomposition as svd

"""
main関数
"""
def main():
    input_file_path_itc = "data/210107C.ITC"
    # input_file_path_nitpic = "data/200203C.nitpic"　# 210107C.nitpicもあるのか？

    os.makedirs("output", exist_ok=True)

    '''
    itc_file_data_visualization(分析対象のITCファイルのPATH（入力ファイル）, output_folder_path)
    第1引数: input_file_path_itc → 分析対象のITCファイルのパス
    第2引数: output_folder_path → 出力フォルダのパス（"/output"）
    '''
    print('\033[34m' + 'RUN：itc_file_data_visualization' + '\033[0m')
    input_file_path_svd, all_data_path, titration_count = itc(input_file_path_itc, "output/")
    print('\033[34m' + 'Task of itc_file_data_visualization completed!!!')

    '''
    singular_value_decomposition(input_file_path_itc, input_file_path_svd, all_data_path, output_folder_path, M, V_index)
    第1引数: input_file_path_itc → 分析対象のITCファイルのパス
    第2引数: input_folder_path → itc_file_data_visualization関数からの返り値でsplit_experimental_data/フォルダのパス
    第3引数: all_data_path → itc_file_data_visualization関数で作成したすべての実験データが保存されているCSVファイルのパス
    第4引数: output_folder_path → 出力フォルダのパス（"/output"）
    第5引数: M → スライド窓のステップ数M
    第6引数: V_index → 要素波形のどこまでをピーク成分とするか
    '''
    print('\033[34m' + 'RUN：singular_value_decomposition' + '\033[0m')
    svd(input_file_path_itc, input_file_path_svd, all_data_path, titration_count, "output/", 50,4)
    print('\033[34m' + 'Task of singular_value_decomposition completed!!!')

    '''
    nitpic_file_data_visualization(input_file_path_nitpic, output_folder_path)
    第1引数: input_file_path_nitpic, → 分析対象のnitpicファイルのパス
    第2引数: output_folder_path → 出力フォルダのパス（"/output"）
    '''
    # print('\033[34m' + 'RUN：nitpic_file_data_visualization' + '\033[0m')
    # nitpic(input_file_path_nitpic, "output/")
    # print('\033[34m' + 'Task of nitpic_file_data_visualization completed!!!' + '\033[0m')

if __name__ == '__main__':
    print('\033[33m' + 'RUN：main' + '\033[0m')
    main()
    print('\033[33m' + 'All tasks completed!!!' + '\033[0m')
