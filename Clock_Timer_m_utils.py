import datetime
type_alarm = ("Ежедневно", "По дням недели", "По дате")


def ret_priod(period, date, type):
    rez = ""
    lstday = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")
    if type == 0:
        rez = "Ежедневно"
    elif type == 1:
        rez = ""
        i = 0
        for c in period:
            rez = rez + (lstday[i] + "," if c == "1" else "")
            i += 1
        rez = rez[0:-1]
    elif type == 2:
        rez = datetime.datetime.strftime(date, '%d.%m.%Y')
    return rez


def get_key_alarm(word):
    x = word.split("~")
    return x[0] + "~" + x[1]


if __name__ == '__main__':
    pass
