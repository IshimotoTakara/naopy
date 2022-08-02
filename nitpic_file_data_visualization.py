import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re

from utils import plot_data, separate_with_commas, spline_interp


def nitpic_file_data_visualization(input_file_path, output_folder_path):
    """
    nitpicファイル読み込み
    """
    path = input_file_path  # nitpicファイル(入力ファイル)のPATH
    with open(path, mode='rt', encoding='utf-8') as f:
        read_data = f.readlines()
    print('\033[32m' + 'SUCCESS：READ ' + path + '\033[0m')

    """
    出力フォルダを作成する（nitpicファイル名-split_experimental_data）
    """
    # file_name = os.path.basename(path)  # 拡張子ありのファイル名
    file_name_head = os.path.splitext(os.path.basename(path))[0]  # 拡張子なしのファイル名
    os.makedirs(output_folder_path + file_name_head, exist_ok=True)
    output_folder_path_base = output_folder_path + file_name_head + "/"

    """
    nitpicファイルを整形する
    """
    # CSVファイル（出力ファイル）のPATH
    head_path = output_folder_path_base + file_name_head + "_nitpic_head.csv"  # nitpicファイル先頭の情報を格納するCSVファイル
    data_path = output_folder_path_base + file_name_head + "_nitpic_experimental_data.csv"  # nitpicファイルの実験データを格納するCSVファイル

    print('nitpicファイルをヘッダーと実験データに分割します.')
    # 先頭27行と29行目以降で分割する
    head = read_data[:27]  # 先頭27個の要素
    data = read_data[28:]  # 実験データ

    # 空白と改行文字を削除
    head = [s.replace(' ', '').replace('\n', '') for s in head]
    data = [s.replace(' ', '').replace('\n', '').replace('\t', ',') for s in data]


    # head_dataをCSVファイルに出力する
    np.savetxt(head_path, head, delimiter=",", fmt='%s')
    print('\033[32m' + 'SUCCESS：SAVE TO ' + head_path + '\033[0m')

    data_inject = data  # INJECTIONNUMBERを含む要素が残っているデータのコピー(滴定毎のデータに分割するときに使う)
    # 実験データの'INJECTIONNUMBER'を含む行以外を抽出(INJECTIONNUMBERを含む行を削除)
    data = [s for s in data if 'INJECTIONNUMBER' not in s]
    del data[-1]  # 最後の行（INJECTIONNUMBER〜）を削除
    
    data = separate_with_commas(data) # ','区切りの要素を','毎に分割する

    # 配列dataを辞書に整形
    time, electric_power = [], []
    for s in data:
        time.append(float(s[0]))
        electric_power.append(float(s[1]))

    dictionary = {'Time': time, 'ElectricPower': electric_power}

    # 整形した実験データをCSVファイルに出力する
    df_all = pd.DataFrame(dictionary)
    df_all.to_csv(data_path)
    print('\033[32m' + 'SUCCESS：SAVE TO ' + data_path + '\033[0m')


    # 'INJECTIONNUMBER'を含むdata_injectの要素を検索
    invj_in = [s for s in data_inject if 'INJECTIONNUMBER' in s]
    p = r'INJECTIONNUMBER(.*)'
    r = re.findall(p, invj_in[-1])    # 「INJECTIONNUMBER25」中のINJECTIONNUMBERの後ろの文字を抽出
    titration_count = int(r[0])  # 滴定回数(25)
    print('滴定回数：' + str(titration_count))

    peak_time, peak_power = [], []
    time, electric_energy = [], []  # 電力量の推移をプロットするときに使う

    # 滴定回数毎の実験データのピークを検索
    for i in range(titration_count-1):
        # INJECTIONNUMBER0~INJECTIONNUMBERtitration_countまでをINJECTIONNUMBERi毎に整形する
        # i == titration_countの時は次の'INJECTIONNUMBER'が無いから、'INJECTIONNUMBER'から最後までを格納する
        if i == titration_count:
            data = data_inject[data_inject.index(invj_in[i]):]
        else:
            data = data_inject[data_inject.index(invj_in[i]):data_inject.index(invj_in[i + 1])]

        del data[0]  # 最初の行（INJECTIONNUMBER〜）を削除
        data = separate_with_commas(data)  # ','区切りの要素を','毎に分割する

        # １滴定の実験データ（時間、電力）を格納する
        time_each, electric_power_each = [], []
        for s in data:
            time_each.append(float(s[0]))
            electric_power_each.append(float(s[1]))

        d_time = float(time_each[-1]) - float(time_each[0])  # １回の実験（滴定）の時間
        time.append(time_each[-1] / 60)  # １回の実験（滴定）の時間を配列に追加
        electric_energy.append(float(np.mean(electric_power_each)) * d_time)  # 電力の平均×時間を配列に追加

    """
    プロット
    """
    # ”GRAPH：電力の推移”のPATH
    electric_power_graph_path = output_folder_path_base + "nitpic_electric_power_graph.png"
    # ”GRAPH：電力量の推移”のPATH
    electric_energy_graph_path = output_folder_path_base + "nitpic_electric_energy_graph.png"

    print('電力の推移をプロット')
    # 電力の推移をプロット
    plot_data(fig_size=(8, 5),
					title="Electric Power",
					save_path=electric_power_graph_path,
					ylabel="μcal/sec", xlabel="Time[min]",
					data1=[df_all.Time / 60, df_all.ElectricPower],
					data2=0.04,
				    label1="electric power", label2="Base Line",
                    type2="axhline")
    print('\033[32m' + 'SUCCESS：SAVE TO ' + electric_power_graph_path + '\033[0m')

    print('電力量の推移をプロット')
    # 電力量の推移をプロット
    time_spline, electric_energy_spline = spline_interp(time, electric_energy)  # スプライン補間
    plot_data(fig_size=(8, 5),
					title="Molar Ratio(Glc/GBd)",
					save_path=electric_energy_graph_path,
					ylabel="kcal/mole of injection", xlabel="Time[min]",
					data1=[time, electric_energy],
					data2=[time_spline, electric_energy_spline],
				    label1="electric energy", label2="curve",
                    type1="scatter")
    print('\033[32m' + 'SUCCESS：SAVE TO ' + electric_energy_graph_path + '\033[0m')

