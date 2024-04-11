# -*- coding:utf-8 -*-
import time
import csv
import os

import numpy as np
from scipy.interpolate import spline
import matplotlib.pyplot as plt
import matplotlib.image as img

import add_import_paths  # не удалять тут пути прописываются
add_import_paths.add_public_path()

import techChannel
import shortClasses


TEST_TEXT_NUMBER = u"Класс анализа ПЗУ."
TEST_DESCRIPTION = u"В этом классе описаны методы, связанные с анализом ПЗУ."

TEST_PATH = 'C:\Users\User\Desktop\work\Romka\TKPA_GVM100-6_PO_U.10048-01\Gurza\RomAnalyzer\MedHelp\TestProg_0x30.run'


class RomAnalyzer:
    def __init__(self):
        self.GVM = None
        self.GVM_connection = False

        self.dir_path = u'RomAnalyzerData' + os.sep
        self.cur_path = None

        if not os.path.exists(self.dir_path):
            os.mkdir(self.dir_path)

        self.data = list()

    def create_connection(self, protocol_type, port_name, number_vm, work_speed):
        self.GVM = techChannel.TechChannel(protocol_type, port_name, number_vm, work_speed)
        number_vm = self.GVM.interface.numberVM
        print(u"Ожидание соединения с ВМ{}...".format(number_vm))

        return_data = self.GVM.open_link()
        if return_data.error:
            output_string = u"Нет устройства для связи (ВМ{})".format(number_vm)
        else:
            self.GVM_connection, output_string = self.check_connection()

        print(output_string)

    def check_connection(self):
        number_vm = self.GVM.interface.numberVM
        success = True

        # проверяем эхо («Тест - Установка соединения»)
        return_data = self.GVM.check_link_long()
        if return_data.error:
            success = False
            output_string = u"Нет соединения по тех. каналу с ВМ{}".format(number_vm)
        else:
            output_string = (u"Соединение по тех. каналу с ВМ{} установлено".format(number_vm))

        return success, output_string

    def close_connection(self):
        number_vm = self.GVM.interface.numberVM
        self.GVM.close_link()
        self.GVM_connection = False
        self.GVM = None
        print u"Соединение с ВМ{} закрыто".format(number_vm)

    def load_test(self, test_path):
        if not self.GVM_connection:
            return

        time_start = time.clock()
        return_data = self.GVM.file_to_device(test_path)
        if return_data.error is True:
            print u"Ошибка при работе с загружаемым тестом"
        else:
            print u"Загружаемый тест готов к использованию: \"{}\"".format(test_path)
        time_end = time.clock()

        print 'Время загрузки теста: {} сек.'.format(time_end - time_start)

    def launch_test(self, parameter_1, parameter_2):
        if not self.GVM_connection:
            return

        start_address = self.GVM.fileParser.get_address()

        time_start = time.clock()
        return_data = self.GVM.start_load_test_long(start_address,
                                                    parameter_1,
                                                    parameter_2)
        time_end = time.clock()

        print u'\n\nВремя работы теста: {} сек.'.format(time_end - time_start)

        return return_data.data

    def read_sector(self, sector_number):
        if not self.GVM_connection:
            return

        time_start = time.clock()
        sector_size = shortClasses.GVM_PZU_K[sector_number]
        sector_address = self.GVM.get_flash_info(sector_number, 1).data | 0xA0000000
        next_sector_address = sector_address + sector_size
        max_read_count = 248
        ptr = sector_address

        while ptr + max_read_count < next_sector_address:
            self.data.extend(self.GVM.read_memory_long(ptr, max_read_count).data)
            ptr += max_read_count

        remaining_space = next_sector_address - ptr
        if ptr != sector_address and remaining_space > 0:
            self.data.extend(self.GVM.read_memory_long(ptr, remaining_space).data)

        time_end = time.clock()

        print 'Время чтения сектора ПЗУ: {} сек.'.format(time_end - time_start)

    def create_csv(self, cycle_n):
        csv_file_path = self.cur_path + 'csv_raw_data_{}.csv'.format(cycle_n)
        csv_file = open(csv_file_path, 'w')
        writer = csv.writer(csv_file, delimiter=',', lineterminator='\n')

        cols = 248
        rows = len(self.data) / cols

        for row in range(rows):
            tmp_list = list()
            for col in range(cols):
                num = col + row * cols
                tmp_list.append(self.data[num])
            writer.writerow(tmp_list)

    def read_csv(self, cycle_n):
        csv_file_path = self.cur_path + 'csv_raw_data_{}.csv'.format(cycle_n)
        csv_file = open(csv_file_path, 'r')
        reader = csv.reader(csv_file, delimiter=',', lineterminator='\n')

        # НЕ ДОДЕЛАНО
        # for el in reader:
        #     print(el)

    def change_folder(self, folder):
        self.cur_path = self.dir_path + folder + os.sep
        if not os.path.exists(self.cur_path):
            os.mkdir(self.cur_path)


if __name__ == "__main__":
    rom_entity = RomAnalyzer()

    rom_entity.change_folder(time.strftime("%H_%M_%S-%d_%m_%Y"))
    rom_entity.create_connection("GVM_Mon",
                                 "COM3",
                                 0,
                                 57600)

    if rom_entity.GVM_connection:
        rom_entity.load_test(TEST_PATH)

        cycle_number = 0
        while True:
            print u'\nЦикл №{}'.format(cycle_number + 1)

            return_data = rom_entity.launch_test(0x40000 + 0x200 * cycle_number, 30)
            rom_entity.read_sector(30)
            rom_entity.create_csv(cycle_number)

            cycle_number += 1

            # НЕ ДОДЕЛАНО
            if return_data == 0xFFFFFFFF:
                break

        rom_entity.close_connection()
