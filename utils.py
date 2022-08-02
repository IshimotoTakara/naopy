"""
関数
"""
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d


# 配列の','区切りの要素を','毎に分割する関数
def separate_with_commas(param):
    l = []
    [l.append(s.split(',')) for s in param]

    return l

# ３次元配列["time0,ep0,temp0", "time1,ep1,temp1","",,,,]を辞書に変換する関数
# time, electric_power, degree, dictionaryを返す
def make_dictionary(data):
    time, electric_power, degree = [], [], []
    for s in data:
        time.append(float(s[0]) / 60) # 単位を[sec]に変換
        electric_power.append(float(s[1]) / 60) # 単位を[μcal/sec]に変換
        degree.append(float(s[2]))
    
    # 全データを１回目の滴定のでの電力で引く（→0スタートになる）
        electric_power_from_zero = []
        first_electric_power = electric_power[0] # 最初の電力データ
        for ep in electric_power: 
            electric_power_from_zero.append(ep - first_electric_power)

    dictionary = {'Time': time, 'ElectricPower': electric_power_from_zero, 'Degree': degree}

    return time, electric_power_from_zero, degree, dictionary

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
