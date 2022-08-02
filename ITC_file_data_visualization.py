import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re

from utils import make_dictionary, plot_data
from utils import separate_with_commas, spline_interp

def itc_file_data_visualization(input_file_path, output_folder_path):
    """
    ITCファイル読み込み
    """
    with open(input_file_path, mode='rt', encoding='utf-8') as f:
        read_data = f.readlines()
    print('\033[32m' + 'SUCCESS：READ ' + input_file_path + '\033[0m')

    """
    出力フォルダを作成する（ITCファイル名 - split_experimental_data）
    """
    # file_name = os.path.basename(input_file_path)  # 拡張子ありのファイル名
    file_name_head = os.path.splitext(os.path.basename(input_file_path))[0]  # 拡張子なしのファイル名
    os.makedirs(output_folder_path + file_name_head, exist_ok=True)
    output_folder_path_base = output_folder_path + file_name_head + "/"

    """
    ITCファイルを整形する
    """
    # CSVファイル（出力ファイル）のPATH
    head_path = output_folder_path_base + file_name_head + "_ITC_head.csv"  # ITCファイル先頭の情報を格納するCSVファイル
    experimental_data_path = output_folder_path_base + file_name_head + "_ITC_experimental_data.csv"  # ITCファイルの実験データを格納するCSVファイル

    print('ITCファイルをヘッダーと実験データに分割します.')
    # 先頭３１行とそれ以外で分割する
    head = read_data[:31]  # 先頭31個の要素
    data = read_data[31:]  # 実験データ

    # 空白と改行文字を削除
    head = [s.replace(' ', '').replace('\n', '') for s in head]
    data = [s.replace(' ', '').replace('\n', '') for s in data]

    # head_dataをCSVファイルに出力する
    np.savetxt(head_path, head, delimiter=",", fmt='%s')
    print('\033[32m' + 'SUCCESS：SAVE TO ' + head_path + '\033[0m')

    data_at = data  # @を含む要素が残っているデータのコピー(滴定毎のデータに分割するときに使う)
    # 実験データの'@'を含む行以外を抽出(@を含む行を削除)
    data = [s for s in data if '@' not in s]
    # ','区切りの要素を','毎に分割する
    data = separate_with_commas(data)
    # 配列dataを辞書に整形
    _, _, _, dictionary = make_dictionary(data)
    # 整形した実験データをCSVファイルに出力する
    df_all = pd.DataFrame(dictionary)
    df_all.to_csv(experimental_data_path)
    print('\033[32m' + 'SUCCESS：SAVE TO ' + experimental_data_path + '\033[0m')

    """
    実験データを滴定回数毎に分割する
    """
    print('実験データを滴定回数毎に分割します.')
    # '@'を含むdata_atの要素を検索
    at_in = [s for s in data_at if '@' in s]
    p = r'\@(.*)\,'
    r = re.findall(p, at_in[-1])  # 「@25,4.008375」中の”@”と”,”に囲まれている文字を抽出
    titration_count = int(r[0])  # 滴定回数(25)
    print('滴定回数：' + str(titration_count))

    # CSVファイル（出力ファイル）のPATH名のベース
    split_experimental_data_path = output_folder_path_base + "split_experimental_data/"
    os.makedirs(split_experimental_data_path, exist_ok=True)

    path_base = split_experimental_data_path + file_name_head
    time, electric_energy = [], []  # 電力量の推移をプロットするときに使う

    # 滴定回数毎の実験データをCSVファイルに出力,同時にプロット
    for i in range(titration_count + 1):
        csv_path = path_base + f"_{i}.csv"  # PATH名を定義

        # @0~@titration_countまでを@i毎に整形する
        # i == titration_countの時は次の'@'が無いから、'@'から最後までを格納する
        if i == titration_count:
            data = data_at[data_at.index(at_in[i]):]
        else:
            data = data_at[data_at.index(at_in[i]):data_at.index(at_in[i + 1])]

        del data[0]  # 最初の行（@〜）を削除
        data = separate_with_commas(data)  # ','区切りの要素を','毎に分割する
        time_each, electric_power_each, degree_each, dictionary = make_dictionary(data)  # 配列dataを辞書に整形
        df = pd.DataFrame(dictionary)
        df.to_csv(csv_path)
        print('\033[32m' + 'SUCCESS：SAVE TO ' + csv_path + '\033[0m')

        """
        プロット(滴定毎の実験データ)
        """
        each_epower_graph_path = path_base + f"_graph{i}.png"  # グラフ保存用のPATH

        plot_data(fig_size=(8, 5),
					title=f"Electric Power of Transition{i}",
					save_path=each_epower_graph_path,
					ylabel="μcal/sec", xlabel="Time[min]",
					data1=[df.Time, df.ElectricPower],
				    label1="electric power")
        print('\033[32m' + 'SUCCESS：SAVE TO ' + each_epower_graph_path + '\033[0m')

        d_time = float(time_each[-1]) - float(time_each[0])  # １回の実験（滴定）の時間
        time.append(time_each[-1])  # １回の実験（滴定）の時間を配列に追加
        electric_energy.append(float(np.mean(electric_power_each)) * d_time)  # 電力の平均を配列に追加

    """
    プロット(全ての実験データ)
    """
    # ”GRAPH：電力の推移”のPATH
    electric_power_graph_path = output_folder_path_base + "ITC_electric_power_graph.png"
    # ”GRAPH：電力量の推移”のPATH
    electric_energy_graph_path = output_folder_path_base + "ITC_electric_energy_graph.png"

    print('電力の推移をプロット')
    # 電力の推移をプロット
    plot_data(fig_size=(8, 5),
					title="Electric Power",
					save_path=electric_power_graph_path,
					ylabel="μcal/sec", xlabel="Time[min]",
					data1=[df_all.Time, df_all.ElectricPower],
				    label1="electric power")
    print('\033[32m' + 'SUCCESS：SAVE TO ' + electric_power_graph_path + '\033[0m')

    print('電力量の推移をプロット')
    # 電力量の推移をプロット
    time_spline, electric_energy_spline = spline_interp(time, electric_energy)  # スプライン曲線に変換
    plot_data(fig_size=(8, 5),
                title="Molar Ratio(Glc/GBd)",
                save_path=electric_energy_graph_path,
                ylabel="kcal/mole of injection", xlabel="Time[min]",
                data1=[time, electric_energy],
                data2=[time_spline, electric_energy_spline],
                label1="electric energy",
                label2="curve",
                type1="scatter")
    print('\033[32m' + 'SUCCESS：SAVE TO ' + electric_energy_graph_path + '\033[0m')

    return experimental_data_path, titration_count