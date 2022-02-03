"""
関数
"""
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import csv
import matplotlib.pyplot as plt
from scipy import integrate
import os


# 配列の','区切りの要素を','毎に分割する関数
def separate_with_commas(param):
    l = []
    [l.append(s.split(',')) for s in param]

    return l

# ３次元配列["time0,ep0,temp0", "time1,ep1,temp1","",,,,]を辞書に変換する関数
# option="d" → dictionaryのみを返す
# option="tedd" → time, electric_power, degree, dictionaryを返す
def make_dictionary(data, option):
    time, electric_power, degree = [], [], []
    for s in data:
        time.append(float(s[0]) / 60) # 単位を[sec]に変換
        electric_power.append(float(s[1]) / 60) # 単位を[μcal/sec]に変換
        degree.append(float(s[2]))

    dictionary = {'Time': time, 'ElectricPower': electric_power, 'Degree': degree}

    if option == "d":
        return dictionary
    elif option == "tedd":
        return time, electric_power, degree, dictionary

# スプライン曲線を作成する関数(離散データを折れ線グラフにしたときに滑らかになる)
def spline_interp(in_x, in_y):
    out_x = np.linspace(np.min(in_x), np.max(in_x), np.size(in_x)*100)  # もとのxの個数より多いxを用意
    func_spline = interp1d(in_x, in_y, kind='cubic')  # cubicは3次のスプライン曲線
    out_y = func_spline(out_x)  # func_splineはscipyオリジナルの型

    return out_x, out_y

# 欠損値に対するスプライン補完をする関数
def spline_interp_missing_value(in_x, in_y):
    df = pd.Series(in_y,index=in_x) 
    df = df.replace(["None"], np.nan) # NoneをNan（欠損値の変換）
    df = df.interpolate('spline', order=2) # 欠損値をスプライン補完
    df = df.dropna(how='all') # 欠損値の行を削除

    return df.index.tolist(), df.values.tolist()
    

# singular_value_decomposition.pyのメインで使用する
# 与えられた引数を境に分けたピーク成分とノイズ成分再現して、プロットする関数
def separate_noise_from_peak(input_file_path, output_folder_path_base, M, V_index):
  E_power = [] # 電力の時系列データを格納すリスト
  time = [] # 時間を格納するリスト
  X = [] # 部分時系列を格納するリスト
  peak_component, noise_component = 0, 0 # 初期化

  '''
  csvファイルから電力のみを取り出す処理
  '''
  firstLoop = True # ファーストループ確認フラグ
  with open(input_file_path, encoding='utf8', newline='') as f:
      csvreader = csv.reader(f)
      for row in csvreader:
          if firstLoop: # １行目のカラム名はいらないからスキップ
              firstLoop = False # フラグを下ろす
          else:
              # ※CSVファイルはString型で保存されてるので、float型にしてあげて格納するよ
              E_power.append(float(row[2])) # 3列目,つまり電力をリストE_powerに入れていく
              time.append(float(row[1])) # 2列目,つまり時間をリストtimeに入れていく
  
  V_size = len(E_power)-M # 要素波形の数
  # print(V_size)

  # 時系列データSがスライド窓のステップ数Mより少ないとnp.linalg.svd()でエラー
  if V_size > 0:
    """
    M次元部分時系列データを作る処理
    """
    for i in range(V_size): # 「'時系列データの数' - 'スライド窓の長さM'」回繰り返す
      x = []
      for j in range(M): # スライド窓の長さM分繰り返す
        x.append(E_power[i+j]) # i番目のxはs[i]からs[i+M-1]までを格納したリスト
      X.append(x)
    
    """
    ピーク成分とノイズ成分の再現
    """
    U, s, V = np.linalg.svd(X, full_matrices=True) # 特異値分解
    # print('U: ' + str(np.shape(U)) + ", s: " + str(np.shape(s)) + ",V: " + str(np.shape(V))) # 特異値分解の成分確認用

    # ピーク成分の再現
    for i in range(V_index): # 0 〜 (V_index-1)までをピーク成分として合成（再現）
      peak_component += U[i][i]*s[i]*V[i]

    # ノイズ成分の再現
    if V_size > M: # 通常の処理
      for i in range(V_index, M): # V_index 〜 (M-1)までをノイズ成分として合成（再現）
        noise_component += U[i][i]*s[i]*V[i]
      
    else: # 要素波形の数がMに満たないときの処理 
      for i in range(V_index, V_size): # V_index 〜 (V_size-1)までをノイズ成分として合成（再現）
        noise_component += U[i][i]*s[i]*V[i]
    
    # peak_component, noise_componentをCSVファイルに保存 
    csv_file_peak = output_folder_path_base + "/peak.csv"
    np.savetxt(csv_file_peak, peak_component, delimiter=",", fmt='%12.8f') # 浮動小数点数値
    csv_file_noise = output_folder_path_base + "/noise.csv"
    np.savetxt(csv_file_noise, noise_component, delimiter=",", fmt='%12.8f') # 浮動小数点数値
    csv_file_time = output_folder_path_base + "/time.csv"
    np.savetxt(csv_file_time, time, delimiter=",", fmt='%12.8f') # 浮動小数点数値

      
    # U, s, VをCSVファイルに保存
    csv_file_U = output_folder_path_base + "/svd_U.csv"
    np.savetxt(csv_file_U, U, delimiter=",", fmt='%12.8f') # 浮動小数点数値
    csv_file_s = output_folder_path_base + "/svd_s.csv"
    np.savetxt(csv_file_s, s, delimiter=",", fmt='%12.8f') # 浮動小数点数値
    csv_file_V = output_folder_path_base + "/svd_V.csv"
    np.savetxt(csv_file_V, V, delimiter=",", fmt='%12.8f') # 浮動小数点数値

    """
    プロット
    """
    x = np.linspace(time[0], time[-1], M) # x軸を時間に変換
    # ピーク成分をプロット
    peak_graph_path = output_folder_path_base + "peak.png"
    plt.figure(figsize=(8, 5))  # Figureを設定
    plt.title("Peak Component (M = " + str(M) + ", V_index: 0~" +str(V_index-1) + ")", fontsize=18)  # タイトルを追加
    plt.ylabel("Electric Power μcal/sec", size="large")  # y軸ラベルを追加
    plt.xlabel("Time[sec]", size="large")  # x軸ラベルを追加
    plt.minorticks_on()  # 補助目盛りを追加
    plt.grid(which="major", color="black", alpha=0.5)  # 目盛り線の表示
    plt.grid(which="minor", color="gray", linestyle=":")  # 目盛り線の表示
    plt.plot(x, peak_component, color='black')  # データをプロット
    plt.savefig(peak_graph_path)  # グラフを保存
    plt.close(peak_graph_path)
    print('\033[32m' + 'SUCCESS：SAVE TO ' + peak_graph_path + '\033[0m')

    # ノイズ成分をプロット
    noise_graph_path = output_folder_path_base + "noise.png"
    if V_size > M: # 通常の処理
        plt.figure(figsize=(8, 5))  # Figureを設定
        plt.title("Noise Component (M = " + str(M) + ", V_index: " + str(V_index) + "~" + str(M) + ")", fontsize=18)  # タイトルを追加
        plt.ylabel("Electric Power μcal/sec", size="large")  # y軸ラベルを追加
        plt.xlabel("Time[sec]", size="large")  # x軸ラベルを追加
        plt.minorticks_on()  # 補助目盛りを追加
        plt.grid(which="major", color="black", alpha=0.5)  # 目盛り線の表示
        plt.grid(which="minor", color="gray", linestyle=":")  # 目盛り線の表示
        plt.plot(x, noise_component, color='black')  # データをプロット
        plt.savefig(noise_graph_path)  # グラフを保存
        plt.close(noise_graph_path)
        print('\033[32m' + 'SUCCESS：SAVE TO ' + noise_graph_path + '\033[0m')
      
    else: # 要素波形の数がMに満たないときの処理 
        plt.figure(figsize=(8, 5))  # Figureを設定
        plt.title("Noise Component (M = " + str(M) + ", V_index: " + str(V_index) + "~" + str(V_size) + ")", fontsize=18)  # タイトルを追加
        plt.ylabel("Electric Power μcal/sec", size="large")  # y軸ラベルを追加
        plt.xlabel("Time[sec]", size="large")  # x軸ラベルを追加
        plt.minorticks_on()  # 補助目盛りを追加
        plt.grid(which="major", color="black", alpha=0.5)  # 目盛り線の表示
        plt.grid(which="minor", color="gray", linestyle=":")  # 目盛り線の表示
        plt.plot(x, noise_component, color='black')  # データをプロット
        plt.savefig(noise_graph_path)  # グラフを保存
        plt.close(noise_graph_path)
        print('\033[32m' + 'SUCCESS：SAVE TO ' + noise_graph_path + '\033[0m')

  # 時系列データSがスライド窓のステップ数Mより少なかったら返り値0,0
  else:
    print('\033[31m' + '時系列データSがスライド窓のステップ数Mより少ないので、' + input_file_path + 'では部分時系列データXが作れません' + '\033[0m')

# ピーク成分とノイズ成分の積分値の差を計算する関数
def plot_difference_peak_noise(svd_path, output_folder_path, titration_count):
    
    difference_peak_noise = []
    for i in range(titration_count):
        csv_file_peak = svd_path + "/210107C_" + str(i) + "/peak.csv"
        csv_file_noise = svd_path + "/210107C_" + str(i) + "/noise.csv"
        csv_file_time = svd_path + "/210107C_" + str(i) + "/time.csv"

        # フォルダにcsv_file_peak,noise,timeの全部があったら計算
        if os.path.isfile(csv_file_peak) & os.path.isfile(csv_file_peak) & os.path.isfile(csv_file_time):
            peak_component, noise_component, time = [], [], []
            # peak_component読み込み
            with open(csv_file_peak, encoding='utf8', newline='') as f:
                csvreader = csv.reader(f)
                for row in csvreader:
                    # ※CSVファイルはString型で保存されてるので、float型にしてあげて格納するよ
                    peak_component.append(float(row[0])) # 1行ずつリストpeak_componentに入れていく
            
            # noise_component読み込み
            with open(csv_file_noise, encoding='utf8', newline='') as f:
                csvreader = csv.reader(f)
                for row in csvreader:
                    # ※CSVファイルはString型で保存されてるので、float型にしてあげて格納するよ
                    noise_component.append(float(row[0])) # 1行ずつリストpeak_componentに入れていく
            # time読み込み
            with open(csv_file_time, encoding='utf8', newline='') as f:
                csvreader = csv.reader(f)
                for row in csvreader:
                    # ※CSVファイルはString型で保存されてるので、float型にしてあげて格納するよ
                    time.append(float(row[0])) # 1行ずつリストpeak_componentに入れていく

            V_size = len(peak_component) # 要素波形の数（ピーク成分、またはノイズ成分の行列の長さに相当）
            time_start, time_end = time[0], time[-1] # 時間の最初と最後を格納
            x = np.linspace(time[0], time[-1], V_size) # x軸を時間に変換
            '''
            積分計算
            '''
            # 参考：https://org-technology.com/posts/integrate-function-fixed-sample.html
            peak_component_integral = integrate.simps(peak_component, x) # ピーク成分の積分値（シンプソン法）
            noise_component_integral = integrate.simps(noise_component, x) # ノイズ成分の積分値（他にも台形法、Romberg法などが使える）
            difference_peak_noise.append(peak_component_integral - noise_component_integral) # ピーク成分とノイズ成分の積分値の差

        # フォルダにcsv_file_peakとcsv_file_noiseのどちらか、または両方なかったらNone(欠損地) ← 後でスプライン補完（最初からdf使っとけばよかったと公後悔w）
        else:
            difference_peak_noise.append(None)

        print(str(i) + "回目の滴定のピーク成分とノイズ成分の積分値の差は" + str(difference_peak_noise[i]) + "です")

    '''
    ピーク成分とノイズ成分の積分値の差分（何を意味する？電力量の差分？）をプロット
    '''
    x_diff = np.array(range(0, titration_count)) # [0~(titration_count-1)]
    differenc_peak_noise_graph_path = output_folder_path + "diff_peak_noise.png"
    plt.figure(figsize=(8, 5))  # Figureを設定
    plt.title('Difference in integral value', fontsize=18)  # タイトルを追加
    plt.ylabel("integral value(= Electric energy?)", size="large")  # y軸ラベルを追加
    plt.xlabel("Number of titrations = " + str(titration_count), size="large")  # x軸ラベルを追加
    plt.minorticks_on()  # 補助目盛りを追加
    plt.grid(which="major", color="black", alpha=0.5)  # 目盛り線の表示
    plt.grid(which="minor", color="gray", linestyle=":")  # 目盛り線の表示
    plt.scatter(x_diff, difference_peak_noise, color='black')  # データをプロット
    x_diff, difference_peak_noise = spline_interp_missing_value(x_diff, difference_peak_noise) # 欠損値のスプライン補完
    x_diff, difference_peak_noise = spline_interp(x_diff, difference_peak_noise) # スプライン曲線に変換
    plt.plot(x_diff, difference_peak_noise, color='red')  # データをプロット
    plt.savefig(differenc_peak_noise_graph_path)  # グラフを保存
    plt.close(differenc_peak_noise_graph_path)
    print('\033[32m' + 'SUCCESS：SAVE TO ' + differenc_peak_noise_graph_path + '\033[0m')
