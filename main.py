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
    input_file_path_itc = "data/200203C/200203C.ITC" # data/200203C/200203C.ITC
    input_file_path_nitpic = "data/200203C/200203C.nitpic" # nitpicファイル

    os.makedirs("output", exist_ok=True)

    '''
    itc_file_data_visualization(分析対象のITCファイルのPATH（入力ファイル）, output_folder_path)
    第1引数: input_file_path_itc → 分析対象のITCファイルのパス
    第2引数: output_folder_path → 出力フォルダのパス（"/output"）
    '''
    print('\033[34m' + 'RUN：itc_file_data_visualization' + '\033[0m')
    experimental_data_path, titration_count = itc(input_file_path_itc, "output/")
    print('\033[34m' + 'Task of itc_file_data_visualization completed!!!')

    '''
    singular_value_decomposition(input_file_path_itc, all_data_path, titration_count, output_folder_path, M, V_index)
    第1引数: input_file_path_itc → 分析対象のITCファイルのパス
    第2引数: all_data_path → itc_file_data_visualization関数で作成したすべての実験データが保存されているCSVファイルのパス
    第3引数: titration_count → 滴定回数
    第4引数: output_folder_path → 出力フォルダのパス（"/output"）
    第5引数: M → スライド窓のステップ数M
    第6引数: V_index → 要素波形のどこまでをピーク成分とするか
    '''
    print('\033[34m' + 'RUN：singular_value_decomposition' + '\033[0m')
    svd(input_file_path_itc, experimental_data_path, titration_count, "output/", 50, 4)
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
