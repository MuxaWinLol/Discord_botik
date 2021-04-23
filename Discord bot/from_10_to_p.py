from decimal import Decimal


def for_integer(N, base):
    # Для чисел
    if not hasattr(for_integer, 'table'):
        for_integer.table = '0123456789ABCDEF'
    x, y = divmod(N, base)
    return for_integer(x, base) + for_integer.table[y] if x else for_integer.table[y]


def for_period(some_part):
    # Для периодов
    znam = ''
    chicl = ['', '']
    plus = '0'
    f = True
    for i in some_part[2:-1]:
        if '(' == i:
            f = False
            plus = '9'
        else:
            znam = plus + znam
            if f:
                chicl[1] += i
            chicl[0] += i
    if chicl[1] == '':
        chicl[1] = '0'
    return Decimal((int(chicl[0]) - int(chicl[1])) / int(znam))


def from_10_to_p(number, cc):
    # Перевод из 10 сс в P
    number = number.split(".")
    result = ''
    ind = 0
    f = False
    if len(number) == 1:
        return for_integer(int(number[0]), cc)
    else:
        if '(' in number[1]:
            float_part = for_period('0.' + number[1])
        else:
            float_part = Decimal('0.' + number[1])
        m = [float_part]
        i = 0
        f = True
        while float_part > 0 and i < 32:
            d = int(float_part * cc)
            result += for_integer(d, cc)
            float_part = Decimal(str(float_part * cc - d)[:-1])
            print(float_part)
            if float_part in m:
                f = False
                ind = m.index(float_part)
                break
            m.append(float_part)
            i += 1
        print(m)
    if str(cc - 1) * 5 in result:
        result = result[:result.index(str(cc - 1) * 5)]
        result = str(int(result) + 1)
    if f:
        if result:
            return for_integer(int(number[0]), cc) + '.' + result
        return for_integer(int(number[0]), cc)
    return for_integer(int(number[0]), cc) + '.' + result[:ind] + '(' + result[ind:] + ')'
