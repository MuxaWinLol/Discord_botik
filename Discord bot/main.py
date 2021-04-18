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

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

with open("config.json", "r", encoding="UTF-8") as fl:
    data = json.load(fl)
client = commands.Bot(command_prefix=data["prefix"])
genius = lyricsgenius.Genius(data["genius"])

wikipedia.set_lang("ru")


# def change_prefix(new_pref):
#     global data
#     data["prefix"] = new_pref
#     with open("config.json", "w", encoding="UTF-8") as fl1:
#         fl1.write(json.dumps(data))


def wiki(req):
    article = wikipedia.page(req)
    return article.title, article.page


def isint(inp: str) -> bool:
    try:
        int(inp)
        return True
    except ValueError:
        return False


def isfloat(inp: str) -> bool:
    try:
        float(inp)
        return True
    except ValueError:
        return False


def pprint(mes):
    return [f"{3 * '`'}\n{mes[1980 * i:1980 * (i + 1)]}{3 * '`'}"
            for i in range(math.ceil(len(mes) / 1980))]


def tenorgif(req_mes, limit=10):
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
    await client.change_presence(status=discord.Status.idle, activity=discord.Game("Ledivee kinda sus ngl."))
    print(f'{client.user} has connected to Discord!')
    guilds = client.guilds
    for guild in guilds:
        print(f'{client.user} подключились к чату: '
              f'{guild.name}(id: {guild.id})\n')


@client.event
async def on_message(message):
    if message.author.bot:
        return
    _usr = (str(message.author.id), message.author.name + "#" + message.author.discriminator)
    isadmin = message.author.id in [318322325923692544, 386068088644304918] or \
              message.author.guild_permissions.administrator
    pref = data["prefix"]
    channel = message.channel
    text = message.content
    if text == "1000 - 7" or text == "1000-7" and isadmin:
        await channel.send("```" + "\n".join([f"{1000 - i} - {7} = {1000 - i - 7}"
                                              for i in range(0, 1000, 7)]) + "```")

    if text.startswith(pref):
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

        elif text == pref + "latency":
            await channel.send(latency())

        elif text.startswith(pref + "send_a_cat"):
            await channel.send(send_a_cat())

        elif text == pref + "pog":
            await channel.send("".join([i if choice([0, 1]) else i.capitalize() for i in "poggers"]))

        elif text.startswith(pref + "send_nudes") and isadmin:
            await channel.send(send_nudes())

        elif text.startswith(pref + "stop") and isadmin:
            await stop(channel)

        elif text.startswith(pref + "changeprefix"):
            await stop(channel)

        elif text.startswith(pref + "clear") and isadmin:
            lim = text.split()
            if len(lim) > 1 and lim[1].isdigit():
                await clear(channel, int(lim[1]))
            else:
                await clear(channel)

        elif text.startswith(pref + "song"):
            args = text.split()
            if len(args) > 1:
                for item in song(text.split()[1:]):
                    await channel.send(item)
            else:
                await channel.send("```Wrong song or name.\n.song {song name} :"
                                   " {artist}\nor\n.song {song name}```")

        elif text.startswith(pref + "artist"):
            args = text.split()
            if len(args) > 1:
                for item in artist(text.split()[1:]):
                    await channel.send(item)
            else:
                await channel.send("```Wrong artist name.\n.artist {artist}```")

        elif text.startswith(pref + "tree"):
            args = text.split()
            if len(args) > 1:
                f = False
                for i in args[1:]:
                    if not isfloat(i):
                        f = True
                        break
                else:
                    for item in tree(args[1:]):
                        await channel.send(item)
                if f:
                    await channel.send("```Arguments are not all numbers```")
            else:
                await channel.send("```No arguments to create a binary tree```")

        elif text.startswith(pref + "lichess"):
            args = text.split()
            if len(args) > 1:
                if args[1] == "user" and len(args) > 2:
                    await channel.send(liuser(args[2]))
            else:
                await channel.send("```No arguments to create a binary tree```")

        elif text.startswith(pref + "savechat"):
            args = text.split()
            if len(args) > 1 and args[1].isdigit():
                await savechat(channel, int(args[1]))
            else:
                await savechat(channel)

        elif text.startswith(pref + "ima_ghoul") or text.startswith(pref + "i_am_a_ghoul"):
            args = text.split()
            if len(args) > 1 and args[1].isdigit():
                await channel.send(ima_ghoul(int(args[1])))
            else:
                await channel.send(ima_ghoul())

        elif text.startswith(pref + "ss"):
            args = text.split()
            if len(args) == 4 and args[1].isdigit() and 1 < int(args[1]) < 36 \
                    and args[2].isdigit() and 1 < int(args[2]) < 36:
                await channel.send(ss(int(args[1]), int(args[2]), args[3]))
            else:
                await channel.send("`СОСИ ЖЁПУ!!11!1!11`")

        elif text.startswith(pref + "bincode") or text.startswith(pref + "bin_code"):
            args = text.split()
            if len(args) > 1 and isint(args[1]):
                if len(args) > 2:
                    responce = bin_code(int(args[1]), int(args[2]))
                    if responce is not None:
                        await channel.send(f"```"
                                           f"Прямой код: {responce[0]}\n"
                                           f"Обратный код: {responce[1]}\n"
                                           f"Дополнительный код: {responce[2]}"
                                           f"```")
                    else:
                        await channel.send(f"```Ваше число вне диапазона [{2 ** (int(args[2]) - 1) - 1};"
                                           f"{-(2 ** (int(args[2]) - 1))}]```")
                else:
                    responce = bin_code(int(args[1]))
                    if responce is not None:
                        await channel.send(f"```"
                                           f"Прямой код: {responce[0]}\n"
                                           f"Обратный код: {responce[1]}\n"
                                           f"Дополнительный код: {responce[2]}"
                                           f"```")
                    else:
                        await channel.send("Ваше число вне диапазона [127;-128]")
            else:
                await channel.send("`СОСИ ЖЁПУ!!11!1!11`")

        elif text.startswith(pref + "in_to_post") or text.startswith(pref + "in2post"):
            ops = "+-*/()"
            for i in ops:
                text = text.replace(i, " " + i + " ")
            args = text.split()
            if len(args) > 1:
                responce = infix_to_postfix(" ".join(args[1:]))
                if responce is not None:
                    await channel.send(responce)
                else:
                    await channel.send("`СОСИ ЖЁПУ!!11!1!11`")
            else:
                await channel.send("`СОСИ ЖЁПУ!!11!1!11`")

        elif text.startswith(pref + "post"):
            ops = "+-*/"
            for i in ops:
                text = text.replace(i, " " + i + " ")
            args = text.split()
            if len(args) > 1:
                responce = post(args[1:])
                if responce is not None:
                    await channel.send(responce)
                else:
                    await channel.send("`СОСИ ЖЁПУ!!11!1!11`")

        elif text.startswith(pref + "pref"):
            ops = "+-*/"
            for i in ops:
                text = text.replace(i, " " + i + " ")
            args = text.split()
            if len(args) > 1:
                responce = prefix(deque(args[1:]))
                if responce is not None:
                    await channel.send(responce)
                else:
                    await channel.send("`СОСИ ЖЁПУ!!11!1!11`")

        elif text.startswith(pref + "wiki"):
            args = text.split()
            if len(args) > 1:
                for item in pprint(wiki(" ".join(args[1:]))):
                    await channel.send(item)
            else:
                await channel.send("`СОСИ ЖЁПУ!!11!1!11`")

        elif text.startswith(pref + "list"):
            args = text.split()
            if len(args) > 2:
                if args[2] == "create":
                    await channel.send(create_list(args[1], _usr, args[3]))
                elif args[2] == "add":
                    await channel.send(add_to_list((args[1], _usr, args[3:])))
                elif args[2] == "remove":
                    await channel.send(remove_list(args[1], args[3:], _usr))
                elif args[2] == "removeat":
                    await channel.send(removeat_list(args[1], int(args[3]), _usr))
                elif args[2] == "insert":
                    await channel.send(insert_list(args[1], int(args[3]), args[4], _usr))
                elif args[2] == "delete":
                    await channel.send(delete_list(args[1], _usr))
                elif args[2] == "author":
                    await channel.send(get_list_author(args[1]))
            else:
                if args[1] == "help":
                    await channel.send("""```.list {listname} create  {args}
.list {listname} add  {args}
.list {listname} remove  {arg}
.list {listname} removeat  {ind}
.list {listname} insert  {ind} {arg}
.list {listname} delete
.list {listname} author
.list {listname}```""")
                else:
                    _, lst = read_list(args[1])
                    outp = args[1] + ":\n\n" + "\n".join([f"{ind + 1}. {i}" for ind, i in enumerate(lst)])
                    for item in pprint(outp):
                        await channel.send(item)
        # elif text.startswith(pref + "change_prefix"):
        #     args = text.split()
        #     if len(args) > 1:
        #         change_prefix(args[1])
        #         await channel.send(f"`prefix was successfully set to {args[1]}`")
        #     else:
        #         await channel.send("`no prefix argument was given`")


def latency():
    return f"Latency: {round(client.latency * 1000)} ms"


async def stop(channel):
    await channel.purge(limit=1)
    await client.close()


async def clear(channel, amount=100):
    try:
        await channel.purge(limit=(amount + 1))
    except Exception as e:
        print(e)


def song(songinfo):
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
        for i in pprint(lyr):
            yield i
        yield f"Write to Rythm: \n`" \
              f"!p {VideosSearch(sng.title + ' ' + sng.artist, limit=1).result()['result'][0]['link']}`"

    except Exception as e:
        print(e)
        yield "```Wrong song or name.\n.song {song name} : {artist}\nor\n.song {song name}```"


def artist(artistname):
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
            for i in pprint(outp):
                yield i
        else:
            yield "```Wrong artist name.\n.artist {artist}```"
    except Exception as e:
        print(e)
        yield "```Wrong artist name.\n.artist {artist}```"


def tree(keys):
    inp = [int(x) for x in keys]
    b1 = Tree(inp[0])
    b2 = Tree(inp[0])
    for r in inp[1:]:
        b1.insert(r, bal=False)
        b2.insert(r)
    outp1 = ""
    for i in b1.display():
        outp1 += "\n" + i
    for i in pprint(outp1):
        yield i
    outp2 = ""
    for i in b2.display():
        outp2 += "\n" + i
    if outp1 != outp2:
        for i in pprint(outp2):
            yield i


async def savechat(ctx, limit=1000):
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
    return get("https://api.thecatapi.com/v1/images/search").json()[0]["url"]


def send_nudes():
    lst = [
        "imgur.com/a/c4kDjce",
        "imgur.com/lzQbq6F",
        "media.discordapp.net/attachments/770721440945143868/819552036587569172/unknown.png?width=810&height=450",
        "media.discordapp.net/attachments/770232175630221333/819541521464426526/unknown.png?width=810&height=572"
    ]
    return "https://" + choice(lst)


def ima_ghoul(limit=30):
    kaneki = tenorgif("kaneki", limit)
    if kaneki is not None:
        return kaneki
    return 3 * "`" + "Wrong request.\n.i_am_a_ghoul {limit : integer}" + 3 * "`"


def ss(ss1, ss2, n):
    return from_10_to_p(from_p_to_10(n, ss1), ss2)


def bin_code(n, am=8):
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
