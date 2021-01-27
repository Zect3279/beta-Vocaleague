from os import environ
from bot import Zect
import sys

bot = Zect()

# vocaleague.cmdから渡された引数を格納したリストの取得
argvs = sys.argv


file_name = argvs[1]

bot.load_extension(f"cogs.{file_name}")

bot.run(environ["BOT_TOKEN"])

# bot.run(BOT_TOKEN)
