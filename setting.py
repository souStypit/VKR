# -*- coding:utf-8 -*-

# None - ничего не выбрано программа завершится сразу,
# "First" - только ВМ 0,
# "Second" - только ВМ 1,
# "All" - оба ВМ
# target = "First"
# target = "Second"
target = "First"

# VM0_com = "COM3"
# VM1_com = "COM2"

# число циклов (< 0 бесконечное выполнение)
value = -1
init_sus = 0x47e00
sector_number = 30
fast_analyze = False

# "Short", "Long" - вывод ошибок и уведомлений (не реализовано)
type_output = "Long"
Test_K = (
    (u"Тест ПЗУ", (r"TestProg_0x30.run", init_sus, sector_number, fast_analyze))
)

# 9600, 14400, 19200, 38400, 57600, 115200 - список доступных скоростей
required_baud_rate = 57600

# "Ignore" - игнорировать учет ошибок,
# "FirstError" - завершение по первой ошибке,
# "LimitError" - завершение по определенному кол-ву ошибок, заданному в value_error
error_control = "Ignore"
value_error = 0
