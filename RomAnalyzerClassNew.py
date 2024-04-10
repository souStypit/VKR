# -*- coding:utf-8 -*-
import time
import csv
import shortClasses
import os
import io

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
    def __init__(self):
        self.GVM = None
        self.GVM_connection = False

        _dir = 'RomAnalyzerData'
        self.dir_path = _dir + os.sep

        if not os.path.exists(_dir):
            os.mkdir(_dir)

        self.data = list()

    def create_connection(self):
        self.GVM = techChannel.TechChannel(protocol_type="GVM_Mon", number_vm=0)
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
        self.GVM.close_link()
        self.GVM_connection = False
        self.GVM = None

    def read_sector(self, sector_number):
        if not self.GVM_connection:
            return

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

    def create_csv(self):
        csv_file_path = self.dir_path + 'csv_raw_data_{}.csv'.format(0)
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

    def read_csv(self):
        csv_file_path = self.dir_path + 'csv_raw_data_{}.csv'.format(0)
        csv_file = open(csv_file_path, 'r')
        reader = csv.reader(csv_file, delimiter=',', lineterminator='\n')

        for el in reader:
            print(el)


if __name__ == "__main__":
    rom_entity = RomAnalyzer()

    rom_entity.create_connection()
    rom_entity.check_connection()
    rom_entity.read_sector(30)
    rom_entity.close_connection()

    rom_entity.create_csv()
    rom_entity.read_csv()

    # print rom_entity.data
