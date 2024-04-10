# -*- coding:utf-8 -*-
# проверка связи rs
import time
import csv
import shortClasses
import os
import numpy as np
from scipy.interpolate import spline
import matplotlib.pyplot as plt
import matplotlib.image as img

import add_import_paths  # не удалять тут пути прописываются
add_import_paths.add_public_path()

import support_scripts
import techChannel
import datetime


TEST_TEXT_NUMBER = u"Класс анализа ПЗУ."
TEST_DESCRIPTION = u"В этом классе описаны методы, связанные с анализом ПЗУ."


class RomAnalyzer:
    def __init__(self, cur_time, sector_number=30, bool_fast_analyze=False, value_cycles=1):
        parent_dir = 'Images'
        self.dir = parent_dir + os.sep + cur_time
        self.dir_one_side = self.dir + os.sep + 'one_side'
        self.dir_another_side = self.dir + os.sep + 'another_side'

        if not os.path.exists(parent_dir):
            os.mkdir(parent_dir)
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        if not os.path.exists(self.dir_one_side):
            os.mkdir(self.dir_one_side)
        if not os.path.exists(self.dir_another_side):
            os.mkdir(self.dir_another_side)

        self.cycle = value_cycles - 1
        self.data = list()
        self.sector_number = sector_number
        self.bool_fast_analyze = bool_fast_analyze

        self.work_object = techChannel.TechChannel(protocol_type="GVM_Mon", number_vm=0)
        self.sector_address = self.work_object.get_flash_info(self.sector_number, 1).data | 0xA0000000
        self.error = support_scripts.test_check_rs232(self.work_object)

    def read_sector(self, fast=False):
        sector_size = shortClasses.GVM_PZU_K[self.sector_number]
        max_read_count = 0xe0  # 224 (7 строк по 32 )
        multiplier = 1
        next_sector_address = self.sector_address + sector_size

        ptr = self.sector_address

        if fast:
            multiplier *= 8

        while ptr + max_read_count < next_sector_address:
            self.data.extend(self.work_object.read_memory_long(ptr, max_read_count).data)
            ptr += max_read_count * multiplier

        remaining_space = next_sector_address - ptr
        if ptr != self.sector_address and remaining_space > 0:
            self.data.extend(self.work_object.read_memory_long(ptr, remaining_space).data)

    def create_csv(self, _strlen=16):
        csv_file_path_1 = self.dir_one_side + os.sep + 'data_from_gvm_one_side_{}.csv'.format(self.cycle)
        csv_file_1 = open(csv_file_path_1, 'w')
        writer_1 = csv.writer(csv_file_1, delimiter=',', lineterminator='\n')

        csv_file_path_2 = self.dir_another_side + os.sep + 'data_from_gvm_another_side_{}.csv'.format(self.cycle)
        csv_file_2 = open(csv_file_path_2, 'w')
        writer_2 = csv.writer(csv_file_2, delimiter=',', lineterminator='\n')

        _len = len(self.data)

        for row in range(_len / _strlen):
            tmp_list_1 = list()
            tmp_list_2 = list()
            for col in range(_strlen):
                num = col + row * _strlen
                if num % 4 < 2:
                    tmp_list_1.append(bin(self.data[num]).count('1'))
                else:
                    tmp_list_2.append(bin(self.data[num]).count('1'))
            writer_1.writerow(tmp_list_1)
            writer_2.writerow(tmp_list_2)

        csv_file_1.close()
        csv_file_2.close()

    def create_image(self, csv_file_path, image_file_path):
        cmap = 'BuPu'
        vmin, vmax = 0, 8
        data = np.genfromtxt(csv_file_path, delimiter=',')
        img.imsave(image_file_path, data, vmin, vmax, cmap=cmap)
        # plt.imshow(img.imread(image_file_path))
        # fig, ax = plt.subplots()
        # pcm = ax.pcolormesh(data, cmap=cmap, rasterized=True, vmin=vmin, vmax=vmax)
        # fig.colorbar(pcm, pad=0.01, shrink=0.5)
        # ax.invert_yaxis()
        # ax.set_aspect('equal')
        # ax.set_title('Memory state')
        # fig.set_dpi(300)
        # plt.savefig(image_file_path)
        plt.close()

    def sum_data_in_csv(self, csv_file_path, max_i, max_j):
        csvfile = open(csv_file_path)
        reader = csv.reader(csvfile, delimiter=',')
        data = list(reader)
        res = 0
        for i in range(max_i):
            for j in range(max_j):
                res += int(data[i][j])

        return res

    def create_graphics(self):
        self.cycle = -1
        is_exit = False
        sum1 = list()
        sum2 = list()
        y1 = list()
        y2 = list()
        max_i = 64 if self.bool_fast_analyze else 512
        max_j = 128 if self.bool_fast_analyze else 128

        #makes images
        while self.cycle == -1 or not is_exit:
            self.cycle += 1
            csv_file_path_1 = self.dir_one_side + os.sep + 'data_from_gvm_one_side_{}.csv'.format(self.cycle)
            csv_file_path_2 = self.dir_another_side + os.sep + 'data_from_gvm_another_side_{}.csv'.format(self.cycle)
            if os.path.exists(csv_file_path_1):
                sum1.append(self.sum_data_in_csv(csv_file_path_1, max_i, max_j))
                sum2.append(self.sum_data_in_csv(csv_file_path_2, max_i, max_j))
                if self.cycle != 0:
                    y1.append(sum1[self.cycle] - sum1[self.cycle - 1])
                    y2.append(sum2[self.cycle] - sum2[self.cycle - 1])
                # image_file_path_1 = self.dir_one_side + os.sep + 'image_from_data_{}.png'.format(self.cycle)
                # image_file_path_2 = self.dir_another_side + os.sep + 'image_from_data_{}.png'.format(self.cycle)
                # self.create_image(csv_file_path_1, image_file_path_1)
                # self.create_image(csv_file_path_2, image_file_path_2)
            else:
                is_exit = True

        #makes graph
        if len(y1) > 0:
            x = np.array(range(0x36000, 0x36000 + (self.cycle - 1) * 0x200, 0x200))
            y1 = np.array(y1)
            y2 = np.array(y2)
            # x_interpolated = np.linspace(x.min(), x.max(), 500)
            # y1_interpolated = spline(x, y1, x_interpolated)
            # y2_interpolated = spline(x, y2, x_interpolated)
            #
            # plt.plot(x_interpolated, y1_interpolated)
            # plt.plot(x_interpolated, y2_interpolated)

            plt.plot(x, y1)
            plt.plot(x, y2)
            plt.ylabel('Bits erased')
            plt.xlabel('Counts')

            fig = plt.gcf()
            fig.savefig(self.dir + os.sep + 'graph.png')
            plt.show()
            plt.close()

    def analyze_states(self, zeros_stage=False):
        fstate_start, fstate_mid, fstate_end = 0xFF, 0xFF, 0xFF
        read_length = 16
        state_start = self.work_object.read_memory_long(self.sector_address, read_length).data
        state_mid = self.work_object.read_memory_long(self.sector_address + 0x8000, read_length).data
        state_end = self.work_object.read_memory_long(self.sector_address + 0x1FFF0, read_length).data
        for i in range(read_length):
            fstate_start &= state_start[i]
            fstate_mid &= state_mid[i]
            fstate_end &= state_end[i]
        if zeros_stage:
            return fstate_start | fstate_mid | fstate_end
        return fstate_mid | fstate_end

    def checkRom(self):
        for el in self.data:
            if el != 0xFF:
                return False
        return True

    # Главная функция. Использовать для чтения ПЗУ в sourceMedHelp.py
    def analyze(self, check_if_not_erased=False):
        print(u"\nЧтение сектора...")

        start_time = time.time()
        self.read_sector(fast=self.bool_fast_analyze)
        is_erased = False
        if check_if_not_erased:
            is_erased = self.checkRom()
        print(u"Время чтения сектора: {}s.".format(time.time() - start_time))
        self.create_csv(_strlen=256)

        support_scripts.print_status_scripts(self.error)  # Вывод результатов тестирования
        print(u"<Log> {}".format(datetime.datetime.now()))

        return is_erased

    def close_analyzer(self):
        self.work_object.close_link()


if __name__ == "__main__":
    # Создание изображений на основе .csv в указываемой папке
    # folder_name = input(u'Введите название папки (в кавычках): ')

    romka = RomAnalyzer(cur_time='2024_03_20_13_16_13')
    romka.create_graphics()
    romka.close_analyzer()
