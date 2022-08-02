import csv
import glob
import numpy as np
import os
from scipy import integrate

from utils import plot_data, spline_interp, spline_interp_missing_value

# input_folder_path内のCSVファイルに特異値分解を施し、その結果をプロットする
# また、ピーク成分とノイズ成分の積分値の差もプロットする
def singular_value_decomposition(input_file_path_itc, all_data_path, titration_count, output_folder_path, M, V_index):
	file_name_head_itc = os.path.splitext(os.path.basename(input_file_path_itc))[0]  # 拡張子なしのファイル名
	output_folder_path_base = output_folder_path + file_name_head_itc + "/"
	svd_path = output_folder_path_base + "singular_value_decomposition/" # 出力フォルダのパス
	os.makedirs(svd_path, exist_ok=True)
	svd_split_path_base = svd_path + file_name_head_itc

	experimental_data = output_folder_path_base + "split_experimental_data/" # 滴定ごとに分割された実験データの格納フォルダのパス

	"""
	experimental_data内のCSVファイル名を全てcsv_filesに格納
	"""
	csv_files = glob.glob(experimental_data + "*.csv")

	"""
	滴定ごとのデータに特異値分解を実行
	"""
	print('滴定ごとのデータに対するピーク成分とノイズ成分をプロット')
	for file in csv_files:
		# 出力パスを作成する
		file_name_head_csv = os.path.splitext(os.path.basename(file))[0]  # 拡張子なしのファイル名
		output_peak_noise_path = svd_path + file_name_head_csv + "/"
		os.makedirs(svd_path + file_name_head_csv, exist_ok=True)

		# 与えられた引数を境に分けたピーク成分とノイズ成分再現して、プロット
		separate_noise_from_peak(file, output_peak_noise_path, M, V_index)

	"""
	ピーク成分とノイズ成分の積分値の差をプロット
	""" 
	print('ピーク成分とノイズ成分の積分値の差をプロット')
	plot_difference_peak_noise(svd_split_path_base, output_folder_path_base, titration_count)
		
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


# 与えられた引数を境に分けたピーク成分とノイズ成分再現して、プロットする関数
def separate_noise_from_peak(input_file_path, output_folder_path, M, V_index):
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
				E_power.append(float(row[2])) # 3列目,つまり電力をリストE_powerに入れていく
				time.append(float(row[1])) # 2列目,つまり時間をリストtimeに入れていく
	
	V_size = len(E_power) - M # 要素波形の数

	# 時系列データSがスライド窓のステップ数Mより少ないとnp.linalg.svd()でエラー
	if V_size < 0:
		# 時系列データSがスライド窓のステップ数Mより少なかったら何もしない
		print('\033[31m' + '時系列データSがスライド窓のステップ数Mより少ないので、' + input_file_path + 'では部分時系列データXが作れません' + '\033[0m')
		
	else:
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
		roop_num = M if V_size > M else V_size # V_size > M: 通常の処理, V_size <= M要素波形の数がMに満たないときの処理 
		for i in range(V_index, roop_num): # V_index 〜 (roop_num-1)までをノイズ成分として合成（再現）
			noise_component += U[i][i]*s[i]*V[i]
		
		# peak_component, noise_component, timeをCSVファイルに保存 
		csv_file_peak = output_folder_path + "/peak.csv"
		np.savetxt(csv_file_peak, peak_component, delimiter=",", fmt='%12.8f') # 浮動小数点数値
		csv_file_noise = output_folder_path + "/noise.csv"
		np.savetxt(csv_file_noise, noise_component, delimiter=",", fmt='%12.8f') # 浮動小数点数値
		csv_file_time = output_folder_path + "/time.csv"
		np.savetxt(csv_file_time, time, delimiter=",", fmt='%12.8f') # 浮動小数点数値
		
		# U, s, VをCSVファイルに保存
		csv_file_U = output_folder_path + "/svd_U.csv"
		np.savetxt(csv_file_U, U, delimiter=",", fmt='%12.8f') # 浮動小数点数値
		csv_file_s = output_folder_path + "/svd_s.csv"
		np.savetxt(csv_file_s, s, delimiter=",", fmt='%12.8f') # 浮動小数点数値
		csv_file_V = output_folder_path + "/svd_V.csv"
		np.savetxt(csv_file_V, V, delimiter=",", fmt='%12.8f') # 浮動小数点数値

		"""
		プロット
		"""
		x = np.linspace(time[0], time[-1], M) # x軸を時間に変換
		# ピーク成分をプロット
		peak_graph_path = output_folder_path + "peak.png"
		plot_data(fig_size=(8, 5),
					title="Peak Component (M = " + str(M) + ", V_index: 0~" +str(V_index-1) + ")",
					save_path=peak_graph_path,
					ylabel="Electric Power μcal/sec", xlabel="Time[min]",
					data1=[x, peak_component],
					label1="peak")
		print('\033[32m' + 'SUCCESS：SAVE TO ' + peak_graph_path + '\033[0m')

		# ノイズ成分をプロット
		noise_graph_path = output_folder_path + "noise.png"
		if V_size > M: # 通常の処理
			plot_data(fig_size=(8, 5),
					title="Noise Component (M = " + str(M) + ", V_index: " + str(V_index) + "~" + str(M) + ")",
					save_path=noise_graph_path,
					ylabel="Electric Power μcal/sec", xlabel="Time[min]",
					data1=[x, noise_component],
					label1="noise")

		else: # 要素波形の数がMに満たないときの処理 
			plot_data(fig_size=(8, 5),
					title="Noise Component (M = " + str(M) + ", V_index: " + str(V_index) + "~" + str(V_size) + ")",
					save_path=noise_graph_path,
					ylabel="Electric Power μcal/sec", xlabel="Time[min]",
					data1=[x, noise_component],
					label1="noise")
		print('\033[32m' + 'SUCCESS：SAVE TO ' + noise_graph_path + '\033[0m')
		

		# ピーク成分とノイズ成分を重ねてプロット
		peak_noise_graph_path = output_folder_path + "peak_noise.png"
		plot_data(fig_size=(8, 5),
					title="Peak And Noise Component (M = " + str(M) + ", V_index: " + str(V_index) + ")",
					save_path=peak_noise_graph_path,
					ylabel="Electric Power μcal/sec", xlabel="Time[min]",
					data1=[x, noise_component],
					data2=[x, peak_component],
					label1="noise", label2="peak")
		print('\033[32m' + 'SUCCESS：SAVE TO ' + peak_noise_graph_path + '\033[0m')


# ピーク成分とノイズ成分の積分値の差を計算する関数
def plot_difference_peak_noise(svd_split_path_base, output_folder_path, titration_count):
    
    difference_peak_noise = []
    for i in range(titration_count + 1):
        csv_file_peak = svd_split_path_base +f"_{i}/peak.csv" # ピーク成分を保存するCSVファイルパス
        csv_file_noise = svd_split_path_base +f"_{i}/noise.csv" # ノイズ成分を保存するCSVファイルパス
        csv_file_time = svd_split_path_base +f"_{i}/time.csv" # 時間を保存するCSVファイルパス

        # フォルダにcsv_file_peak,noise,timeの全部があったら計算
        if all([os.path.isfile(csv_file_peak), os.path.isfile(csv_file_peak), os.path.isfile(csv_file_time)]):
            peak_component, noise_component, time = [], [], []
            # peak_component読み込み
            with open(csv_file_peak, encoding='utf8', newline='') as f:
                csvreader = csv.reader(f)
                for row in csvreader:
                    peak_component.append(float(row[0])) # 1行ずつリストpeak_componentに入れていく
            
            # noise_component読み込み
            with open(csv_file_noise, encoding='utf8', newline='') as f:
                csvreader = csv.reader(f)
                for row in csvreader:
                    noise_component.append(float(row[0])) # 1行ずつリストpeak_componentに入れていく
            # time読み込み
            with open(csv_file_time, encoding='utf8', newline='') as f:
                csvreader = csv.reader(f)
                for row in csvreader:
                    time.append(float(row[0])) # 1行ずつリストpeak_componentに入れていく

            V_size = len(peak_component) # 要素波形の数（ピーク成分、またはノイズ成分の行列の長さに相当）
            x = np.linspace(time[0], time[-1], V_size) # x軸を時間に変換
            '''
            積分計算
            '''
            # 参考：https://org-technology.com/posts/integrate-function-fixed-sample.html
            peak_component_integral = integrate.simps(peak_component, x) # ピーク成分の積分値（シンプソン法。他にも台形法、Romberg法などが使える）
            noise_component_integral = integrate.simps(noise_component, x) # ノイズ成分の積分値
            difference_peak_noise.append(peak_component_integral - noise_component_integral) # ピーク成分とノイズ成分の積分値の差を格納していく（滴定回数分）

        # フォルダにcsv_file_peakとcsv_file_noiseのどちらか、または両方なかったらNone(欠損値) ← 後でスプライン補完（最初からdf使っとけばよかったと後悔w）
        else:
            difference_peak_noise.append(None)

        print(str(i) + "回目の滴定のピーク成分とノイズ成分の積分値の差は" + str(difference_peak_noise[i]) + "です")

    '''
    ピーク成分とノイズ成分の積分値の差分（何を意味する？電力量の差分？）をプロット
    → ピーク成分(ノイズ成分を除いたもの)の積分値をプロット
    '''
    x_diff = np.array(range(0, titration_count + 1)) # [0~(titration_count-1)]
    difference_peak_noise_graph_path = output_folder_path + "diff_peak_noise.png"
    x_diff_spline, difference_peak_noise_spline = spline_interp_missing_value(x_diff, difference_peak_noise) # 欠損値のスプライン補完
    x_diff_spline, difference_peak_noise_spline = spline_interp(x_diff_spline, difference_peak_noise_spline) # スプライン曲線に変換
	
    plot_data(fig_size=(8, 5),
				title="Integral Value of Peak Component",
				save_path=difference_peak_noise_graph_path,
				ylabel="integral value(= Electric energy?)", xlabel="Number of titrations = " + str(titration_count),
				data1=[x_diff, difference_peak_noise],
				data2=[x_diff_spline, difference_peak_noise_spline],
				label1="sample", label2="curve",
				type1="scatter")
    print('\033[32m' + 'SUCCESS：SAVE TO ' + difference_peak_noise_graph_path + '\033[0m')
