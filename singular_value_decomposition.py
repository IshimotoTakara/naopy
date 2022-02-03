import os
import glob
import csv
from unittest import skip
import numpy as np
import matplotlib.pyplot as plt
# func.pyからimport
from func import separate_noise_from_peak, plot_difference_peak_noise

# input_folder_path内のCSVファイルに特異値分解を施し、その結果をプロットする
# また、ピーク成分とノイズ成分の積分値の差もプロットする
def singular_value_decomposition(input_file_path_itc, input_folder_path, all_data_path, titration_count, output_folder_path, M, V_index):
  file_name_head_itc = os.path.splitext(os.path.basename(input_file_path_itc))[0]  # 拡張子なしのファイル名
  svd_path = output_folder_path + file_name_head_itc + "/singular_value_decomposition"
  output_svd_path = output_folder_path + file_name_head_itc + "/"
  os.makedirs(svd_path, exist_ok=True)

  """
  input_folder_path内のCSVファイル名を全てcsv_fileに格納
  """
  csv_files = glob.glob(input_folder_path + "*.csv")


  """
  滴定ごとのデータに特異値分解を実行
  """
  print('滴定ごとのデータに対するピーク成分とノイズ成分をプロット')
  for file in csv_files:
    # 出力パスを作成する
    file_name_head_csv = os.path.splitext(os.path.basename(file))[0]  # 拡張子なしのファイル名
    output_folder_path_base = output_folder_path + file_name_head_itc + "/singular_value_decomposition/" + file_name_head_csv + "/"
    os.makedirs(output_folder_path + file_name_head_itc + "/singular_value_decomposition/" + file_name_head_csv, exist_ok=True)

    # 与えられた引数を境に分けたピーク成分とノイズ成分再現して、プロット
    separate_noise_from_peak(file, output_folder_path_base, M, V_index)


  """
  ピーク成分とノイズ成分の積分値の差をプロット
  """ 
  print('ピーク成分とノイズ成分の積分値の差をプロット')
  plot_difference_peak_noise(svd_path, output_svd_path, titration_count)

     
  """
  全てのデータに特異値分解を実行(おまけ)
  """ 
  # 出力パスを作成する
  file_name_head_csv = os.path.splitext(os.path.basename(all_data_path))[0]  # 拡張子なしのファイル名
  output_folder_path_base = output_folder_path + file_name_head_itc + "/singular_value_decomposition/" + file_name_head_csv + "/"
  os.makedirs(output_folder_path + file_name_head_itc + "/singular_value_decomposition/" + file_name_head_csv, exist_ok=True)

  print('全データに対するピーク成分とノイズ成分をプロット')
  # 与えられた引数を境に分けたピーク成分とノイズ成分再現して、プロット
  separate_noise_from_peak(all_data_path, output_folder_path_base, M, V_index)


