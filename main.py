from freq_sc import freq_sc

# ------------------------------------ #

# ファイルパス引数指定 (*.txt)
import sys
args = sys.argv
path = args[1]

# ファイルパス直接指定 (*.txt)
# path = "input.txt"

# ------------------------------------ #


def main():
    global path

    # ファイル(path)からデータを読み込む
    txt = freq_sc(path)

    # waveフォーマットを解析する
    txt.wave_format()

    # 周期的なデータを探索する
    txt.calc_freqbyte()

    # バイトを反転する
    txt.rev_byte()

    # 2byteごとの反転データを10進数に変換する
    txt.toDecimal()

    # 結果を表示する
    print(txt)

    # グラフ表示
    # import matplotlib.pyplot as plt
    # plt.plot([int(i) for i in txt.decimal_rev_freq])
    # plt.show()


main()