import numpy
import num2words
import datetime
import decimal
import locale

import traceback

locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))


def rgb2hex(r: int, g: int, b: int) -> str:
    """
    Функция преобразования палитры RGB в шестнадцатеричное число
    @param r: int, красный цвет от 0 о 255
    @param g: int, зеленый цвет от 0 о 255
    @param b: int, синий цвет от 0 о 255
    @return: str шестнадцатеричное число RRGGBB
    """
    if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
        raise ValueError("Ошибка!!! Значения параметров должно быть в диапазоне от 0 до 255")
    else:
        return f"{r:02X}{g:02X}{b:02X}"


def hex2rgb(hexp):
    """
    Функция преобразования в шестнадцатеричного числа в палитру RGB
    @param hex: str шестнадцатеричное число RRGGBB
    @param
    @return коржеж (r: int красный цвет от 0 о 255, g: int, зеленый цвет от 0 о 255, b: int, синий цвет от 0 о 255)
    """
    h = list(hexp.lower())
    if (all(x in '0123456789abcdef' for x in h)) and len(h) == 6:
        return tuple(int(hexp[i:i + 2], 16) for i in (0, 2, 4))
    else:
        raise ValueError("Ошибка!!! Должно быть 6 символов от 0 до F")


def print_exception(err):
    exc_type, _, exc_tb = sys.exc_info()
    fname = traceback.extract_tb(exc_tb)[-1].filename
    line = traceback.extract_tb(exc_tb)[-1].lineno
    print(err)
    print(f"Тип исключения: {exc_type.__name__}")
    print(f"Имя файла: {fname}")
    print(f"Номер строки: {line}")


def num2ordinal(num, sex="y"):
    """
    Возвращает порядковое числительное.
    Параметры: num - целое число.
    sex – род('f' - женский, 'm' – мужской, 'n' – средний, 'y' – для дня в дате). Значение по умолчанию 'y'
    Примеры:
    num2ordinal(1, "f") ->'первая'
    num2ordinal(1, "m") ->'первый'
    num2ordinal(1, "n") ->'первое'
    num2ordinal(1, "y") ->'первого'
    """
    if sex == "m":
        return num2words.num2words(num, to='ordinal', lang="ru")
    elif sex == "f":
        return num2words.num2words(num, to='ordinal', lang="ru").replace("ый", "ая").replace("ий", "ья").replace("ой",
                                                                                                                 "ая")
    elif sex == "n":
        return num2words.num2words(num, to='ordinal', lang="ru").replace("ый", "ое").replace("ий", "ье").replace("ой",
                                                                                                                 "ое")
    elif sex == "y":
        return num2words.num2words(num, to='ordinal', lang="ru").replace("ый", "ого").replace("ий", "ьего").replace(
            "ой", "ого")
    return None


def AddDescription(num: int, lstDescp):
    """
    Возвращает существительное в зависимости от числительного.
    Параметры: num - целое число,
    lstDescp - список существительных (например минута, минуты, минут).
    """

    mod100 = num % 100
    mod10 = num % 10
    if 10 < mod100 < 20 or mod10 == 0 or mod10 > 4:
        return str(num) + " " + lstDescp[2]
    elif mod10 == 1:
        return str(num) + " " + lstDescp[0]
    else:
        return str(num) + " " + lstDescp[1]


def Addunist(num: int, main_units=((u'', u'', u''), 'm'), derive_number=True):
    """
    Возвращает существительное в зависимости от числительного.
    main_units - кортеж ((u'x1', u'x2', u'x3'), 's') где x1,x2,x3 – существительные (например, метр, метра, метров),
    s – род ('f' - женский, 'm' – мужской (по умолчанию), 'n' – средний).
    """
    numabs = abs(num)
    mod100 = numabs % 100
    mod10 = numabs % 10
    number = (str(num) + " " if derive_number else "")
    if 10 < mod100 < 20 or mod10 == 0 or mod10 > 4:
        return number + main_units[0][2]
    elif mod10 == 1:
        return number + main_units[0][0]
    else:
        return number + main_units[0][1]


units = (
    u'ноль',

    (u'один', u'одна', u'одно'),
    (u'два', u'две', u'два'),

    u'три', u'четыре', u'пять',
    u'шесть', u'семь', u'восемь', u'девять'
)

teens = (
    u'десять', u'одиннадцать',
    u'двенадцать', u'тринадцать',
    u'четырнадцать', u'пятнадцать',
    u'шестнадцать', u'семнадцать',
    u'восемнадцать', u'девятнадцать'
)

tens = (
    teens,
    u'двадцать', u'тридцать',
    u'сорок', u'пятьдесят',
    u'шестьдесят', u'семьдесят',
    u'восемьдесят', u'девяносто'
)

hundreds = (
    u'сто', u'двести',
    u'триста', u'четыреста',
    u'пятьсот', u'шестьсот',
    u'семьсот', u'восемьсот',
    u'девятьсот'
)

orders = (  # plural forms and gender
    # ((u'', u'', u''), 'm'), # ((u'рубль', u'рубля', u'рублей'), 'm'), # ((u'копейка', u'копейки', u'копеек'), 'f')
    ((u'тысяча', u'тысячи', u'тысяч'), 'f'),
    ((u'миллион', u'миллиона', u'миллионов'), 'm'),
    ((u'миллиард', u'миллиарда', u'миллиардов'), 'm'),
    ((u'триллион', u'триллиона', u'триллионов'), 'm'),
)

minus = u'минус'


def thousand(rest, sex):
    """Converts numbers from 19 to 999"""
    prev = 0
    plural = 2
    name = []
    use_teens = 10 <= rest % 100 <= 19
    if not use_teens:
        data = ((units, 10), (tens, 100), (hundreds, 1000))
    else:
        data = ((teens, 10), (hundreds, 1000))
    for names, x in data:
        cur = int(((rest - prev) % x) * 10 / x)
        prev = rest % x
        if x == 10 and use_teens:
            plural = 2
            name.append(teens[cur])
        elif cur == 0:
            continue
        elif x == 10:
            name_ = names[cur]
            if isinstance(name_, tuple):
                name_ = name_[0 if sex == 'm' else (1 if sex == "f" else 2)]
            name.append(name_)
            if 2 <= cur <= 4:
                plural = 1
            elif cur == 1:
                plural = 0
            else:
                plural = 2
        else:
            name.append(names[cur - 1])
    return plural, name


def num2text(num, main_units=((u'', u'', u''), 'm'), isChar=True):
    """
    Возвращает сумму прописью с существительным (например, один метр).
    Параметры:
    num - целое число.
    main_units - кортеж ((u'x1', u'x2', u'x3'), 's') где x1,x2,x3 – существительные (например, метр, метра, метров),
    s – род ('f' - женский, 'm' – мужской (по умолчанию), 'n' – средний).
    """
    if isChar:
        _orders = (main_units,) + orders
        if num == 0:
            return ' '.join((units[0], _orders[0][0][2])).strip()  # ноль

        rest = abs(num)
        order = 0
        name = []
        while rest > 0:
            plural, nme = thousand(rest % 1000, _orders[order][1])
            if nme or order == 0:
                name.append(_orders[order][0][plural])
            name += nme
            rest = int(rest / 1000)
            order += 1
        if num < 0:
            name.append(minus)
        name.reverse()
        return ' '.join(name).strip()
    else:
        return Addunist(num, main_units)


def decimal2text(value, int_units=(('', '', ''), 's'),
                 exp_units=(('', '', ''), 's'), places=2, isChar=True):
    """
    Возвращает сумму прописью с дробной частью c существительным (например, один рубль две копейки, если isChar= True
    или 1 рубль 2 копейки, если isChar= False).
    Параметры:
    value – число может быть с дробной частью
    int_units - кортеж ((u'x1', u'x2', u'x3'), 'm') где x1,x2,x3 – существительные для целой части (например, рубль, рубля, рублей),
        s – род ('f' - женский, 'm' – мужской (по умолчанию), 'n' – средний).
    exp_units - кортеж ((u'x1', u'x2', u'x3'), 'm') где x1,x2,x3 – существительные для дробной части (например, копейка, копейки, копеек),
        s – род ('f' - женский, 'm' – мужской (по умолчанию), 'n' – средний).
    places – количество разрядов дробной части, по умолчанию 2
    isChar – если True, то возвращать сумму прописью, иначе цифрами, по умолчанию True
    """

    value = decimal.Decimal(value)
    q = decimal.Decimal(10) ** -places

    integral, exp = str(value.quantize(q)).split('.')
    return u'{} {}'.format(
        num2text(int(integral), int_units, isChar),
        num2text(int(exp), exp_units, isChar))


def decimal2textfloat(value, main_units=(('', '', ''), 'm'),
                      places=0, isChar=True):
    """
    Возвращает сумму прописью с дробной частью c существительным (например, один и пять десятых градуса или два градуса, если isChar= True
    или 1.5 десятых градуса или 2 градуса, если isChar= False).
    Параметры:
    value – число может быть с дробной частью
    main_units - кортеж ((u'x1', u'x2', u'x3'), 's') где x1,x2,x3 – существительные (например, метр, метра, метров),
    s – род ('f' - женский, 'm' – мужской (по умолчанию), 'n' – средний).
    places – количество разрядов дробной части, по умолчанию 0,
    isChar – если True, то возвращать сумму прописью, иначе цифрами, по умолчанию True
    """
    exp = integral = 0
    int_units = (('целая', 'целые', 'целых'), 'f')
    float_uints = ((('десятая', 'десятые', 'десятых'), 'f'),
                   (('сотая', 'сотые', 'сотых'), 'f'),
                   (('тысячная', 'тысячные', 'тысячных'), 'f'),
                   (('десятитысячная', 'десятитысячные', 'десятитысячных'), 'f'),
                   (('стотысячная', 'стотысячные', 'стотысячных'), 'f'),
                   (('миллионная', 'миллионные', 'миллионных'), 'f'),
                   (('десятимиллионная', 'десятимиллионные', 'десятимиллионных'), 'f'),
                   (('стомиллионная', 'стомиллионные', 'стомиллионных'), 'f'),
                   (('миллиардная', 'миллиардные', 'миллиардных'), 'f'),
                   (('десятимиллиардная', 'десятимиллиардные', 'десятимиллиардных'), 'f'),
                   (('стомиллиардная', 'стомиллиардные', 'стомиллиардных'), 'f'),
                   (('триллионная', 'триллионные', 'триллионных'), 'f'),
                   (('десятитриллионная', 'десятитриллионные', 'десятитриллионных'), 'f'),
                   (('стотриллионная', 'стотриллионные', 'стотриллионных'), 'f'),
                   )
    values = numpy.format_float_positional(round(value, 14), trim='-')
    # print(f"{values=}")
    # values="{:.14f}".format(round(value,14))
    if len(values) > 1:
        values = values.rstrip("0")
    # print(f"{values=}")
    places = min(places, 14)
    if '.' in values:
        integral, exp = values.split('.')
        if exp:
            if int(exp) == 0:
                values = integral
    if '.' in values:
        # print(".")
        if isChar:
            len_float = len(exp) - 1
            # print(f"{places=} {len(exp)=}")
            sign = 'минус ' if value < 0 and abs(int(integral)) < 1 else ""  # если число отрицательное
            # и меньше 1 по абсолютной величине, то добавляем минус
            # если число отрицательное и не меньше 1 по абсолютной величине, то минус
            # возвратит функция num2text()
            if places > len(exp):
                add_f = places - len(exp)
                len_float = places - 1
                # print("places > len(exp)")
                return sign + num2text(int(integral), int_units) + " " + num2text(int(exp) * 10 ** add_f,
                                                                                  main_units=float_uints[
                                                                                      len_float]) + " " + \
                    main_units[0][1]
            else:
                # print("else places > len(exp)")
                return sign + num2text(int(integral), int_units) + " " + num2text(int(exp),
                                                                                  main_units=float_uints[
                                                                                      len_float]) + " " + \
                    main_units[0][1]
        else:
            # print("else isChar")
            return values + " " + main_units[0][1]
    else:
        integral = values
        # print("else .", f"{integral=}")
        return num2text(int(integral), main_units, isChar)


def duration(start_time, end_time):
    # Рассчитываем продолжительность дня путем вычитания времени окончания от времени начала
    try:
        start_datetime = datetime.datetime.strptime(start_time, "%H:%M")
        end_datetime = datetime.datetime.strptime(end_time, "%H:%M")
        value = end_datetime - start_datetime
        if end_datetime < start_datetime:
            value = value + datetime.timedelta(hours=24)
    except(Exception,):
        print("Ошибка в параметрах. Начальная и конечная даты должны иметь вид ЧЧ:ММ в текстовом формате!")
        start_datetime = datetime.datetime.strptime("00:00", "%H:%M")
        end_datetime = datetime.datetime.strptime("00:00", "%H:%M")
        value = end_datetime - start_datetime
    # Выводим продолжительность дня в формате HH:MM
    return value


def tohex(decimal_number, len_hex=0):
    """
    Преобразовывает целое число в шестнадцатеричное
    Параметры:
    decimal_number – число для преобразования
    len_hex – длина шестнадцатеричного числа, по умолчанию 0.
    Если len_hex больше длины шестнадцатеричного числа, то оно дополняется слева пробелами,
    так чтобы длина стала равной len_hex
    """

    hexadecimal_digits = "0123456789ABCDEF"  # Строка с шестнадцатеричными цифрами
    hexadecimal_number = ""

    while decimal_number > 0:
        remainder = decimal_number % 16  # Получаем остаток от деления на 16
        hexadecimal_digit = hexadecimal_digits[remainder]  # Получаем шестнадцатеричную цифру
        hexadecimal_number = hexadecimal_digit + hexadecimal_number  # Добавляем цифру в начало шестнадцатеричного числа
        decimal_number //= 16  # Выполняем целочисленное деление на 16
    if len_hex > 0:
        hexadecimal_number = hexadecimal_number.zfill(len_hex)
    return hexadecimal_number


def find_first(strzad, strcmd):
    # Смотрим strzad начинается с strcmd,
    # если да, то возращаем par
    par = ""
    ln = len(strcmd)
    if 0 < ln < len(strzad):
        zadl = strzad[0:ln]
        if zadl == strcmd:
            par = strzad[ln:].lstrip()
    return par


def date_to_str(dt, date_format="", tyear="года"):
    """
    Возвращает дату в виде ДД ММ ГГ.
    ДД - день число (одна или две цифры) или прописью
    ММ - месяц прописью
    ГГ - год число или прописью
    Параметры: dt - дата.
    format - формат:
    по умолчанию пусто: ДД и ГГ число;
    D - ДД прописью;
    Y - ГГ прописью;
    DY, YD - ДД и ГГ прописью;
    NY -  нет года, tyear = ''
    tyear - текст после даты года:
    по умолчанию 'года', для отмены вывода - ''
    """
    dtstrp = ""
    dtstr_d = datetime.datetime.strftime(dt, '%d').lstrip('0')
    dtstr_m = datetime.datetime.strftime(dt, '%B').lower()
    dtstr_y = datetime.datetime.strftime(dt, '%Y').lower()
    dtstr_m = dtstr_m.replace('рь', 'ря').replace('ль', 'ля').replace('рт', 'рта').replace('ай', 'ая').replace('нь',
                                                                                                               'ня').replace(
        'ст', 'ста')
    if date_format == '':
        dtstrp = dtstr_d + " " + dtstr_m + " " + dtstr_y
    elif date_format == 'D':
        dtstrp = num2ordinal(int(dtstr_d)) + " " + dtstr_m + " " + dtstr_y
    elif date_format == 'Y':
        dtstrp = dtstr_d + " " + dtstr_m + " " + num2ordinal(int(dtstr_y))
    elif date_format == 'NY':
        dtstrp = dtstr_d + " " + dtstr_m
        tyear = ""
    elif date_format == 'DY' or date_format == 'YD':
        dtstrp = num2ordinal(int(dtstr_d)) + " " + dtstr_m + " " + num2ordinal(int(dtstr_y))
    if tyear:
        dtstrp = dtstrp + " " + tyear
    return dtstrp


def weekday_ru(nom_day):
    str_day = ("понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье")
    return str_day[nom_day]


def word2num(string, sex='m'):
    """
    Возвращает число цифрами на основе числа прописью
    Параметры:
    string - числ прописью.
    sex – род ('f' - женский, 'm' – мужской, 'n' – средний), по умолчанию m.
    Если обнаружена ошибка, то возвращается чило -999999999999999 15-ть девяток с минусом
    """

    numbers = {"ноль": "0",
               "один": "1", "одна": "1", "одно": "1",
               "два": "2", "две": "2",
               "три": "3",
               "четыре": "4",
               "пять": "5",
               "шесть": "6",
               "семь": "7",
               "восемь": "8",
               "девять": "9",
               "десять": "10",
               "одиннадцать": "11",
               "двенадцать": "12",
               "тринадцать": "13",
               "четырнадцать": "14",
               "пятнадцать": "15",
               "шестнадцать": "16",
               "семнадцать": "17",
               "восемнадцать": "18",
               "девятнадцать": "19",
               "двадцать": "20",
               "тридцать": "30",
               "сорок": "40",
               "пятьдесят": "50",
               "шестьдесят": "60",
               "семьдесят": "70",
               "восемьдесят": "80",
               "девяносто": "90",
               "сто": "100",
               "двести": "200",
               "триста": "300",
               "четыреста": "400",
               "пятьсот": "500",
               "шестьсот": "600",
               "семьсот": "700",
               "восемьсот": "800",
               "девятьсот": "900",
               "тысяча": "1000", "тысячи": "1000", "тысяч": "1000",
               "миллион": "1000000", "миллиона": "1000000", "миллионов": "1000000",
               "миллиард": "1000000000", "миллиарда": "1000000000", "миллиардов": "1000000000"
               }
    lst = string.lower().split(" ")  # разбиваем на слова
    stringn = " ".join(lst)  # т.к. в исходном параметре слова могли разделяться несколькими пробелами,
    # то формируем этот параметр с одним пробелом между словами для дальнейшей проверки.
    # Небходимо получит выражение типа (100+16)*1000000+(100+20+1)*1000+(900+30),
    # а затем eval вычислить его
    strv = ""
    minus_sign = False
    f_Bracket = True  # необходима открывающая скобка
    i = 0
    for word in lst:
        if i == 0 and word == "минус":  # запоминаем минус
            minus_sign = True
        else:
            nword = numbers.setdefault(word, "NO")  # ищем слово в словаре.
            if nword == "NO":
                return -999999999999999  # если не найдено слово в словаре, то возвращаем 15 9-ок.
            if nword[1:4] == "000":  # если надо добавить тысячи, миллионы, миллиарды
                strv = strv + ")*" + nword  # добавляем к выражению закрывающую скобку, умножение и число
                f_Bracket = True  # необходима открывающая скобка
            else:
                if f_Bracket:
                    strv = strv + "+(" + nword  # добавляем к выражению плюс, открывающую скобку и число
                    f_Bracket = False  # открывающая скобка не нужна
                else:
                    strv = strv + "+" + nword  # добавляем к выражению плюс и число
        i = +1
    if not f_Bracket:
        strv = strv + ")"  # добавляем закрывающую скобку.
    strv = strv[1:]  # Т.к. вначале стоит плюс, то берем с 1-го символа (убираем плюс)
    # получаем выражение типа (100+16)*1000000+(100+20+1)*1000+(900+30)
    try:
        value = eval(strv) * (-1 if minus_sign else 1)  # вычисляем выражение и при необходимости умножаем на -1
        # print(strv)
        stringv = num2text(value, main_units=((u'', u'', u''), sex))  # преобразовываем число в пропись
        if stringv != stringn:  # если значения исходного параметра с одним пробелом не совпадают с числом прописью,
            # значит в исходном параметре была ошибка (например, один тысяча)
            value = -999999999999999  # возвращаем 15 9-ок.
    except (Exception,):
        value = -999999999999999  # возвращаем 15 9-ок.
    return value


def str_to_date(dtc):
    """
     Возвращает дату формате даты.
     Параметры: dtc - дата в виде DD MMMM YYYY года (например, 5 марта 2020 года или 5 март 2020).
     DD - день в цифровом формате
     MMMM - месяц в сиволном формате
     YYYY - год  в цифровом формате
     текст 'года' может отсутвовать
     """

    dtstr_m = dtc.replace('ря', 'рь').replace('ля', 'ль').replace('рта', 'рт').replace('ая', 'ай', ).replace('ня',
                                                                                                             'нь').replace(
        'ста', 'ст').replace('года', '').replace(" ", "")
    return datetime.datetime.strptime(dtstr_m, "%d%B%Y")


def wordsd2num(number, sex='m'):
    """
    Возвращает число цифрами
    Параметры:
    number - число, может быть целое, строчное из цифр или прописью.
    sex – род ('f' - женский, 'm' – мужской, 'n' – средний), по умолчанию m.
    Если обнаружена ошибка, то возвращается чило -999999999999999 15-ть девяток с минусом
    """
    ret = -999999999999999
    if type(number) == int:
        ret = number
    elif number.isdigit():
        try:
            ret = int(number)
        except(Exception,):
            pass
    else:
        ret = word2num(number, sex)
    return ret


import sys


def main():
    # x=Addunist(0, main_units = ((u'метр', u'метра', u'метров'), 'm'),derive_number=False)
    # print(x)
    print(hex2rgb("123456"))


if __name__ == "__main__":
    main()
