import json
import logging
import math
from collections import deque
from random import choice

import discord
import lichess.api
import lyricsgenius
import pandas as pd
import requests
import wikipedia
from discord.ext import commands
from pythonds.basic.stack import Stack
from requests import get
from youtubesearchpython import VideosSearch

from BalanceTree import Tree
from from_10_to_p import from_10_to_p
from from_p_to_10 import from_p_to_10
from lists import *

# Логирование
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
# Подгрузка данных из файла config.json
with open("config.json", "r", encoding="UTF-8") as fl:
    data = json.load(fl)
client = commands.Bot(command_prefix=data["prefix"])
genius = lyricsgenius.Genius(data["genius"])

wikipedia.set_lang("en")


def wiki(req):
    # Получает обобщение статьи из википедии
    article = wikipedia.summary(req, sentences=5)
    return article


def isint(inp: str) -> bool:
    # Является ли число целым
    try:
        int(inp)
        return True
    except ValueError:
        return False


def isfloat(inp: str) -> bool:
    # Является ли число вещественным
    try:
        float(inp)
        return True
    except ValueError:
        return False


def prettyprint(mes):
    # Красивая печать
    return [f"{3 * '`'}\n{mes[1980 * i:1980 * (i + 1)]}{3 * '`'}"
            for i in range(math.ceil(len(mes) / 1980))]


def tenorgif(req_mes, limit=10):
    # Получает gif-картинку
    try:
        tenor_key = data["tenor"]
        r = requests.get("https://api.tenor.com/v1/anonid?key=%s" % tenor_key)
        if r.status_code == 200:
            anon_id = json.loads(r.content)["anon_id"]
        else:
            anon_id = ""
        r = requests.get(
            "https://api.tenor.com/v1/search?q=%s&key=%s&limit=%s&anon_id=%s" %
            (req_mes, tenor_key, limit, anon_id))

        if r.status_code == 200:
            return choice(json.loads(r.content)["results"])["url"]
        return None
    except Exception as e:
        print(e)
        return None


@client.event
async def on_ready():
    # Действия при запуске бота
    await client.change_presence(status=discord.Status.idle, activity=discord.Game("Ledivee kinda sus ngl."))
    print(f'{client.user} has connected to Discord!')
    guilds = client.guilds
    for guild in guilds:
        print(f'{client.user} подключились к чату: '
              f'{guild.name}(id: {guild.id})\n')


@client.event
async def on_message(message):
    # Действия при сообщении
    if message.author.bot:
        return
    _usr = (str(message.author.id), message.author.name + "#" + message.author.discriminator)
    # Есть ли у пользователя роль админа
    isadmin = message.author.guild_permissions.administrator

    pref = data["prefix"]
    channel = message.channel
    text = message.content

    # Комманды бота
    if text.replace(" ",  "") == "1000-7":
        await channel.send("```" + "\n".join([f"{1000 - i} - {7} = {1000 - i - 7}"
                                              for i in range(0, 1000, 7)]) + "```")

    if text.startswith(pref):
        # Получить аватарки упомянутых пользователей или ролей
        if text.startswith(pref + "av"):
            args = message.mentions
            for i in message.role_mentions:
                args += i.members
            if not args:
                await channel.send(f"`{message.author.nick or message.author.name}'s avatar:`")
                await channel.send(message.author.avatar_url)
            else:
                for i in message.mentions:
                    await channel.send(f"`{i.nick or i.name}'s avatar:`")
                    await channel.send(i.avatar_url)

        elif text.startswith(pref + "stop") and _usr[0] == "318322325923692544":
            # Закончить сессию (млжет только тот, чей id в условии)
            if len(text.split()) > 1 and text.split()[1] == "help":
                await channel.send(f"```{pref}stop```")
            else:
                await stop(channel)

        elif text == pref + "latency":
            # Задержка до сервера
            if len(text.split()) > 1 and text.split()[1] == "help":
                await channel.send(f"```{pref}latency```")
            else:
                await channel.send(latency())

        elif text == pref + "help":
            # Помощь
            lst = [[("help",), "helps with commands", False],
                   [("latency",), "sends bot's latency", False],
                   [("clear",), "clears last N messages", True],
                   [("savechat",), "saves last N messages in chat", True],
                   [("av",), "sends avatars of all mentioned people or roles", False],
                   [("list",), "works with lists", False],
                   [("song",), "sends info about the song", False],
                   [("artist",), "sends info about the artist", False],
                   [("lichess",), "works with lichess api", False],
                   [("wiki",), "gets a brief summary of an article", False],
                   [("ss",), "translates numbers between number systems", False],
                   [("bincode",), "returns binary code of a number", False],
                   [("tree",), "builds and sends 2 binary trees: non- and balanced", False],
                   [("in_to_post", "in2post"), "infix format to postfix format", False],
                   [("post",), "evaluates the expression in postfix format", False],
                   [("pref",), "evaluates the expression in prefix format", False],
                   [("pog",), "responds with 'poggers' in random encapsulation", False],
                   [("send_a_cat",), "sends random cat pic / gif", False],
                   [("i_am_a_ghoul", "ima_ghoul"), "sends random kaneki gif", False],
                   [("send_nudes",), "sends a random Khovanskiy Maksim pic", True]]

            outp = ""
            for i in lst:
                outp += f"{pref}{i[0][0]:16} —  {i[1]} {'(fa)' * i[2]}" + "\n" * (len(i[0]) > 1) + \
                        "\n".join(["   > " + pref + j for j in i[0][1:]]) + "\n"
            for item in prettyprint(f"Form: command_name — description\n\n{outp}1000 - 7          "
                                    f"—  counts down from 1000 to -1 with the step of 7 "
                                    f"\n\n(fa) = 'only for admins'"):
                await channel.send(item)

        elif text.startswith(pref + "send_a_cat"):
            # Отправить случайного котика
            if len(text.split()) > 1 and text.split()[1] == "help":
                await channel.send(f"```{pref}send_a_cat```")
            await channel.send(send_a_cat())

        elif text.startswith(pref + "pog"):
            # PoGgErS
            if len(text.split()) > 1 and text.split()[1] == "help":
                await channel.send(f"```{pref}pog```")
            else:
                await channel.send("".join([i if choice([0, 1]) else i.capitalize() for i in "poggers"]))

        elif text.startswith(pref + "send_nudes") and isadmin:
            # Кхм...
            if len(text.split()) > 1 and text.split()[1] == "help":
                await channel.send(f"```{pref}send_nudes```")
            await channel.send(send_nudes())

        elif text.startswith(pref + "clear") and isadmin:
            # Очистить первык N сообщений
            lim = text.split()
            if len(lim) > 1:
                if lim[1] == "help":
                    await channel.send(f"```{pref}clear {{limit}}```")
                elif lim[1].isdigit():
                    await clear(channel, int(lim[1]))
                else:
                    await channel.send(f"```Argument isn't a number.\n{pref}clear {{limit}}```")
            else:
                await clear(channel)

        elif text.startswith(pref + "song"):
            # Прислать информацию о запрошенной песне
            args = text.split()
            if len(args) > 1:
                if args[1] == "help":
                    await channel.send(f"```{pref}song {{song name}} : {{artist}}\nor\n{pref}song {{song name}}```")
                else:
                    for item in song(text.split()[1:]):
                        await channel.send(item)
            else:
                await channel.send(f"```Wrong song or name.\n{pref}song {{song name}} :"
                                   f" {{artist}}\nor\n{pref}song {{song name}}```")

        elif text.startswith(pref + "artist"):
            # Прислать информацию о запрошенном музыкальном исполнителе
            args = text.split()
            if len(args) > 1:
                if args[1] == "help":
                    await channel.send(f"```{pref}artist {{artist}}```")
                else:
                    for item in artist(text.split()[1:]):
                        await channel.send(item)
            else:
                await channel.send(f"```Wrong artist name.\n{pref}artist {{artist}}```")

        elif text.startswith(pref + "tree"):
            # Построить бинарное дерево (небалансированное и сбалансированное)
            args = text.split()
            if len(args) > 1:
                if args[1] == "help":
                    await channel.send(f"{pref}tree {{numbers,}}")
                else:
                    f = False
                    for i in args[1:]:
                        if not isfloat(i):
                            f = True
                            break
                    else:
                        for item in tree(args[1:]):
                            await channel.send(item)
                    if f:
                        await channel.send(f"```Arguments are not all numbers.\n{pref}tree {{numbers}}```")
            else:
                await channel.send(f"```No arguments to create a binary tree.\n{pref}tree {{numbers}}```")

        elif text.startswith(pref + "lichess"):
            # Делает запрос к lichess
            args = text.split()
            if len(args) > 1:
                if args[1] == "help":
                    await channel.send(f"```{pref}lichess user {{username}}```")
                elif args[1] == "user" and len(args) > 2:
                    # Запрос о пользователе
                    await channel.send(liuser(args[2]))
                else:
                    await channel.send(f"```There is no command named {args[1]}.\n"
                                       f"{pref}lichess help```")
            else:
                await channel.send(f"```No command was written.\n"
                                   f"{pref}lichess help```")

        elif text.startswith(pref + "savechat"):
            # Сохраняет последние N сообщений из чата
            args = text.split()
            if len(args) > 1:
                if args[1] == "help":
                    await channel.send(f"```{pref}savechat {{limit}}```")
                elif args[1].isdigit():
                    await savechat(channel, int(args[1]))
                else:
                    await channel.send(f"```Limit argument should be an integer.\n{pref}savechat {{limit=1000}}```")
            else:
                await savechat(channel)

        elif text.startswith(pref + "ima_ghoul") or text.startswith(pref + "i_am_a_ghoul"):
            # Случайная gif-картинка канеки
            args = text.split()
            if len(args) > 1 and args[1].isdigit():
                if args[1] == "help":
                    await channel.send(f"```{pref}ima_ghoul {{Limit=30}}\n{pref}i_am_a_ghoul {{Limit=30}}```")
                await channel.send(ima_ghoul(int(args[1])))
            else:
                await channel.send(ima_ghoul())

        elif text.startswith(pref + "ss"):
            # Перевод между системами счисления
            args = text.split()
            if len(args) > 1 and args[1] == "help":
                await channel.send(f"```{pref}ss {{ss1}} {{ss2}} {{number}}```")
            if len(args) == 4 and args[1].isdigit() and 1 < int(args[1]) < 36 \
                    and args[2].isdigit() and 1 < int(args[2]) < 36:
                await channel.send(ss(int(args[1]), int(args[2]), args[3]))
            else:
                await channel.send(f"```Not enough arguments.\n{pref}ss {{ss1}} {{ss2}} {{number}}```")

        elif text.startswith(pref + "bincode"):
            # Двоичный код числа
            args = text.split()
            if len(args) > 1:
                if args[1] == "help":
                    await channel.send(f"```{pref}bincode {{number}} {{bits=8}}```")
                elif isint(args[1]):
                    if len(args) > 2:
                        responce = bin_code(int(args[1]), int(args[2]))
                        if responce is not None:
                            await channel.send(f"```"
                                               f"Normal form: {responce[0]}\n"
                                               f"Ones' complement: {responce[1]}\n"
                                               f"Two’s complement: {responce[2]}"
                                               f"```")
                        else:
                            await channel.send(f"```Your number isn't in range [{2 ** (int(args[2]) - 1) - 1};"
                                               f"{-(2 ** (int(args[2]) - 1))}]```")
                    else:
                        responce = bin_code(int(args[1]))
                        if responce is not None:
                            await channel.send(f"```"
                                               f"Normal form: {responce[0]}\n"
                                               f"Ones' complement: {responce[1]}\n"
                                               f"Two’s complement: {responce[2]}"
                                               f"```")
                        else:
                            await channel.send("```Your number isn't in range [127;-128].```")
                else:
                    await channel.send(f"```The argument isn't a number.\n{pref}bincode {{number}} {{bits=8}}```")
            else:
                await channel.send(f"```Not enough arguments.\n{pref}bincode {{number}} {{bits=8}}```")

        elif text.startswith(pref + "in_to_post") or text.startswith(pref + "in2post"):
            # Перевод из инфиксной в постфиксную форму
            ops = "+-*/()"
            for i in ops:
                text = text.replace(i, " " + i + " ")
            args = text.split()
            if len(args) > 1:
                if args[1] == "help":
                    await channel.send(f"```{pref}in2post {{expression}}\n{pref}in_to_post {{expression}}```")
                responce = infix_to_postfix(" ".join(args[1:]))
                if responce is not None:
                    await channel.send(responce)
                else:
                    await channel.send(f"```No response received.\n{pref}in2post {{expression}}"
                                       f"\n{pref}in_to_post {{expression}}```")
            else:
                await channel.send(f"```No expression was given.\n{pref}in2post {{expression}}"
                                   f"\n{pref}in_to_post {{expression}}```")

        elif text.startswith(pref + "post"):
            # Вычиление в постфиксной форме
            ops = "+-*/"
            for i in ops:
                text = text.replace(i, " " + i + " ")
            args = text.split()
            if len(args) > 1:
                if args[1] == "help":
                    await channel.send(f"```{pref}post {{expression}}```")
                responce = post(args[1:])
                if responce is not None:
                    await channel.send(responce)
                else:
                    await channel.send(f"```No response received.\n{pref}post {{expression}}```")
            else:
                await channel.send(f"```No expression was given.\n{pref}post {{expression}}```")

        elif text.startswith(pref + "pref"):
            # Вычиление в префиксной форме
            ops = "+-*/"
            for i in ops:
                text = text.replace(i, " " + i + " ")
            args = text.split()
            if len(args) > 1:
                responce = prefix(deque(args[1:]))
                if responce is not None:
                    await channel.send(responce)
                else:
                    await channel.send(f"```No response received.\n{pref}pref {{expression}}```")
            else:
                await channel.send(f"```No expression was given.\n{pref}pref {{expression}}```")

        elif text.startswith(pref + "wiki"):
            # Запрос из википедии
            args = text.split()
            if len(args) > 1:
                if args[1] == "help" and len(args) == 2:
                    await channel.send(f"```{pref}wiki {{object}}```")
                obj = " ".join(args[1:])
                try:
                    w = wiki(obj)
                    for item in prettyprint(w):
                        await channel.send(item)
                except:
                    await channel.send(f'```No such article article was found: "{obj}".```')
            else:
                await channel.send("```No arguments were given.\n{pref}wiki {{object}}```")

        elif text.startswith(pref + "list"):
            # Списки
            args = text.split()
            if len(args) > 2:
                if args[2] == "create":
                    await channel.send(create_list(args[1], _usr, args[3]))
                elif args[2] == "add":
                    await channel.send(add_to_list((args[1], _usr, " ".join(args[3:]))))
                elif args[2] == "remove":
                    await channel.send(remove_list(args[1], " ".join(args[3:]), _usr))
                elif args[2] == "removeat":
                    await channel.send(removeat_list(args[1], int(args[3]), _usr))
                elif args[2] == "insert":
                    await channel.send(insert_list(args[1], int(args[3]), " ".join(args[4:]), _usr))
                elif args[2] == "delete":
                    await channel.send(delete_list(args[1], _usr))
                elif args[2] == "author":
                    await channel.send(get_list_author(args[1]))
            else:
                if args[1] == "help":
                    await channel.send(f"```{pref}list {{listname}} create {{args}}\n"
                                       f"{pref}list {{listname}} add {{arg}}\n"
                                       f"{pref}list {{listname}} remove {{arg}}\n"
                                       f"{pref}list {{listname}} removeat {{ind}}\n"
                                       f"{pref}list {{listname}} insert {{ind}} {{arg}}\n"
                                       f"{pref}list {{listname}} delete\n"
                                       f"{pref}list {{listname}} author\n"
                                       f"{pref}list {{listname}}```")
                else:
                    _, lst = read_list(args[1])
                    outp = args[1] + ":\n\n" + "\n".join([f"{ind + 1}. {i}" for ind, i in enumerate(lst)])
                    for item in prettyprint(outp):
                        await channel.send(item)


def latency():
    # Задержка до сервера
    return f"Latency: {round(client.latency * 1000)} ms"


async def clear(channel, amount=100):
    # Очистить первык N сообщений
    try:
        await channel.purge(limit=(amount + 1))
    except Exception as e:
        print(e)


async def stop(channel):
    # Закончить сессию
    await channel.purge(limit=1)
    await client.close()


def song(songinfo):
    # Прислать информацию о запрошенной песне
    try:
        if ":" in songinfo:
            div = songinfo.index(":")
            songname = " ".join(songinfo[:div])
            artistname = " ".join(songinfo[div + 1:])
        else:
            songname = " ".join(songinfo)
            artistname = ""
        sng = genius.search_song(songname, artistname)
        artistname = sng.artist
        songname = sng.title
        lyr = sng.lyrics
        yield f"`Text from {songname} by {artistname}:`"
        for i in prettyprint(lyr):
            yield i
        yield f"Write to Rythm: \n`" \
              f"!p {VideosSearch(sng.title + ' ' + sng.artist, limit=1).result()['result'][0]['link']}`"

    except Exception as e:
        print(e)
        yield "```Wrong song or artist name.\n.song {song name} : {artist}\nor\n.song {song name}```"


def artist(artistname):
    # Прислать информацию о запрошенном музыкальном исполнителе
    try:
        limit = 3
        artistname = " ".join(artistname)
        try:
            page = wikipedia.page(artistname)
            tmp = page.content.split('\n')[0]
            content = tmp[:1000] + (len(tmp) > 1000) * "..."
            yield f"{3 * '`'}{page.title}\n\n{content}{3 * '`'}"
        except Exception as exc:
            print(exc)
        songs = genius.search_artist(artistname, max_songs=limit).songs
        tt = "\n".join([f"{i + 1}|  {sng.title} "
                        f"({VideosSearch(sng.title + ' ' + sng.artist, limit=1).result()['result'][0]['link']})"
                        for i, sng in enumerate(songs)])
        if tt:
            outp = f"Most popular songs by {artistname}:\n\n{tt}"
            for i in prettyprint(outp):
                yield i
        else:
            yield "```Wrong artist name.\n.artist {artist}```"
    except Exception as e:
        print(e)
        yield "```Wrong artist name.\n.artist {artist}```"


def tree(keys):
    # Построить бинарное дерево (небалансированное и сбалансированное)
    inp = [int(x) for x in keys]
    b1 = Tree(inp[0])
    b2 = Tree(inp[0])
    for r in inp[1:]:
        b1.insert(r, bal=False)
        b2.insert(r)
    outp1 = ""
    for i in b1.display():
        outp1 += "\n" + i
    for i in prettyprint(outp1):
        yield i
    outp2 = ""
    for i in b2.display():
        outp2 += "\n" + i
    if outp1 != outp2:
        for i in prettyprint(outp2):
            yield i


async def savechat(ctx, limit=1000):
    # Сохраняет последние N сообщений из чата
    try:
        dt = pd.DataFrame(columns=['content', 'time', 'author'])
        flag = 0
        chnl = ctx.message.channel
        async for msg in chnl.history(limit=limit):
            dt = dt.append({'content': msg.content,
                            'time': msg.created_at,
                            'author': msg.author.name}, ignore_index=True)
            flag += 1
            if flag == limit:
                break
        cnt = 1
        while True:
            file_location = rf"saves/{chnl.name}{cnt}_save.csv"
            if not os.path.exists(file_location):
                break
            cnt += 1
        dt.to_csv(file_location)
        await ctx.send("done")
    except Exception as e:
        print(e)


def liuser(*others):
    # Данные о пользователе lichess
    _user = lichess.api.user(" ".join(others))
    return f"{3 * '`'}" \
           f"{_user['username']} (Currently {'online' if _user['online'] else 'offline'}).\n" \
           f"Classical:\n    Rating: {_user['perfs']['classical']['rating']}" \
           f"\n    Games: {_user['perfs']['classical']['games']}\n" \
           f"Rapid:\n    Rating: {_user['perfs']['rapid']['rating']}" \
           f"\n    Games: {_user['perfs']['rapid']['games']}\n" \
           f"Blitz:\n    Rating: {_user['perfs']['blitz']['rating']}" \
           f"\n    Games: {_user['perfs']['blitz']['games']}\n" \
           f"Bullet:\n    Rating: {_user['perfs']['bullet']['rating']}" \
           f"\n    Games: {_user['perfs']['bullet']['games']}\n" \
           f"Puzzles:\n    Rating: {_user['perfs']['puzzle']['rating']}" \
           f"\n    Completed: {_user['perfs']['puzzle']['games']}\n" \
           f"{3 * '`'}"


def send_a_cat():
    # Отправить случайного котика

    return get("https://api.thecatapi.com/v1/images/search").json()[0]["url"]


def send_nudes():
    # Кхм-Кхм...
    lst = [
        "imgur.com/a/c4kDjce",
        "imgur.com/lzQbq6F",
        "media.discordapp.net/attachments/770721440945143868/819552036587569172/unknown.png?width=810&height=450",
        "media.discordapp.net/attachments/770232175630221333/819541521464426526/unknown.png?width=810&height=572"
    ]
    return "https://" + choice(lst)


def ima_ghoul(limit=30):
    # Случайная gif-картинка канеки
    kaneki = tenorgif("kaneki", limit)
    if kaneki is not None:
        return kaneki
    return 3 * "`" + "Wrong request.\n.i_am_a_ghoul {limit : integer}" + 3 * "`"


def ss(ss1, ss2, n):
    # Перевод между системами счисления
    return from_10_to_p(from_p_to_10(n, ss1), ss2)


def bin_code(n, am=8):
    # Двоичный код числа
    pref = "0" if n >= 0 else "1"
    num = bin(abs(n))[2:]
    if n > 2 ** (am - 1) - 1 or n < -(2 ** (am - 1)):
        return None
    pr = "0" * (am - len(num)) + num
    if pref == "1":
        obr = "".join(["1" if i == "0" else "0" for i in pr])
        dop = from_10_to_p(str(int(from_p_to_10(obr, 2)) + 1), 2)[-am:]
        dop = "0" * (am - len(dop)) + dop
    else:
        obr = pr
        dop = pr
    return pr, obr, dop


def post(inp):
    # Вычиление в постфиксной форме
    stack = []
    i = 0
    for x in inp:
        if x in "+-*/":
            i += 1
            if len(stack) < 2:
                return None
            op2 = float(stack.pop())
            op1 = float(stack.pop())
            if x == "+":
                res = op1 + op2
            elif x == "-":
                res = op1 - op2
            elif x == "*":
                res = op1 * op2
            else:
                res = op1 / op2
            stack.append(res)
        else:
            stack.append(x)
    if len(stack) == 1:
        return stack[0]
    return None


def infix_to_postfix(infixexpr):
    # Перевод из инфиксной в постфиксную форму
    prec = dict()
    prec["*"] = 3
    prec["/"] = 3
    prec["+"] = 2
    prec["-"] = 2
    prec["("] = 1
    opStack = Stack()
    postfixList = list()
    tokenList = infixexpr.split()

    for token in tokenList:
        if token in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" or isfloat(token):
            postfixList.append(token)
        elif token == '(':
            opStack.push(token)
        elif token == ')':
            topToken = opStack.pop()
            while topToken != '(':
                postfixList.append(topToken)
                topToken = opStack.pop()
        else:
            while (not opStack.isEmpty()) and \
                    (prec[opStack.peek()] >= prec[token]):
                postfixList.append(opStack.pop())
            opStack.push(token)

    while not opStack.isEmpty():
        postfixList.append(opStack.pop())
    return " ".join(postfixList)


def prefix(tokens):
    # Вычиление в префиксной форме
    token = tokens.popleft()
    if token == '+':
        return prefix(tokens) + prefix(tokens)
    elif token == '-':
        return prefix(tokens) - prefix(tokens)
    elif token == '*':
        return prefix(tokens) * prefix(tokens)
    elif token == '/':
        return prefix(tokens) / prefix(tokens)
    else:
        return float(token)


client.run(data["token"])
