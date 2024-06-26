# class freq_sc

# python version: 3.8.17
# encoding: utf-8


class freq_sc():
    def __init__(self, path: str) -> None:
        self.path = path
        self.data = []
        self.header = {}
        self.freq = []
        self.rev_freq = []
        self.i_rec = 0
        self.freq_lower_threshold = 5

        with open(self.path, "rb") as f:
            data = f.readlines()
        
        # sort data
        new_data = [0] * (len(data)-6)
        for i in range(len(data)-6):
            new_data[i] = str(data[i+6]).replace("\r\n", "")[11:61].replace(" -", "").split()
        data = new_data[:-1]

        new_data = []
        for i in data:
            for k in i:
                new_data.append(k)

        # update data
        self.data = new_data


    def wave_format(self) -> None:
        header = {}
        i = 0
        self.data

        # search riff, format, data
        rec_riff, rec_format, rec_data = False, False, False
        while i < len(self.data):
            if self.bin_equals(self.data[i:i+4], "RIFF"):
                header["riff"] = "RIFF "
                rec_riff = True
                i += 4
                continue
            if self.bin_equals(self.data[i:i+4], "fmt"):
                header["format"] = "fmt "
                rec_format = True
                i += 4
                continue
            if self.bin_equals(self.data[i:i+4], "data"):
                header["data"] = "data "
                rec_data = True
                rec_format = False
                i += 4
                continue
            if self.bin_equals(self.data[i:i+4], "WAVE") or self.bin_equals(self.data[i:i+4], "AVI"):
                header["riff"] += " WAVE"
                i += 4
                rec_riff = False
                continue

            if rec_riff:
                header["riff"] += self.data[i]
            if rec_format:
                header["format"] += self.data[i]
            if rec_data:
                header["data"] += self.data[i]
            i += 1

        header["riff"] = header["riff"].split()
        header["format"] = header["format"].split()
        header["data"] = header["data"].split()

        new_header = {}
        new_header["format"] = {}
        new_header["format"][1] = {}
        new_header["format"][1]["size"] = "".join(self.rev_byte2(self.str2list(header["format"][1][0:8]), 4))
        new_header["format"][1]["format"] = "".join(self.rev_byte2(self.str2list(header["format"][1][8:12]), 2))
        new_header["format"][1]["channel"] = "".join(self.rev_byte2(self.str2list(header["format"][1][12:16]), 2))
        new_header["format"][1]["freq"] = "".join(self.rev_byte2(self.str2list(header["format"][1][16:24]), 4))
        new_header["format"][1]["byte_per_sec"] = "".join(self.rev_byte2(self.str2list(header["format"][1][24:32]), 4))
        new_header["format"][1]["block_size"] = "".join(self.rev_byte2(self.str2list(header["format"][1][32:36]), 2))
        new_header["format"][1]["bit_depth"] = "".join(self.rev_byte2(self.str2list(header["format"][1][36:40]), 2))
        header["format"] = [header["format"][0], new_header["format"][1]]

        header["data"] = [header["data"][0], header["data"][1][0:8], header["data"][1][8:]]

        # update header
        self.header = header


    def __repr__(self) -> str:
        string = "\n"
        string += "------- ヘッダ情報 -------\n"

        # RIFF
        string += f"riff識別子: {self.header['riff'][0]}\n";   temp = "".join(self.rev_byte2(self.str2list(self.header["riff"][1]), 4))
        string += f"riffチャンクサイズ: {temp} ({int(temp, 16)} byte)\n"
        string += f"フォーマット識別子: {self.header['riff'][2]}\n"
        string += "\n"

        # format
        string += "format識別子: {}\n".format(self.header['format'][0])
        string += "formatチャンクサイズ: {} ({} byte)\n".format(self.header["format"][1]["size"], int(self.header["format"][1]["size"], 16))
        string += "音声フォーマット: {} ({})\n".format(self.header["format"][1]["format"], int(self.header["format"][1]["format"], 16))
        string += "チャンネル数: {} ({})\n".format(self.header["format"][1]["channel"], int(self.header["format"][1]["channel"], 16))
        string += "サンプリング周波数: {} ({} samples)\n".format(self.header["format"][1]["freq"], int(self.header["format"][1]["freq"], 16))
        string += "1秒間のバイト数平均: {} ({} byte/s)\n".format(self.header["format"][1]["byte_per_sec"], int(self.header["format"][1]["byte_per_sec"], 16))
        string += "ブロックサイズ: {} ({})\n".format(self.header["format"][1]["block_size"], int(self.header["format"][1]["block_size"], 16))
        string += "ビット深度: {} ({} bit)\n".format(self.header["format"][1]["bit_depth"], int(self.header["format"][1]["bit_depth"], 16))
        string += "\n"

        # data
        string += f"data識別子: {self.header['data'][0]}\n";   temp = "".join(self.rev_byte2(self.str2list(self.header["data"][1]), 4))
        string += f"dataチャンクサイズ: {temp} ({int(temp, 16)})\n"
        string += "-----------------------\n\n"

        # freq
        string += "------- 周期データ探索結果 -------\n"
        string += f"{' '.join(self.freq)}\n"
        string += "\n"
        string += "(参考)次のデータ : {} ...\n".format(''.join(self.header["data"][2][self.i_rec * 2 : self.i_rec * 2 + len(self.freq) * 2]))
        string += "項数 : {}\n".format(len(self.freq) // 2)
        string += "周波数予想 : {} Hz\n".format(int(self.header["format"][1]["freq"], 16) // (len(self.freq) // 2))
        string += "---------------------------------\n\n"

        string += "------- 2byteごとの反転データ(10進数) -------\n"
        string += f"{' '.join(self.decimal_rev_freq)}\n"
        string += "-----------------------------------------\n"

        return string


    def calc_freqbyte(self) -> None:
        datas = self.header["data"][2]
        
        memory = []
        for i in range(len(datas) // 4):
            data = datas[i*2] + datas[i*2+1]

            if datas[i*2 : i*2+len(memory)*2] == "".join(memory) and len(memory) > self.freq_lower_threshold:
                self.freq = memory
                self.i_rec = i
                break

            else:
                memory.append(data)


    def rev_byte(self) -> None:
        rev_freq = self.rev_byte2(self.freq, 2)
        self.rev_freq = rev_freq


    def toDecimal(self) -> None:
        decimal = []
        for i in range(len(self.rev_freq) // 2):
            data = self.rev_freq[i*2] + self.rev_freq[i*2+1]
            data = self.hex_to_decimal(data)
            decimal.append(str(data))
        self.decimal_rev_freq = decimal


    @staticmethod
    def str2list(string: str) -> list:
        return [string[2*i] + string[2*i+1] for i in range(len(string) // 2)]


    @staticmethod
    def rev_byte2(bin: list, digits: int) -> str:
        rev_bin = bin.copy()
        for i in range(len(bin) // digits):
            for k in range(digits):
                rev_bin[i*digits+k] = bin[i*digits+digits-k-1]
        return rev_bin


    @staticmethod
    def bin_equals(bin: str, string: str) -> bool:
        for i in range(len(string)):
            if int(bin[i], 16) != ord(string[i]):
                return False
        return True


    @staticmethod
    def hex_to_decimal(xhex: str) -> int:
        dec = int(xhex, 16)
        if dec > 2**15 - 1:
            dec = (2**16 - dec) * -1
        return dec
