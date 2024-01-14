import discord
import minesweeper
from discord.ext import commands

async def play_minesweeper(client, message):
    '''
    踩地雷指令的函式入口，將字串轉換為場地長寬、地雷數量，並進入 minesweeper.py 的 minesweeper.startGame()

    Parameters
    -----------
    client: :class:`discord.client`
        Bot 本身
    message: :class:`discord.message.Message`
        使用者發送的訊息資訊
    '''
    height, width, mine_nums = 0, 0, 0
    user_input_arr = str(message.content).split(" ")

    # 檢查 message 發送者、位置、以及訊息字串分割後的參數數量
    def check_arr(arr):
        if len(arr) == 3:
            if arr[0].isdigit() and arr[1].isdigit() and arr[2].isdigit():
                return 1
        return 0
    
    def check_msg(m):
        if m.author != client.user and m.channel == message.channel:
            arr = m.content.split(" ")
            return check_arr(arr)
        return 0
    
    # 根據指令使用 '!minesweeper' 或 '!minesweeper [width] [height] [mine_numbers]' 來處理
    if len(user_input_arr) == 1:

        await message.channel.send("輸入場地長、寬、地雷數量，例如 '8 8 10'：")
        new_message = await client.wait_for('message', check=check_msg, timeout=60)
        height, width, mine_nums = map(int, new_message.content.split(" "))

    elif len(user_input_arr) == 4:
        if check_arr(user_input_arr[1:]):
            height, width, mine_nums = map(int, user_input_arr[1:])

    if height * width < mine_nums:
        await message.channel.send(f"地雷數量不能大於場地大小")
        return
    
    else:
        await client.change_presence(activity=discord.Game(name="💣踩地雷"))
        await minesweeper.startGame(client, message, board_w = width, board_h = height, mine_nums = mine_nums)
        await client.change_presence(activity=None)

        


def run_discord_bot():
    '''
    程式由此進入，所有的主要互動行為的函式入口
    '''
    TOKEN = '這裡輸入 Discord 的 TOKEN'
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"{client.user} is now running!")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"{username} said: '{user_message}' ({channel})")

        #  '!' 指令的函式
        if message.content.startswith('!'):
            user_message_arr = user_message.split(" ")
            if user_message_arr[0] == "!minesweeper":
                await play_minesweeper(client, message)



    client.run(TOKEN)

