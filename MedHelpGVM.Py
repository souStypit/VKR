# -*- coding:utf-8 -*-

import os
import Queue
import datetime
import argparse
import threading
import sourceMedHelpGVM
try:
    import kbhit
except ImportError:
    from utils_work.kbhit import kbhit
try:
    import logger
except ImportError:
    from utils_work.Logger import logger
try:
    import shortClasses
except ImportError:
    from tech_work.TechChannel import shortClasses

# -----------------------------------------------------------------------------------------------------------
Command_K = ({"Exit": "e",
              "Pause": "p",
              "Continue": "c",
              "Help": "h",
              "Quit": "q",
              "Stop": "s"})
# -----------------------------------------------------------------------------------------------------------


# сообщение помощи
def local_help():
    temp_string = u"Команды для управления процессом тестирования:\n"
    temp_string += u"{} или {} - завершение программы\n".format(Command_K["Exit"], Command_K["Quit"])
    # temp_string += u"{} - пауза тестов\n".format(Command_K["Pause"])
    # temp_string += u"{} - продолжение тестов\n".format(Command_K["Continue"])
    temp_string += u"{} - вывод данной подсказки\n".format(Command_K["Help"])
    temp_string += u"{} - завершение тестирования по окончанию цикла\n".format(Command_K["Stop"])
    print temp_string
# -----------------------------------------------------------------------------------------------------------


# настройка argparse
def setup_arg_parse(arg_parse_object):

    arg_parse_object.add_argument('-c', '--config',
                                  type=str,
                                  default="default_setting",
                                  dest=u'config',
                                  help=u'Подключаемый конфигурационный файл')

    arg_parse_object.add_argument('-n', '--numberVM',
                                  type=int,
                                  default=None,
                                  dest=u'number_VM',
                                  help=u'Номер ВМ для консольного запуска')

    # arg_parse_object.add_argument('-tg', '--target',
    #                               type=int,
    #                               default="All",
    #                               dest=u'target',
    #                               help=u'Номер ВМ для консольного запуска ("First", "Second", "All")')

    arg_parse_object.add_argument('-s', '--speed',
                                  type=int,
                                  default=None,
                                  dest=u'speed',
                                  help=u'Скорость портов для консольного запуска')

    arg_parse_object.add_argument('-t', '--test',
                                  type=str,
                                  default="",
                                  dest=u'run_file',
                                  help=u'Файл исполнения для консольного запуска')

    arg_parse_object.add_argument('-v', '--variable',
                                  type=int,
                                  default=None,
                                  dest=u'variable',
                                  help=u'Номер стандартного теста для ПСИ')

    arg_parse_object.add_argument('-vc', '--valueCycles',
                                  type=int,
                                  default=None,
                                  dest=u'value_cycles',
                                  help=u'число циклов для выполнения задачи (меньше 0 бесконечное выполнение)')

    arg_parse_object.add_argument('-p1', '--parameter_1',
                                  type=str,
                                  default="0",
                                  dest=u'param_1',
                                  help=u'параметр 1 для запуска ран файла или запуска по адресу')

    arg_parse_object.add_argument('-p2', '--parameter_2',
                                  type=str,
                                  default="0",
                                  dest=u'param_2',
                                  help=u'параметр 2 для запуска ран файла или запуска по адресу')

    arg_parse_object.add_argument('-p3', '--parameter_3',
                                  type=str,
                                  default="0",
                                  dest=u'param_3',
                                  help=u'параметр 3 для запуска ран файла или запуска по адресу')

    arg_parse_object.add_argument('-p4', '--parameter_4',
                                  type=str,
                                  default="0",
                                  dest=u'param_4',
                                  help=u'параметр 4 для запуска ран файла или запуска по адресу')

    arg_parse_object.add_argument('-pc', '--path_to_catalog',
                                  type=str,
                                  default="",
                                  dest=u'path_catalog',
                                  help=u'путь к каталогу где находятся файлы загрузки')

    arg_parse_object.add_argument('-com1', '--com_port1',
                                  type=str,
                                  default=None,
                                  dest=u'com_port1',
                                  help=u'Номер первого com port')

    arg_parse_object.add_argument('-com2', '--com_port2',
                                  type=str,
                                  default=None,
                                  dest=u'com_port2',
                                  help=u'Номер второго com port')
# -----------------------------------------------------------------------------------------------------------


# метод в котором в основной класс загружаются параметры
def processor_load_parameters(prime_thread, input_data):
    # parameters = __import__("setting")
    parameters = __import__(input_data.config)
    # additional_code = __import__("additional_code")
    additional_code = __import__("test_pre_post_processing")
    flag_find = False

    prime_thread.code_between_write_and_start_code = additional_code.code_between_write_and_start_code
    prime_thread.code_after_end_test = additional_code.code_after_end_test

    # добавление задач
    if input_data.run_file != "":
        temp_task = None

        # обработка стандартного теста
        if input_data.run_file.find(u"PSI") >= 0:
            if input_data.variable is None:
                print u"Не задан номер теста ПСИ"
                shortClasses.exit_method()
            if len(parameters.Test_K) <= input_data.variable:
                print u"Теста №{} в списке ПСИ нет".format(input_data.variable)
                shortClasses.exit_method()
            temp_task = parameters.Test_K[input_data.variable]
            flag_find = True

        # Обработка теста из ПЗУ
        if (input_data.run_file.find(u"0x") >= 0) and (flag_find is False):
            temp_task = (u"Консольный запуск теста", (int(input_data.run_file, 16), input_data.param_1))
            flag_find = True

        # Обработка Run файла
        if (input_data.run_file.find(u".run") > 0) and (flag_find is False):
            temp_task = (u"Консольный запуск теста", input_data.run_file)
            flag_find = True

        if flag_find is False:
            print u"Не правильно задан параметр для теста \"{}\"".format(input_data.run_file)
            shortClasses.exit_method()
        else:
            prime_thread.add_task(data_add_task=temp_task)
    else:
        prime_thread.add_task(data_add_task=parameters.Test_K)

    # загрузка параметров запуска загружаемых тестов и тестов из флеш памяти в класс
    temp_param = []
    temp_ref = [input_data.param_1, input_data.param_2, input_data.param_3, input_data.param_4]
    for data in temp_ref:
        if data.find("0x") is True:
            temp_param.append(long(data, 16))
        else:
            temp_param.append(long(data))

    # print ("temp_param = {}".format(temp_param))
    prime_thread.set_parameters(temp_param[0], temp_param[1], temp_param[2], temp_param[3])

    # # открытие лога
    # prime_thread.create_and_open_log()

    # загрузка конфигурационного скрипта
    prime_thread.set_error_control(parameters.error_control, parameters.value_error)

    # Загрузка ВМ
    if input_data.number_VM is not None:
        if (input_data.number_VM > 2) or (input_data.number_VM < 0):
            print u"указан не правильно номер ВМ {}".format(input_data.number_VM)
            shortClasses.exit_method()

        if input_data.number_VM == 0:
            prime_thread.set_target("First")
        else:
            if input_data.number_VM == 1:
                prime_thread.set_target("Second")
            else:
                prime_thread.set_target("All")
    else:
        prime_thread.set_target(parameters.target)

    # загрузка параметров лога
    # prime_thread.set_type_output(parameters.type_output)

    # загрузка попаметров циклирования теста
    if input_data.value_cycles is None:
        prime_thread.set_type_inf_cycle(parameters.value)
    else:
        prime_thread.set_type_inf_cycle(input_data.value_cycles)

    # загрузка рекомендуемой скорости работы портов
    if input_data.speed is None:
        prime_thread.set_required_br(parameters.required_baud_rate)
    else:
        prime_thread.set_required_br(input_data.speed)

    if input_data.path_catalog == "":
        prime_thread.info_about_gvm["pathToFiles"] = input_data.path_catalog
    else:
        prime_thread.info_about_gvm["pathToFiles"] = input_data.path_catalog + os.sep
    print(prime_thread.info_about_gvm["pathToFiles"])

    # установка ком портов
    try:
        vm0_com = parameters.VM0_com
    except AttributeError:
        vm0_com = None
    try:
        vm1_com = parameters.VM1_com
    except AttributeError:
        vm1_com = None

    if input_data.com_port1 is not None:
        vm0_com = input_data.com_port1
    if input_data.com_port2 is not None:
        vm1_com = input_data.com_port2

    prime_thread.set_com_channel(vm0_com, vm1_com)

    return flag_find
# ----------------------------------------------------------------------------------------------------------------------


def get_path_logger_file(script_name):

    # проверкак каталога логов
    catalog = u"Logs"

    if not os.path.exists(catalog):
        os.mkdir(catalog)

    # создаем экземпляр логгера
    start_sys_time = datetime.datetime.now()  # Получить текущее время

    # Получить название текущего скрипта без .py на конце # имя файла лога
    temp_file_name = os.path.basename(script_name).replace(".py", "")
    logger_file_name = u"{}_{}.log".format(temp_file_name, start_sys_time.strftime("%Y_%m_%d_%H_%M_%S"))

    return {"path": catalog + os.sep + logger_file_name, "time": start_sys_time}
# ----------------------------------------------------------------------------------------------------------------------


def prime_cycle():
    parser = argparse.ArgumentParser()

    # загрузка данных о параметрах в модуль argparse
    setup_arg_parse(arg_parse_object=parser)

    data_input = parser.parse_args()

    # создание рабочего класса
    prime_work_thread = sourceMedHelpGVM.WorkThread()
    # prime_work_thread.set_target(target=prime_work_thread.SelCom_K[1])
    # prime_work_thread.set_com_channel('COM3', None)

    # процесс загрузки параметров в класс
    auto_end_local = processor_load_parameters(prime_work_thread, data_input)
    if auto_end_local is False:
        local_help()

    # запуск задачи в потоке
    thread_work = threading.Thread(target=prime_work_thread.start_process)
    thread_work.start()

    # создаем обработчик вводимых данных, подключаем очередь для данных, получаем тэг процесса
    thread_input = kbhit.BufferKBHit()

    # создаем связь управления между потоками
    control_queue = Queue.Queue()
    tag_prime = prime_work_thread.get_special_tag()
    tag_input = thread_input.get_special_tag()
    prime_work_thread.set_queue(control_queue)
    thread_input.set_queue(control_queue)

    # print(u"Для управления процессом тестирования введите команду и нажмите \"Enter\"")

    flag_exit = False
    while flag_exit is False:

        # ожидаем события
        temp_data = control_queue.get()
        # отрабатываем ввод с клавиатуры
        if temp_data["Name"] == tag_input:
            command_string = temp_data["Message"]
            if len(command_string) == 0:
                continue

            # немедленное завершение тестирования
            if (command_string.find(Command_K["Exit"]) >= 0) or (command_string.find(Command_K["Quit"]) >= 0):
                flag_exit = True
                prime_work_thread.control_queue.put({"Name": tag_prime, "Message": "Exit"})

            # строка помощи
            elif command_string.find(Command_K["Help"]) >= 0:
                local_help()

            # завершение тестирования по завершению тестов в цикле
            elif command_string.find(Command_K["Stop"]) >= 0:
                flag_exit = True
                prime_work_thread.control_queue.put({"Name": tag_prime, "Message": "Stop"})
            else:
                print(u"Команда не допустима: {}".format(command_string))
        # отрабатываем завершение из главного теста
        elif temp_data["Name"] == tag_prime:
            if temp_data["Message"] is True:
                flag_exit = True
        else:
            pass

        # завершаем потоки и дожидаемся их завершения
    thread_input.controlQueue.put({"Name": tag_input, "Message": True})
    thread_work.join()

    while True:
        temp_data = control_queue.get()
        if temp_data["Name"] == tag_input:
            if type(temp_data["Message"]) == bool:
                if temp_data["Message"] is True:
                    break

    thread_work.join()

    return prime_work_thread.value_error
# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":

    # создание объекта логгера
    temp = get_path_logger_file(__file__)
    logger_instance = logger.Logger(temp["path"])

    error = prime_cycle()

    logger_instance.closeLogger()
    # return error
# -----------------------------------------------------------------------------------------------------------
