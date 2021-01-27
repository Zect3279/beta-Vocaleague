# vq/vq.py

import discord
from discord.ext import commands

import json
import random
import asyncio
from dispander import dispand
import sys
from urllib.parse import urlparse
import mysql.connector
import os


# vq.cmdから渡された引数を格納したリストの取得
argvs = sys.argv


class VQ(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db
        self.hall = int(argvs[3])  # 会場
        self.win = []  # 勝者
        self.gui = str(argvs[4])  # ギルド ID
        self.chi = str(argvs[3])  # チャンネル ID

        self.mem: Optional[str]= None  # メンバー ID（正解判定用）
        self.na: Optional[str] = None  # メンバー Name（正解判定用）

        self.pr = "問題"
        self.an = "正解"

        self.og = False  # On Going（移動中）

        with open("json/question.json", mode="r", encoding='utf-8') as f:
            self.qu = json.load(f)
            f.close()


        # if argvs[2] != "all":
        #     self.ids = argvs[2]  # 参加者ID
        #     self.names = argvs[4]



    @commands.Cog.listener()
    async def on_ready(self):
        chan = self.bot.get_channel(self.hall)
        # if argvs[2] == "all":
        #     msg = "参加者：自由参加"
        # else:
        #     msg = f"参加者一覧...\n{self.names}"
        # await chan.send(f"起動完了\n\n{msg}")
        print("VQ is ready!")
        await chan.send(f"起動完了...\n`/vq`でゲームを開始できます。\n`/vq`の後に任意の数字を入力することで、その回数連続で遊ぶことができます。")
        # await self.vq("abc")

    @commands.command()
    async def start(self,ctx):
        pass

    @commands.command()
    async def point(self, ctx):
        data = self.db.get_user_rankings()
        print(data)

    @commands.command()
    async def end(self, ctx):
        if self.chi != str(ctx.channel.id):
            return
        await ctx.send("了解...\nゲームを終了しました。")
        sys.exit()


    @commands.Cog.listener()
    async def on_message(self, message):
        await dispand(message)

        with open("json/point.json", mode="r", encoding='utf-8') as f:
            self.point = json.load(f)
            f.close()

        self.na = message.author.name

        if message.author == self.bot:
            return
        if self.og != True:
            return
        if self.gui != str(message.author.guild.id):
            return
        if self.chi != str(message.channel.id):
            return
        if self.na in self.win:
            return
        if message.content != self.an:
            return

        try:
            self.db.add_point
        except KeyError:
            self.db.create_user(ctx.author.id, ctx.author.name)
            self.point[self.gui].setdefault(self.mem, {"name" : self.na,"point" : 1})
        finally:
            self.win.append(message.author.name)
            await message.add_reaction("⭕")





    @commands.command()
    async def vq(self, ctx, many="1"):
        if ctx != "abc":
            if self.chi != str(ctx.channel.id):
                return

        try:
            many = int(many)
        except:
            many = 1

        for i in range(many):
            self.__init__(self.bot)

            await asyncio.sleep(1)

            chan = self.bot.get_channel(self.hall)
            self.win = []

            # if ctx.author != self.bot.get_user(653785595075887104):
            #     await ctx.send("あなたには使用する権限がありません。 \nYou don't have the privilege to use this.")
            #     return



            numA = str(random.randint(1, 230))
            numB = int(random.randint(0,2))

            que = self.qu[numA]["Q"]

            self.pr = que[numB]
            self.an = self.qu[numA]["A"]

            test = discord.Embed(title=self.pr,colour=0x1e90ff)
            test.add_field(name="\n思考時間開始", value="ボカリーグ", inline=True)
            # test.set_author(name="ボカリーグ", icon_url=discord.File("V.jpg"))
            # await ctx.send(embed=test)

            # await chan.send(self.an)

            edit = await chan.send(embed=test)
            await asyncio.sleep(0.5)
            for i in range(5):
                n = 5 - i
                test = discord.Embed(title=self.pr,colour=0x1e90ff)
                test.add_field(name="\n思考時間 " + "■" * n, value="ボカリーグ", inline=True)
                # test.set_author(name="ボカリーグ", icon_url=discord.File("V.jpg"))
                await edit.edit(embed=test)
                await asyncio.sleep(0.9)

            self.og = True

            test = discord.Embed(title=self.pr,colour=0x1e90ff)
            test.add_field(name="\n解答開始", value="ボカリーグ", inline=True)
            # test.set_author(name="ボカリーグ", icon_url=discord.File("V.jpg"))
            await edit.edit(embed=test)

            await asyncio.sleep(6.5)

            self.og = False

            test = discord.Embed(title="回答終了\n解答：{}".format(self.an),colour=0x1e90ff)
            await chan.send(embed=test)
            # await ctx.send("正解者：{}".format(round_win))

            await asyncio.sleep(0.5)

            if len(self.win) == 0:
                await chan.send('正解者はいませんでした。')
                return
            txt = "正解者は、\n```"
            for name in self.win:
                txt += f"\n{name} さん"
            await chan.send(f"{txt}\n```\nの{len(self.win)}人です！")

            with open("json/point.json", mode="w", encoding='utf-8') as f:
                WritePoint = json.dumps(self.point, ensure_ascii=False, indent=2)
                f.write(WritePoint)
                print('Pointの上書きに成功しました。')
                f.close()





    # @commands.command()
    # async def point(self, ctx):
    #
    #     if len(self.point[self.gui]) == 0:
    #         await ctx.send('ポイント所持者はいません。')
    #         return
    #
    #     txt = "ポイント保持者:\n```\n"
    #     # Nu = 0
    #     # while Nu <= 10:
    #     for member in self.bot.get_guild(int(ctx.guild.id)).members:
    #         memId = str(member.id)
    #         guiID = str(ctx.guild.id)
    #         try:
    #             if point[guiID][memId]["point"] == 0:
    #                 pass
    #             mesid = self.bot.get_user(int(memId))
    #             pop = point[guiID][memId]["point"]
    #             txt += f"\n{mesid.display_name} : {pop}ポイント"
    #         except KeyError as e:
    #             print(e)
    #             point[str(ctx.guild.id)][str(e)] = {"name" : member.display_name,"point" : 0}
    #         # Nu += 1
    #     await ctx.send(f"{txt}\n```")
    #     # print(txt)
    #
    #     with open("json/point.json", mode="w", encoding='utf-8') as f:
    #         WritePoint = json.dumps(point, ensure_ascii=False, indent=2)
    #         f.write(WritePoint)
    #         # print('Pointの上書きに成功しました。')
    #         f.close()

    # @commands.command()
    # async def point_guild(self, ctx):
    #
    #     with open("json/point.json", mode="r", encoding='utf-8') as f:
    #         point = json.load(f)
    #
    #         # for guild in self.bot.guilds:
    #         #     for member in guild.members:
    #         #         if member not in point[str(guild.id)]:
    #         #             point[str(guild.id)][str(member.id)] = {"name" : member.display_name,"point" : 0}
    #
    #     if len(point) == 0:
    #         await ctx.send('ポイント所持者はいません。')
    #         return
    #     txt = "ポイント保持者:\n```"
    #     for member in self.bot.get_guild(int(ctx.guild.id)).members:
    #         memId = str(member.id)
    #         guiID = str(ctx.guild.id)
    #         mesid = self.bot.get_user(int(memId))
    #         try:
    #             pop = point[guiID][memId]["point"]
    #         except KeyError as e:
    #             print(e)
    #             point[str(ctx.guild.id)][str(e)] = {"name" : member.display_name,"point" : 0}
    #             pop = point[guiID][memId]["point"]
    #         txt += f"\n{mesid.display_name} : {pop}ポイント"
    #     await ctx.send(f"{txt}\n```")


    # @commands.command()
    # async def point_all(self, ctx):
    #
    #     with open("json/point.json", mode="r", encoding='utf-8') as f:
    #         point = json.load(f)
    #
    #     if len(point) == 0:
    #         await ctx.send('ポイント所持者はいません。')
    #         return
    #     txt = "ポイント保持者:\n```"
    #     for member in self.bot.get_guild(int(ctx.guild.id)).members:
    #         memId = str(member.id)
    #         guiID = str(ctx.guild.id)
    #         mesid = self.bot.get_user(int(memId))
    #         try:
    #             pop = point[guiID][memId]["point"]
    #         except KeyError as e:
    #             print(e)
    #             point[str(ctx.guild.id)][str(e)] = {"name" : member.display_name,"point" : 0}
    #             pop = point[guiID][memId]["point"]
    #         txt += f"\n{mesid.display_name} : {pop}ポイント"
    #     await ctx.send(f"{txt}\n```")


    # @commands.command()
    # async def point_set(self, ctx, id: str, pop: int):
    #
    #     if ctx.author != self.bot.get_user(653785595075887104):
    #         await ctx.send("あなたには使用する権限がありません。 \nYou don't have the privilege to use this.")
    #         return
    #
    #     with open("json/point.json", mode="r", encoding='utf-8') as f:
    #         point = json.load(f)
    #         f.close()
    #
    #     point[str(ctx.guild.id)][id]["point"] = pop
    #
    #     with open("json/point.json", mode="w", encoding='utf-8') as f:
    #         WritePoint = json.dumps(point, ensure_ascii=False, indent=2)
    #         f.write(WritePoint)
    #         print('Pointの上書きに成功しました。')
    #         f.close()
    #
    #     id = self.bot.get_user(int(id))
    #     txt = f"**{id.display_name}** の所持ポイントを\n__{pop}__ に変更しました。"
    #     await ctx.send(txt)
    #     print(txt)


    # @commands.command()
    # async def point_reset(self,ctx):
    #
    #     # if ctx.author != self.bot.get_user(653785595075887104):
    #     #     await ctx.send("あなたには使用する権限がありません。 \nYou don't have the privilege to use this.")
    #     #     return
    #
    #     with open("json/point.json", mode="w", encoding='utf-8') as f:
    #         point = {}
    #         WritePoint = json.dumps(point, ensure_ascii=False, indent=2)
    #         f.write(WritePoint)
    #         await ctx.send('Pointの初期化に成功しました。')
    #         print('Pointの初期化に成功しました。')
    #         f.close()
    #
    # @commands.command()
    # async def game_reset(self,ctx):
    #
    #     with open("og.json", mode="w", encoding='utf-8') as f:
    #         og = {}
    #         WriteGame = json.dumps(og, ensure_ascii=False, indent=2)
    #         f.write(WriteGame)
    #         await ctx.send('ゲームの初期化に成功しました。')
    #         print('ゲームの初期化に成功しました。')
    #         f.close()


    # @commands.command()
    # async def point_json(self, ctx):
    #
    #     await ctx.send(file=discord.File("json/point.json"))


def setup(bot):
    bot.add_cog(VQ(bot))
