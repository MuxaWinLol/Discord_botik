import os


def read_list(listname):
    # Чтение списка
    try:
        with open(f"lists\\{listname}.txt", "r", encoding="UTF-8") as fl:
            fl.readline()
            return fl.readline().strip().split(), fl.readline().split("%2C")
    except FileNotFoundError:
        return "`list not found`"


def rewrite_list(args: tuple):
    # Переписать список
    try:
        with open(f"lists\\{args[0]}.txt", "r", encoding="UTF-8") as fl:
            priv = fl.readline().strip()
            auth = fl.readline().strip().split()
        with open(f"lists\\{args[0]}.txt", "w+", encoding="UTF-8") as fl:
            if priv == "public" or priv == "private" and args[1][0] == auth[0]:
                r = f"{priv}\n{' '.join(args[1])}\n{'%2C'.join(args[2])}"
                fl.write(r)
                return "`done`"
            return "`privacy error`"
    except FileNotFoundError:
        return "`list not found`"


def add_to_list(args: tuple):
    # Добавить элементы в список
    try:
        with open(f"lists\\{args[0]}.txt", "r", encoding="UTF-8") as fl:
            priv = fl.readline().strip()
            auth = fl.readline().strip().split()[0]
            b = fl.readline().strip()
        with open(f"lists\\{args[0]}.txt", "a", encoding="UTF-8") as fl:
            if priv == "public" or (priv == "private" and args[1][0] == auth):
                fl.write(("%2C" if b else "") + args[2])
                return "done"
            return "`privacy error`"
    except FileNotFoundError:
        return "`list not found`"


def get_list_author(listname):
    # Получить ник автора
    try:
        with open(f"lists\\{listname}.txt", "r", encoding="UTF-8") as fl:
            fl.readline()
            return fl.readline().strip().split()[1]
    except FileNotFoundError:
        return "`list not found`"


def create_list(listname, author, priv):
    # Создать список
    if listname != "help":
        pth = f"lists\\{listname}.txt"

        if not os.path.exists(pth):
            with open(pth, "w", encoding="UTF-8") as fl:
                fl.write(f"{priv}\n{' '.join(author)}\n")
            return "`done`"
        return "`list already exists`"
    return "`you can not create list with name: \"help\"`"


def delete_list(listname, author):
    # Удалить список
    pth = f"lists\\{listname}.txt"
    with open(f"lists\\{listname}.txt", "r", encoding="UTF-8") as fl:
        priv = fl.readline().strip()
        auth = fl.readline().strip().split()[0]
    if priv == "public" or priv == "private" and author[0] == auth:
        pth = os.path.join(os.path.abspath(os.path.dirname(__file__)), pth)
        os.remove(pth)
        return "`done`"
    return "`privacy error`"


def insert_list(listname, ind, arg, user):
    # Вставка элементов в список
    resp = read_list(listname, user)
    if isinstance(resp, tuple):
        auth, lst = resp
        lst.insert(ind - 1, arg)
        rewrite_list((listname, user, lst))
        return "`done`"
    else:
        return resp


def removeat_list(listname, ind, user):
    # Удаление элементов с индексом ind
    resp = read_list(listname, user)
    if isinstance(resp, tuple):
        auth, lst = resp
        lst = lst[:ind] + lst[ind:]
        rewrite_list((listname, user, lst))
        return "`done`"
    else:
        return resp


def remove_list(listname, arg, user):
    # Удаление элементов из списка
    resp = read_list(listname, user)
    if isinstance(resp, tuple):
        auth, lst = resp
        lst = [i for i in lst if i != arg]
        rewrite_list((listname, user, lst))
        return "`done`"
    else:
        return resp
