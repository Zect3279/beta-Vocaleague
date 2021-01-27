# start.py

import discord
from discord.ext import commands

import json
import random
import asyncio
import os
import sys
from dispander import dispand


global anser
anser = False

# vq.cmdから渡された引数を格納したリストの取得
argvs = sys.argv


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.PlNa = []
        self.PlId = []
        self.open = []
        self.joiner = False


    @commands.Cog.listener()
    async def on_ready(self):
        print('Start is Ready!')


    @commands.Cog.listener()
    async def on_message(self, message):
        await dispand(message)

    @commands.command()
    async def start(self,ctx):
        ChaId = ctx.channel.id
        GuiId = ctx.guild.id
        self.open.append(ChaId)
        com = f'start vocaleague.bat vq all {ChaId} {GuiId}'
        await ctx.send("確認...\nゲームを開始します。")
        print(com)
        os.system(com)
        print(f"＝＝＝＝＝＝＝＝＝＝\nギルド：{ctx.guild.name}\nチャンネル：{ctx.channel.name}\n＝＝＝＝＝＝＝＝＝＝")

    @commands.command()
    async def end(self,ctx):
        if ctx.channel.id not in self.open:
            return
        self.open.remove(ctx.channel.id)

    @commands.command()
    async def vq(self,ctx,many=1):
        if len(self.open) == 0:
            await ctx.send(f"ここでは起動されていません。\n`/start`でゲームを起動してください。")
        return


    @commands.command()
    async def game(self, ctx):
        ChaId = ctx.channel.id
        await ctx.send("""確認...
30秒後にゲームを開始します。
参加者は`/ok`を入力してください。

自由参加を希望する場合は、代表者が`/all`と入力してください。
""")
        await asyncio.sleep(10)
        if self.joiner == False:
            await ctx.send("参加が確認されませんでした。\nインスタンスを終了します。")
            return
        if self.PlNa == "all":
            com = f"start vocaleague.bat vq all {ChaId}"
        else:
            com = f"start vocaleague.bat vq {self.PlId} {ChaId} {self.PlNa}"
        await ctx.send(f"30秒経過...\nゲームの起動を開始します。")
        print(com)
        os.system(com)

    @commands.command()
    async def point(self, ctx, user: discord.User = None):
        target_user = user if user else ctx.author
        user_data = await self.db.get_user(target_user.id)
        if user_data is None:
            await ctx.send("まだ登録されていません")
            return

        await ctx.send(f"{user_data.name} の所持ポイント\n{user_data.point} Point")
        return

    @commands.command()
    async def ranking(self, ctx: commands.Context) -> None:
        users_ranking = await self.db.get_user_rankings()
        ranking_message = "```\n"

        for user_ranking in users_ranking:
            user = self.bot.get_user(user_ranking[0].id)
            user_data = user_ranking[0]

            ranking_message += f"{user_ranking[1]}位: {user_data.name}, Point: {user_data.point}\n"

        if not discord.utils.find(lambda u: u[0].id == ctx.author.id, users_ranking):
            if rank := await self.db.get_user_ranking(ctx.author.id):
                user_data = await self.bot.db.get_user(ctx.author.id)
                ranking_message += f"\n{rank}位: {user_data.name}, Point: {user_data.point}"

        await ctx.send(ranking_message + "```")

    @commands.command()
    async def join(self, ctx):
        user = await self.db.get_user(ctx.author.id)
        if user is not None:
            await ctx.send("あなたはすでに登録されています")
            return

        await self.db.create_user(ctx.author.id)
        await ctx.send("ユーザー登録を行いました")

    # @commands.command()
    # async def all(self, ctx):
    #     await ctx.send("自由参加が指定されました")
    #     self.PlNa = "all"
    #     self.joiner = True

    # @commands.command()
    # async def ok(self, ctx):
    #     AId = str(ctx.author.id)
    #     ANa = str(ctx.author.display_name)
    #     if AId in self.PlId:
    #         await ctx.send(f"拒否...\n__{ANa}__ はすでに参加しています。")
    #         return
    #     self.PlId.append(AId)
    #     self.PlNa.append(ANa)
    #     await ctx.send(f"承諾...\n__**{ANa}**__ の参加が確認されました。")
    #     print(self.PlId)
    #     print(self.PlNa)
    #     self.joiner = True

    # @commands.command()
    # async def no(self,ctx):
    #     await ctx.send(f"承諾...\n__**{}**__ の参加が取り消されました。")






# com = f"py -3 vocaleague.bat vq.vq {PlayerList} {GuildId} {ChannelId} {GameData}"
# print(com)
# os.system(com)

# j = {
#     guild.id:{
#         channel.id{
#             "player" : ["list of user.id"],
#             "guild" : guild.id,
#             "channel" : channel.id
#         },
#         channel.id{
#             "player" : ["list of user.id"],
#             "guild" : guild.id,
#             "channel" : channel.id
#         },
#         channel.id{
#             "player" : ["list of user.id"],
#             "guild" : guild.id,
#             "channel" : channel.id
#         }
#     },
#     guild.id:{
#         channel.id{
#             "player" : ["list of user.id"],
#             "guild" : guild.id,
#             "channel" : channel.id
#         }
#     }
# }



def setup(bot):
    bot.add_cog(Game(bot))
