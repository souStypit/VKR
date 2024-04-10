# -*- coding:utf-8 -*-

from __future__ import print_function
import threading
import Queue
import os
import time
import noteInfo
# import logBuilder
import datetime
import RomAnalyzerClass
try:
    import shortClasses
except ImportError:
    from tech_work.TechChannel import shortClasses
try:
    import techChannel
except ImportError:
    from tech_work.TechChannel import techChannel
# ----------------------------------------------------------------------------------------------------------------------


class WorkThread:

    SelCom_K = (None, "First", "Second", "All")
    ErrorControl_K = ("Ignore", "FirstError", "LimitError")
# ----------------------------------------------------------------------------------------------------------------------

    def __init__(self):

        # интерфейсы каналов
        self._interface_channel_1 = None
        self._interface_channel_2 = None

        # ручное задание кома
        self._manual_com_channel_1 = None
        self._manual_com_channel_2 = None

        # переменная для выхода
        self._exit_flag = False

        # массив с текущими заданиями
        self._array_data = []

        # счетчик для режима ограниченного циклирования
        self._counter_cycle_limit = 0

        # выбор работы на комах
        self._select_com = self.SelCom_K[0]
        # скорость прописанная в конфигурационном файле
        self._required_br = 19200

        # флаг для немедленного завершения тестирования
        # self._test_end_flag = False

        # флаг для завершение тестирования в конце итерации
        self._flag_stop_test_after_end_cycle = False

        # управление паузой
        self._pause_control = False
        self._save_test_parameters = 0

        self.value_error = 0

        # для повторного запуска загруженного теста без загрузки
        self._pre_form_file = ""

        # контроли управления по количеству ошибок
        self._error_control = self.ErrorControl_K[0]
        self._value_error = 0

        self._parameter_1 = 0
        self._parameter_2 = 0
        self._parameter_3 = 0
        self._parameter_4 = 0

        self._list_data_store = []

        # self._break_puts_queue = False
        # self._puts_string = u""

        self.code_between_write_and_start_code = None
        self.code_after_end_test = None

        self.info_about_gvm = {}

        # переменные для сохранения информационных данных при работе тестов
        self.personal_data_channel = [[], []]

        self._special_tag = u"prime_tag"
        self._answer_queue = None
        self.control_queue = Queue.Queue()

        self.test_return_data = None
# ----------------------------------------------------------------------------------------------------------------------

    def set_special_tag(self, new_name):
        self._special_tag = u"{}".format(new_name)
# ----------------------------------------------------------------------------------------------------------------------

    def get_special_tag(self):
        return self._special_tag
# ----------------------------------------------------------------------------------------------------------------------

    def set_queue(self, par_queue):
        if isinstance(par_queue, Queue.Queue) is True:
            self._answer_queue = par_queue
# ----------------------------------------------------------------------------------------------------------------------
#
#     # получение настроек скрипта
#     def get_setup(self, print_setup=True):
#         if print_setup is True:
#             print(self.channel_1)
#             print(self.channel_2)
#             print(self._select_com)
#             print(self._counter_cycle_limit)
#         else:
#             return [self.channel_1, self.channel_2, self._select_com, self._counter_cycle_limit]
# ----------------------------------------------------------------------------------------------------------------------

    def set_com_channel(self, channel_one=None, channel_two=None):
        self._manual_com_channel_1 = channel_one
        self._manual_com_channel_2 = channel_two
# ----------------------------------------------------------------------------------------------------------------------

    # выход из бесконечного цикла
    def exit_inf_cycle(self):
        self._exit_flag = True
# ----------------------------------------------------------------------------------------------------------------------

    # def get_test_end(self):
    #     return self._test_end_flag
# ----------------------------------------------------------------------------------------------------------------------

    def stop_test_after_end_cycle(self):
        self._flag_stop_test_after_end_cycle = True
# ----------------------------------------------------------------------------------------------------------------------

    # метод установки контроля ошибок
    def set_error_control(self, type_control, value=0):
        # установка контроля над ошибками
        if type_control not in self.ErrorControl_K:
            self._error_control = self.ErrorControl_K[0]
        else:
            self._error_control = type_control

        # установка количества ошибок до выхода из программы
        if (type(value) != int) and (type(value) != long):
            self._value_error = 0
        else:
            self._value_error = value
# ----------------------------------------------------------------------------------------------------------------------

#     # метод установки паузы
#     def set_pause(self):
#         # self._save_test_parameters = self._counter_cycle_limit
#         self._pause_control = True
# ----------------------------------------------------------------------------------------------------------------------
#
#     # метод продолжения выполнения теста
#     def continue_task(self):
#         if self._pause_control is True:
#             # self._counter_cycle_limit = self._save_test_parameters
#             self._pause_control = False
# ----------------------------------------------------------------------------------------------------------------------

    # установка цели для тестов
    def set_required_br(self, baud_rate):
            self._required_br = baud_rate
# ----------------------------------------------------------------------------------------------------------------------

    # установка цели для тестов
    def set_target(self, target=None):
        if target in self.SelCom_K:
            self._select_com = target
        else:
            print(u"Цель задана не верно ({})".format(target))
            for data_k in self.SelCom_K:
                print(data_k)
# ----------------------------------------------------------------------------------------------------------------------

    # установка управления выполняемой задачи для бесконечного цикла
    def set_type_inf_cycle(self, parameter=0):
        self._counter_cycle_limit = parameter
# ----------------------------------------------------------------------------------------------------------------------

    # установка параметров для тестов
    def set_parameters(self, param_1, param_2, param_3, param_4):
        self._parameter_1 = param_1
        self._parameter_2 = param_2
        self._parameter_3 = param_3
        self._parameter_4 = param_4
# ----------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def check_run_file():
        # check_file
        # # проверка наличия рановского файла
        # if type(check_file) == str:
        #     list_files = os.listdir(os.getcwd())
        #     temp_extension = check_file.split(".")[-1]
        #     if (temp_extension == "run")or(temp_extension == "sre"):
        #         if check_file not in list_files:
        #             print(u"Отсутствует файл " + check_file)
        #             return True
        return False
# ----------------------------------------------------------------------------------------------------------------------

    # добавление задачи к текущим
    def add_task(self, index=0, data_add_task=None):

        # определение метода добавления задач
        # добавление нескольких задач
        if (type(data_add_task[0]) == tuple) or (type(data_add_task[0]) == list):
            counter = index
            for external_data in data_add_task:
                self._array_data.insert(counter, external_data)
                counter += 1
        # добавление одной задачи
        else:
            self._array_data.insert(index, data_add_task)
# ----------------------------------------------------------------------------------------------------------------------
    """
    # удаление задач
    def remove_task(self, index=0, len_remove=1):
        if (len_remove < 1) or (len(self._array_data) == 0):
            print u"Нечего удалять"
            return
            
        if (index + len_remove) > len(self._array_data):
            lim_del = len(self._array_data)
        else:
            lim_del = index + len_remove

        del (self._array_data[index: lim_del])
    """
# ----------------------------------------------------------------------------------------------------------------------
    """
    # чтение текущих задач
    def read_task(self):
        counter = 0
        for internal_data in self._array_data:
            print (u"{0}. {1}; {2}".format(counter, internal_data[0], internal_data[1]))
            counter += 1
    """
# ----------------------------------------------------------------------------------------------------------------------

    # метод для использования необходимых ВМ и ком портов  классом
    def check_necessary_channel(self):

        setup_channel_1 = {"manual_com_name": "_manual_com_channel_1",
                           "ref_interface": "_interface_channel_1",
                           "number_vm": 0}
        setup_channel_2 = {"manual_com_name": "_manual_com_channel_2",
                           "ref_interface": "_interface_channel_2",
                           "number_vm": 1}

        # автоматизируем процесс набора комов
        array_setup = {}
        if(self._select_com == self.SelCom_K[1]) or (self._select_com == self.SelCom_K[3]):
            array_setup["ch1"] = setup_channel_1
        if(self._select_com == self.SelCom_K[2]) or (self._select_com == self.SelCom_K[3]):
            array_setup["ch2"] = setup_channel_2

        temp_error = "Error"
        notification = u"Нет выбранных устройств для работы"
        fatal_error = True
        return_data_local = None

        for item in array_setup:
            temp_vm = None
            temp_com_name = getattr(self, array_setup[item]["manual_com_name"])
            if temp_com_name is None:
                temp_vm = array_setup[item]["number_vm"]
            else:
                # определить номер ВМ
                temp_vm = array_setup[item]["number_vm"]

            # открываем устройства и запоминаем их
            temp_parameters = ("GVM_Mon", temp_com_name, temp_vm, self._required_br)
            setattr(self, array_setup[item]["ref_interface"], techChannel.TechChannel(*temp_parameters))

            # проверяем что устройство отвечает
            return_data_local = getattr(self, array_setup[item]["ref_interface"]).open_link()
            fatal_error = return_data_local.error
            if fatal_error is True:
                temp_error = "Error"
                temp_string = u"Запрашиваемые устройства недоступны (канал {} com {} ВМ {})"
                notification = temp_string.format(item, getattr(self, array_setup[item]["manual_com_name"]), temp_vm)
                getattr(self, array_setup[item]["ref_interface"]).close_link()
                setattr(self, array_setup[item]["ref_interface"], None)
                break
            # else: # не рабочий пока код, ошибка на моменте установки атрибута
            #     if temp_vm is None:
            #         # определить номер ВМ
            #         temp_vm = getattr(self, array_setup[item]["ref_interface"]).get_number_vm().data
            #         tech_channel_wrap_obj = getattr(self, array_setup[item]["ref_interface"]).interface
            #         setattr(self, tech_channel_wrap_obj.numberVM, str(temp_vm))

        if fatal_error is False:
            temp_error = "Summary"
            notification = u"Все требуемые устройства присутствуют"
        return shortClasses.ErrorContainer(fatal_error, temp_error, notification, return_data_local, self)
# ----------------------------------------------------------------------------------------------------------------------

    # метод закрытия класса и закрытия ком порта
    def close_channels(self):

        # подготавливаем цикл
        full_setup = []
        if self._interface_channel_1 is not None:
            full_setup.append({"ref_interface": self._interface_channel_1})
        if self._interface_channel_2 is not None:
            full_setup.append({"ref_interface": self._interface_channel_2})

        # закрываем все в цикле
        for item in range(len(full_setup)):
            full_setup[item]["ref_interface"].close_link()
            # return_data_local = full_setup[item]["ref_interface"].close_link()
            # return_data_local.print_all_data()
            full_setup[item]["ref_interface"] = None
# ----------------------------------------------------------------------------------------------------------------------

    def stub_branch(self, *parameters):
        pass
# ----------------------------------------------------------------------------------------------------------------------

    def load_test(self, name, test_file_par, channel_ref, note_info_par, queue):

        time_load = 0
        start_address = None
        type_test = None
        add_data = None
        temp_error = None

        # проверка наличия связи и попытка ее восстановления
        return_data = channel_ref.check_link_long()
        if return_data.error is True:
            return_data = channel_ref.try_reconnect()
            if return_data.error is True:
                notification = u"Нет связи с устройством"
                temp_error = shortClasses.ErrorContainer(True, "Error", notification, None, self)

        if temp_error is None:

            self.set_parameters(0, 0, 0, 0)

            # если в параметре к тесту указана строка - это зачит тест загружаемый "run" и др. или встроенный
            if type(test_file_par[1]) == str:

                # разделяем загружаемые тесты и встроенные
                temp_extension = test_file_par[1].split(".")[-1]
                if (temp_extension == "run")or(temp_extension == "sre"):

                    type_test = "load_test"

                    # выбираем пути расположения тестов
                    if os.path.isfile(test_file_par[1]) is True:
                        full_path = test_file_par[1]
                    else:
                        full_path = self.info_about_gvm["pathToFiles"] + test_file_par[1]
                        if os.path.isfile(full_path) is True:
                            pass
                        else:
                            full_path = os.path.dirname(__file__) + os.sep + test_file_par[1]

                    time_start = time.time()

                    # загрузка данных в ГВМ
                    return_data = channel_ref.file_to_device(full_path)
                    if return_data.error is True:
                        notification = u"Ошибка при работе с образом в тесте({0})".format(name)
                        temp_error = shortClasses.ErrorContainer(True, "Debug", notification, return_data, self)
                    else:
                        start_address = channel_ref.fileParser.get_address()

                        if return_data.description != u"Данный образ уже готов к использованию":
                            time_load = time.time() - time_start
                else:
                    add_data = int(test_file_par[1], 16)
                    type_test = "build_in"

            elif type(test_file_par[1]) == tuple:

                # определение файл или адрес
                if type(test_file_par[1][0]) == str:

                    type_test = "load_test"

                    # выбираем пути расположения тестов
                    if os.path.isfile(test_file_par[1][0]) is True:
                        full_path = test_file_par[1][0]
                    else:
                        full_path = self.info_about_gvm["pathToFiles"] + test_file_par[1][0]
                        if os.path.isfile(full_path) is True:
                            pass
                        else:
                            full_path = os.path.dirname(__file__) + os.sep + test_file_par[1][0]

                    time_start = time.time()

                    # загрузка данных в ГВМ
                    return_data = channel_ref.file_to_device(full_path)
                    if return_data.error is True:
                        notification = u"Ошибка при работе с образом в тесте({0})".format(name)
                        temp_error = shortClasses.ErrorContainer(True, "Debug", notification, return_data, self)
                    else:
                        start_address = channel_ref.fileParser.get_address()

                        if return_data.description != u"Данный образ уже готов к использованию":
                            time_load = time.time() - time_start
                # тест выполняемый по указанному адресу
                else:
                    start_address = test_file_par[1][0]
                    type_test = "start_address"

                # переписываем параметры в класс, дополняем недостающие обрезаем лишние
                temp_parameters = list(test_file_par[1][1:])
                if len(temp_parameters) >= 4:
                    temp_parameters = temp_parameters[:4]
                else:
                    for counter in range(4 - len(temp_parameters)):
                        temp_parameters.append(0)

                self.set_parameters(*temp_parameters)

            else:
                notification = u"Неверно задан формат теста ({0})".format(name)
                temp_error = shortClasses.ErrorContainer(True, "Error", notification, test_file_par, self)

        # если ошибок не было передаем управляющие данныя для этапа запуска теста
        if temp_error is None:
            notification = u"Этап загрузки завершен для {}".format(name)
            temp_control_data = {"type_test": type_test, "start_address": start_address, "add_data": add_data}
            temp_error = shortClasses.ErrorContainer(False, "Summary", notification, dict(temp_control_data), self)

        setattr(note_info_par, "time_load", time_load)

        # сохраняем параметры для запуска теста, смотреть их будем только в этапе запуска тестов
        queue.put((name, temp_error))
# ----------------------------------------------------------------------------------------------------------------------

    def launch_test(self, name, channel_ref, note_info_par, queue):

        temp_error = None
        counter_temp_error = 0
        time_process = 0
        type_test = None
        start_address = None
        local_number_vm = channel_ref.interface.numberVM
        number_test = None

        while True:

            if local_number_vm is None:
                local_number_vm = channel_ref.get_number_vm()

            if len(self.personal_data_channel[local_number_vm]) == 0:
                # time.sleep(0.1)
                if counter_temp_error > 2:
                    notification = u"Нет данных для запуска теста на {}".format(name)
                    temp_error = shortClasses.ErrorContainer(False, "Summary", notification, None, self)
                    break
                counter_temp_error += 1
            else:
                # ветка для ошибочного выполнения предыдущего этапа
                if self.personal_data_channel[local_number_vm][0].error is True:
                    temp_error = self.personal_data_channel[local_number_vm][0]
                # ветка для номально выполнения
                else:
                    type_test = self.personal_data_channel[local_number_vm][0].data["type_test"]
                    start_address = self.personal_data_channel[local_number_vm][0].data["start_address"]
                    number_test = self.personal_data_channel[local_number_vm][0].data["add_data"]
                break

        # сбрасываем данные аосле загрузки и обработки ответа от загрузки
        self.personal_data_channel[local_number_vm] = []

        # повышаем багоустойчивость, проверяем связь
        if temp_error is None:
            return_data = channel_ref.check_link_long()
            if return_data.error is True:
                return_data = channel_ref.try_reconnect()
                if return_data.error is True:
                    notification = u"Нет связи с устройством"
                    temp_error = shortClasses.ErrorContainer(True, "Error", notification, None, self)

        # производим запуск теста
        return_data = None
        if temp_error is None:
            time_start = time.time()
            # запускаем встроенный тест
            if type_test == "build_in":
                return_data = channel_ref.start_auto_test_long(number_test)
                if return_data.error is True:
                    notification = u"Ошибка при выполнении встроенного теста {}".format(number_test)
                    temp_error = shortClasses.ErrorContainer(True, "Debug", notification, return_data, self)
            # запускаем тест по адресу если это загружаемый тест или тест по адресу
            elif (type_test == "start_address") or (type_test == "load_test"):
                parameters = [start_address, self._parameter_1, self._parameter_2, self._parameter_3, self._parameter_4]
                return_data = channel_ref.start_load_test_long(*parameters)
                if (return_data.error is True) and (return_data.type_message == "Error"):
                    notification = u"Ошибка при выполнении загружаемого теста {}".format(name)
                    temp_error = shortClasses.ErrorContainer(True, "Debug", notification, return_data, self)
            else:
                notification = u"Ошибка не правильно задан параметр для {}".format(name)
                temp_error = shortClasses.ErrorContainer(True, "Debug", notification, None, self)

            time_process = time.time() - time_start

        # нужно контролировать ошибку исключения для того чтобы выдержать паузу на переинициализацию
        if isinstance(temp_error, shortClasses.ErrorContainer) is True:
            temp_variable = temp_error.get_string_error()
            for member in temp_variable:
                if (member.find(u"Исключение по адресу")) >= 0:
                    time.sleep(0.8)
        else:
            # если тесты прошли без ошибок то в return_data будет shortClasses.ErrorContainer
            return_data.data = [return_data.data]
            self.test_return_data = return_data.data[0]
            temp_error = return_data

        setattr(note_info_par, "time_process", time_process)

        queue.put((name, temp_error))
# ----------------------------------------------------------------------------------------------------------------------

    def _control_cycle(self):
        while self._exit_flag is False:
            local_temp = self.control_queue.get()
            if local_temp["Name"] == self._special_tag:
                if local_temp["Message"] == "Stop":
                    self.stop_test_after_end_cycle()
                elif local_temp["Message"] == "Exit":
                    self.exit_inf_cycle()
                else:
                    pass
# ----------------------------------------------------------------------------------------------------------------------

    def start_process(self):

        # описание ошибок находится внутри метода
        return_data = self.check_necessary_channel()
        if return_data.error is True:
            return_data.print_all_data()
            self._exit_flag = True

        # создание задачи
        if not (len(self._array_data) > 0):
            print(u"Нет задач для выполнения")
            self._exit_flag = True

        # обрабатываем флаг выхода
        if self._exit_flag is True:
            print(u"<Error> Тестирование продолжить невозможно")
            # self._test_end_flag = True
            self.value_error = 1
            self.close_channels()
            self._end_method()
            return

        # начало тестирования если грубые проверки прошли
        name_ch_1 = u"канал 1"
        name_ch_2 = u"канал 2"
        self.value_error = 0

        # создаем очередь для упорядоченного получения данных (очередь передается в класс далее)
        puts_queue = Queue.Queue()

        control_cycle_thread = threading.Thread(target=self._control_cycle)
        control_cycle_thread.start()

        # определение рабочего кода и пропись очередей для получения данных
        ref_load_ch1 = self.stub_branch
        ref_load_ch2 = self.stub_branch

        ref_start_ch1 = self.stub_branch
        ref_start_ch2 = self.stub_branch

        value_cycles = 0
        init_sus = self._array_data[0][1][1]
        erase_sus_step = 0x200
        zero_sus_step = 0x1000
        init_sus_step = 0x8000
        cur_sus = init_sus - init_sus_step
        erase_stage = False
        zeros_stage = False
        erase_start_cycle = 0
        cur_time = time.strftime("%Y_%m_%d_%H_%M_%S")
        while self._exit_flag is False:
            # 1 канал или оба канала
            if (self._select_com == self.SelCom_K[1]) or (self._select_com == self.SelCom_K[3]):
                ref_load_ch1 = self.load_test
                ref_start_ch1 = self.launch_test
                self._interface_channel_1.interface.set_label_queue(name_ch_1)
                self._interface_channel_1.interface.set_queue_pointer_puts(puts_queue)

            # 2 канал или оба канала
            if (self._select_com == self.SelCom_K[2]) or (self._select_com == self.SelCom_K[3]):
                ref_load_ch2 = self.load_test
                ref_start_ch2 = self.launch_test
                self._interface_channel_2.interface.set_label_queue(name_ch_2)
                self._interface_channel_2.interface.set_queue_pointer_puts(puts_queue)

            #  завершаем работу если количество заданных циклов исчерпано
            if self._counter_cycle_limit == 0:
                self._exit_flag = True
                continue

            # завершение кратное 1 итерации тестирования
            if self._flag_stop_test_after_end_cycle is True:
                self._exit_flag = self._flag_stop_test_after_end_cycle
                continue

            # откладываем контроль счетчика
            if self._counter_cycle_limit > 0:
                temp_counter = self._counter_cycle_limit - 1
            # если значение счетчика < 0 бесконечное выполнение
            else:
                temp_counter = self._counter_cycle_limit

            # учет количества циклов
            value_cycles += 1
            value_local_error = 0
            print(u"Цикл № {}".format(value_cycles))

            # получение данных из тестов
            for test in self._array_data:

                if self._exit_flag is True:
                    print(u"Тестирование принудительно окончено")
                    break

                # создаем новую структуру с информационными данными
                temp_note_info = noteInfo.TestDataStoreGVM()
                temp_note_info_ch1 = temp_note_info.channel_1
                temp_note_info_ch2 = temp_note_info.channel_2

                # self._puts_string = u""
                # self._break_puts_queue = False
                temp_thread = threading.Thread(target=self._print_puts_string, args=(name_ch_1, name_ch_2, puts_queue))
                temp_thread.start()

                print(u"\tТест: {}".format(test[0]), end="")
                if erase_stage:
                    cur_sus += erase_sus_step
                elif zeros_stage:
                    cur_sus += zero_sus_step
                else:
                    cur_sus += init_sus_step

                test = list(test)
                test[1] = list(test[1])
                test[1][1] = cur_sus
                test[1] = tuple(test[1])
                test = tuple(test)

                print(u"\tПараметры: {}".format(test[1][1]), end="")
                # temp_debug = [self._interface_channel_1.interface.interface.baudRate,
                #               self._interface_channel_2.interface.interface.baudRate,
                #               self._interface_channel_1.interface.required_br,
                #               self._interface_channel_2.interface.required_br]
                # print(u"(CBR_ch1: {}; RBR_ch1: {}); CBR_ch2: {}; RBR_ch2: {})".format(*temp_debug), end="")
                temp_note_info.current_time = datetime.datetime.now()

                # места загрузки данных в устройство
                argument_ch1 = [name_ch_1, test, self._interface_channel_1, temp_note_info_ch1, puts_queue]
                thread1 = threading.Thread(target=ref_load_ch1, args=argument_ch1)

                thread1.start()
                thread1.join()

                # этапы разделены по причине наличия непонятной ошибки на скорости 115200 (данные приняты не полностью)
                argument_ch2 = [name_ch_2, test, self._interface_channel_2, temp_note_info_ch2, puts_queue]
                thread2 = threading.Thread(target=ref_load_ch2, args=argument_ch2)

                thread2.start()
                thread2.join()

                # кусок кода вызываемый после загрузки кода
                if self.code_between_write_and_start_code is not None:
                    self.code_between_write_and_start_code(self)

                # # места загрузки данных в устройство
                # argument_ch1 = [name_ch_1, test, self._interface_channel_1, temp_note_info_ch1, puts_queue]
                # thread1 = threading.Thread(target=ref_load_ch1, args=argument_ch1)
                # argument_ch2 = [name_ch_2, test, self._interface_channel_2, temp_note_info_ch2, puts_queue]
                # thread2 = threading.Thread(target=ref_load_ch2, args=argument_ch2)
                #
                # thread1.start()
                # thread2.start()
                # thread1.join()
                # thread2.join()

                # места запуска программы в устройстве
                argument_ch1 = [name_ch_1, self._interface_channel_1, temp_note_info_ch1, puts_queue]
                thread1 = threading.Thread(target=ref_start_ch1, args=argument_ch1)

                argument_ch2 = [name_ch_2, self._interface_channel_2, temp_note_info_ch2, puts_queue]
                thread2 = threading.Thread(target=ref_start_ch2, args=argument_ch2)


                thread1.start()
                thread2.start()

                thread1.join()
                thread2.join()

                # заполнение информационной структуры общей
                temp_note_info.name_test = test[0]
                temp_note_info.number_iteration = value_cycles
                temp_note_info.type_error_work = self._error_control
                temp_note_info.current_speed_tech_channel = self._required_br

                # останавливаем поток с очередью полинга Puts
                puts_queue.put(True)
                temp_thread.join()

                # заполнение целевых структур, при разборе целевых переменных
                self.process_info_container(temp_note_info)

                # учитываем суммарную ошибку (работает с числовыми данными так как ошибки суммируются)
                temp_note_info.sum_error = temp_note_info.channel_1.flag_error | temp_note_info.channel_2.flag_error
                self._list_data_store.append(temp_note_info)

                # выводим информацию о тесте
                self.print_info(test[0])
                self.print_data_into_log(temp_note_info)

                value_local_error += temp_note_info.sum_error

                # контроль управления по ошибкам
                self.error_control_method(self.value_error + value_local_error)

                # перенос счетчика циклов из локальной переменной в классовую
                self._counter_cycle_limit = temp_counter

                # чистим результаты тестов
                self.personal_data_channel = [[], []]

                # кусок кода вызываемый сразу после завершения теста
                # if self.code_after_end_test is not None:
                #     self.code_after_end_test(self)

                flag_print_data = True  # Реагировать на все ошибки

                # кусок кода вызываемый сразу после завершения теста
                if self.code_after_end_test is not None:
                    self.code_after_end_test(self, flag_print_data)


            self.value_error += value_local_error

            # отчет за цикл
            if value_local_error:
                print(u"<Ошибка> Ошибок за цикл {}: {}.".format(value_cycles, value_local_error))
            else:
                print(u"Цикл {} прошел без ошибок.".format(value_cycles))

            # отчет по всему тестированию
            if self.value_error:
                print(u"<Error> При тестировании обнаружены ошибки в кол-ве {}".format(self.value_error))

            self.close_channels()

            romka = RomAnalyzerClass.RomAnalyzer(cur_time,
                                                 sector_number=test[1][2],
                                                 bool_fast_analyze=test[1][3],
                                                 value_cycles=value_cycles - erase_start_cycle)
            erase_stage, zeros_stage = True, True

            if not zeros_stage:
                if romka.analyze_states() == 0x00:
                    zeros_stage = True
            elif not erase_stage and romka.analyze_states(zeros_stage) == 0x00:
                erase_stage = True
                erase_start_cycle = value_cycles
                romka.cycle = 0

            if erase_stage:
                if romka.analyze(self.test_return_data == 0xFFFFFFFF):
                    self._exit_flag = True

            romka.close_analyzer()

        romka = RomAnalyzerClass.RomAnalyzer(cur_time,
                                             sector_number=test[1][2],
                                             bool_fast_analyze=test[1][3])
        romka.create_graphics()
        romka.close_analyzer()

        self._counter_cycle_limit = 0
        # self._test_end_flag = True
        self._end_method()
        control_cycle_thread.join()
# ----------------------------------------------------------------------------------------------------------------------

    def _end_method(self):
        self.control_queue.put({"Name": self._special_tag, "Message": "Exit"})
        if isinstance(self._answer_queue, Queue.Queue) is True:
            temp_dict = {"Name": self._special_tag, "Message": True}
            self._answer_queue.put(dict(temp_dict))
# ----------------------------------------------------------------------------------------------------------------------

    # метод свертка кода обработки информации после завершения теста
    def process_info_container(self, temp_note_info):

        ref_ch1 = {"data_ref": self.personal_data_channel[0],
                   "result_ref": temp_note_info.channel_1,
                   "interface_ref": self._interface_channel_1}
        ref_ch2 = {"data_ref": self.personal_data_channel[1],
                   "result_ref": temp_note_info.channel_2,
                   "interface_ref": self._interface_channel_2}
        full_ref = [ref_ch1, ref_ch2]

        # if self._interface_channel_1 is not None:
        for local_item in full_ref:
            temp_string = u""

            if local_item["interface_ref"] is None:
                local_item["result_ref"].any_cond = temp_string
                local_item["result_ref"].flag_error = 0
                local_item["result_ref"].error_type = shortClasses.ErrorContainer(False, "Debug", None, None, None)
                # local_item["result_ref"].string_after_test = None
            else:
                for data_cell in local_item["data_ref"]:
                    if isinstance(data_cell, shortClasses.ErrorContainer) is False:
                        temp_string += data_cell
                    else:
                        temp_error = int(data_cell.error) | (data_cell.type_message != "Summary")
                        local_item["result_ref"].flag_error = temp_error
                        local_item["result_ref"].any_cond = temp_string
                        local_item["result_ref"].error_type = data_cell
                        local_item["result_ref"].string_after_test = data_cell.description
# ----------------------------------------------------------------------------------------------------------------------

    # метод управления циклом через количество ошибок
    def error_control_method(self, value_error):

        # если self._error_control == "Ignore"
        if self._error_control == self.ErrorControl_K[0]:
            self._exit_flag = self._exit_flag
        else:
            # если self._error_control == "FirstError"
            if self._error_control == self.ErrorControl_K[1]:
                if value_error > 0:
                    self._exit_flag = True
            else:
                # если self._error_control == "LimitError"
                if self._error_control == self.ErrorControl_K[2]:
                    if value_error >= self._value_error:
                        self._exit_flag = True
# ----------------------------------------------------------------------------------------------------------------------

    def _print_puts_string(self, name_ch1, name_ch2, queue):
        # обнуляем данные при начале следующего теста
        self.personal_data_channel = [[], []]
        local_flag_end = False
        if isinstance(queue, Queue.Queue):
            while local_flag_end is False:
                temp_data = queue.get()

                if type(temp_data) == bool:
                    local_flag_end = temp_data
                    # если первый элемент в очереди не кластер с данными, отсекаем в консоли Puts
                    # 0 элемнт это остатки от загрузки теста
                    condition = (len(self.personal_data_channel[0]) > 1) or (len(self.personal_data_channel[1]) > 1)
                    if condition is True:
                        print(u"")
                    if local_flag_end is True:
                        break
                else:
                    # перебрасываем данные из очереди в персональные переменные
                    if temp_data[0] == name_ch1:
                        self.personal_data_channel[0].append(temp_data[1])

                    if temp_data[0] == name_ch2:
                        self.personal_data_channel[1].append(temp_data[1])

                    temp_short_string = u""
                    if isinstance(temp_data[1], shortClasses.ErrorContainer) is False:
                        temp_short_string = temp_data[1]
                    print(u"<tmp>" + temp_short_string, end=u'')
# ----------------------------------------------------------------------------------------------------------------------

    def print_info(self, test_name):

        # получаем список данных по конкретному тесту
        list_data_to_type = noteInfo.data_filter(self._list_data_store, [["name_test", test_name]])

        # если измерений нет, пропускаем обработку
        value_measurement = len(list_data_to_type)
        if value_measurement == 0:
            return u""

        # получаем готовую строку по тесту
        value_errors_type = len(noteInfo.data_filter(list_data_to_type, [["sum_error", True]]))
        # print(u" Тест: {}(Ошибок: {} из прогонов: {});".format(test_name, value_errors_type, value_measurement))
        print(u"(Ошибок {} из {});".format(value_errors_type, value_measurement))
# ----------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def print_data_into_log(cell_info):

        temp_string_ch1 = u""
        temp_string_ch2 = u""
        for item in cell_info.channel_1.error_type.get_full_string_error():
            temp_string_ch1 += item
        for item in cell_info.channel_2.error_type.get_full_string_error():
            temp_string_ch2 += item

        array_data = [{"string_name": u"current_time", "data": cell_info.current_time},
                      {"string_name": u"name_test", "data": cell_info.name_test},
                      {"string_name": u"number_iteration", "data": cell_info.number_iteration},
                      {"string_name": u"type_error_work", "data": cell_info.type_error_work},
                      {"string_name": u"current_speed_tech_channel", "data": cell_info.current_speed_tech_channel},
                      {"string_name": u"any_cond_ch1", "data": cell_info.channel_1.any_cond},
                      {"string_name": u"any_cond_ch2", "data": cell_info.channel_2.any_cond},
                      {"string_name": u"time_load_ch1", "data": cell_info.channel_1.time_load},
                      {"string_name": u"time_load_ch2", "data": cell_info.channel_2.time_load},
                      {"string_name": u"time_process_ch1", "data": cell_info.channel_1.time_process},
                      {"string_name": u"time_process_ch2", "data": cell_info.channel_2.time_process},
                      {"string_name": u"string_after_test_ch1", "data": cell_info.channel_1.string_after_test},
                      {"string_name": u"string_after_test_ch2", "data": cell_info.channel_2.string_after_test},
                      {"string_name": u"flag_error_ch1", "data": cell_info.channel_1.flag_error},
                      {"string_name": u"flag_error_ch2", "data": cell_info.channel_2.flag_error},
                      {"string_name": u"error_type_ch1", "data": temp_string_ch1},
                      {"string_name": u"error_type_ch2", "data": temp_string_ch2},
                      {"string_name": u"sum_error", "data": cell_info.sum_error}]

        temp_string = u"<Log>"
        for item in array_data:
            temp_string += u"\t {}: {};\n".format(item["string_name"], item["data"])
        print(temp_string)
# ----------------------------------------------------------------------------------------------------------------------

    # метод подсчета ошибок
    @staticmethod
    def error_check(channel_data):

        # событие аппаратной ошибки
        event_error_1 = channel_data.error is True

        # событие программной ошибки ГВМ
        event_error_2 = False
        temp_variable = channel_data.get_string_error()
        for data in temp_variable:
            # поиск ошибок в канале
            event_error_2 = (data.find(u"Тест прошел успешно") < 0) and (data.find(u"Код ошибки: 0x00000000") < 0)
            if event_error_2 is True:
                break
        # True соответствует наличию ошибки
        return event_error_1 or event_error_2
