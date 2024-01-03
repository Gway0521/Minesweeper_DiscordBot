from queue import Queue
from enum import Enum
import numpy as np
import asyncio
import discord
import random

class BottomLayer(Enum):
    NORMAL_BLOCK = 0
    MINE_BLOCK = 10
    EXPLODED_BLOCK = 11

class TopLayer(Enum):
    UNSTEP_BLOCK = 0
    STEPED_BLOCK = 1
    FLAG_BLOCK = 2

class LayerType(Enum):
    BOTTOM = 0
    TOP = 1

class CommandType(Enum):
    ILLEGAL_COMMAND = 0
    TWO_WORD_COMMAND = 1
    THREE_WORD_COMMAND = 2
    FOUR_WORD_COMMAND = 3
    STOP_COMMAND = 4

class Limit(Enum):
    EMOJI_LIMIT = 199


class Board:
    '''
    遊戲的各種數據、以及其訪問函數定義
    '''
    def __init__(self, board_w = 8, board_h = 8, mine_nums = 10):
        # 初值定義
        self.board_w = board_w
        self.board_h = board_h
        self.mine_nums = mine_nums
        self.cur_unstep = board_w * board_h
        self.is_lose = False
        self.is_win  = False

        # 場地初值
        self.flag_board = np.zeros((board_h, board_w), dtype=str)
        self.board = np.zeros((board_h, board_w, len(LayerType)), dtype=np.uint8)
        shuf_arr = list(range(board_w * board_h))
        random.shuffle(shuf_arr)

        check = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
        for _ in range(mine_nums):
            mine_loc = shuf_arr.pop()
            self.set_block(mine_loc%board_w, mine_loc//board_w, LayerType.BOTTOM, BottomLayer.MINE_BLOCK)
            for x, y in check:
                check_x = mine_loc%board_w + x
                check_y = mine_loc//board_w + y
                case1 = check_x >=0 and check_x < board_w
                case2 = check_y >=0 and check_y < board_h

                if case1 and case2:
                    if not self.check_block(check_x, check_y, LayerType.BOTTOM, BottomLayer.MINE_BLOCK):
                        self.board[check_y, check_x, LayerType.BOTTOM.value] += 1

    # 成員函式
    def set_block(self, x, y, layerType, block):
        '''
        將 layerType 的 x, y 方塊轉為 block
        '''
        self.board[y, x, layerType.value] = block.value

    def check_block(self, x, y, layerType, block):
        '''
        layerType 的 x, y 方塊是否為 block
        '''
        return self.board[y, x, layerType.value] == block.value

    def set_flag(self, x, y, flag_name = ":checkered_flag:"):
        '''
        將 TopLayer 的 x, y 方塊轉為 FLAG_BLOCK，並儲存 flag_name
        '''
        self.set_block(x, y, LayerType.TOP, TopLayer.FLAG_BLOCK)
        self.flag_board[y, x] = flag_name

    def step(self, x, y):
        '''
        將 TopLayer 的 x, y 方塊轉為 STEPED_BLOCK，並減少 1 個 unstep 數量
        '''
        self.set_block(x, y, LayerType.TOP, TopLayer.STEPED_BLOCK)
        self.cur_unstep -= 1

    def remove_flag(self, x, y):
        '''
        將 TopLayer 的 x, y 方塊轉為 UNSTEP_BLOCK，並移除 flag_name
        '''
        self.set_block(x, y, LayerType.TOP, TopLayer.UNSTEP_BLOCK)
        self.flag_board[y, x] = str()

    
async def startGame(client, message, board_w, board_h, mine_nums):
    '''
    踩地雷遊戲的函式入口，定義遊戲主要的流程

    Parameters
    -----------
    client: :class:`discord.client`
        Bot 本身
    message: :class:`discord.message.Message`
        使用者發送的訊息資訊
    board_w: :class:`integer`
        場地的寬(橫向)的方塊數
    board_h: :class:`integer`
        場地的高(縱向)的方塊數
    mine_nums: :class:`integer`
        地雷數
    '''
    # 宣告變數
    sent_message_list = []
    board = Board(board_w, board_h, mine_nums)

# ==============================================================================================

    def checkTypeOfInput(userInput):
        '''
        檢查輸入是哪一種 CommandType，不顯示錯誤輸入通知

        Parameters
        -----------
        userInput: :class:`list`
            含有將 message.content.split(" ") 後數個 String 的 List
        
        Returns
        -----------
        :class:`CommandType(Enum)`
            回傳 CommandType
        '''
        if len(userInput) == 1:
            if userInput[0].lower() == "stop":
                return CommandType.STOP_COMMAND
                    
        if len(userInput) == 2:
            if len(userInput[0]) == 1 and len(userInput[1]) == 1:
                if userInput[0].isalpha() and userInput[1].isalpha():
                    select_x = ord(user_input[0].lower()) - ord('a')
                    select_y = ord(user_input[1].lower()) - ord('a')
                    if select_x < board.board_w and select_y < board.board_h:
                        return CommandType.TWO_WORD_COMMAND
            
        elif len(userInput) == 3:
            if userInput[0] in ['S', 'F', 's', 'f'] and len(userInput[1]) == 1 and len(userInput[2]) == 1:
                if userInput[1].isalpha() and userInput[2].isalpha():
                    select_x = ord(user_input[1].lower()) - ord('a')
                    select_y = ord(user_input[2].lower()) - ord('a')
                    if select_x < board.board_w and select_y < board.board_h:
                        return CommandType.THREE_WORD_COMMAND

        elif len(userInput) == 4:
            if userInput[0] in ['F', 'f'] and len(userInput[1]) == 1 and len(userInput[2]) == 1:
                if userInput[1].isalpha() and userInput[2].isalpha():
                    select_x = ord(user_input[1].lower()) - ord('a')
                    select_y = ord(user_input[2].lower()) - ord('a')
                    if select_x < board.board_w and select_y < board.board_h:
                        return CommandType.FOUR_WORD_COMMAND
        
        return CommandType.ILLEGAL_COMMAND
    

    def ExecuteCommand(userInput, commandType):
        '''
        依據 commandType 決定執行哪種 command

        Parameters
        -----------
        userInput: :class:`list`
            含有將 message.content.split(" ") 後數個 String 的 List
        commandType: :class:`CommandType(Enum)`
            Enum CommandType
        '''
        # 踩方塊指令
        if commandType == CommandType.TWO_WORD_COMMAND:
            case = 's'
            select_x = ord(user_input[0].lower()) - ord('a')
            select_y = ord(user_input[1].lower()) - ord('a')
            stepBlock(select_x, select_y)

        # 踩方塊指令 與 插拔旗指令
        elif commandType == CommandType.THREE_WORD_COMMAND:
            case = user_input[0].lower()
            select_x = ord(user_input[1].lower()) - ord('a')
            select_y = ord(user_input[2].lower()) - ord('a')
            if case == 's':
                stepBlock(select_x, select_y)
            elif case == 'f':
                if board.check_block(select_x, select_y, LayerType.TOP, TopLayer.UNSTEP_BLOCK):
                    board.set_flag(select_x, select_y)
                elif board.check_block(select_x, select_y, LayerType.TOP, TopLayer.FLAG_BLOCK):
                    board.remove_flag(select_x, select_y)

        # 插拔旗指令
        elif commandType == CommandType.FOUR_WORD_COMMAND:
            case = 'f'
            select_x = ord(user_input[1].lower()) - ord('a')
            select_y = ord(user_input[2].lower()) - ord('a')
            flag_name = user_input[3].lower()
            board.set_flag(select_x, select_y, flag_name)

        # 結束指令
        elif commandType == CommandType.STOP_COMMAND:
            board.is_lose = True
    

    async def showBoard(printOut = False):
        '''
        顯示場地，選擇印出 message 或修改 message

        Parameters
        -----------
        userInput: :class:`boolean`
            是否要印出來，若否，則只用修改 message 的方式
        '''
        # 儲存 Emoji 的 list
        num_arr = ["0⃣", "1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣"]
        alpha_arr = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"]
        msg_content_list = []

        # 第一行字串
        first_row_list = [":purple_square:"]
        # 每個字母之間加上 '\u200b' 避免合併字元
        for i, alpha in enumerate(alpha_arr[:board.board_w-1]):
            first_row_list.append(alpha)
            first_row_list.append('\u200b')
            # 每七格就多一個空格，方便玩家目視對位子
            if ((i+2) % 7 == 0):
                first_row_list.append(' ')
        first_row_list.append(alpha_arr[board.board_w-1])
        first_row_list.append('\n')
        # 先用 list 處理，再用 join 形成字串，速度較快
        first_row = ''.join(first_row_list)
        row_list = [first_row]
        emoji_ct = board.board_w + 1
        
        # 其餘所有字串
        for y, row_board in enumerate(board.board):
            
            elem_list = []
            elem_list.append(f"{alpha_arr[y]}")
            for x, block in enumerate(row_board):
                if board.check_block(x, y, LayerType.TOP, TopLayer.UNSTEP_BLOCK):
                    elem_list.append("⬜")
                elif board.check_block(x, y, LayerType.TOP, TopLayer.FLAG_BLOCK):
                    elem_list.append(board.flag_board[y, x])
                elif board.check_block(x, y, LayerType.TOP, TopLayer.STEPED_BLOCK):
                    if board.check_block(x, y, LayerType.BOTTOM, BottomLayer.NORMAL_BLOCK):
                        elem_list.append("⬛")
                    elif board.check_block(x, y, LayerType.BOTTOM, BottomLayer.MINE_BLOCK):
                        elem_list.append(":bomb:")
                    elif board.check_block(x, y, LayerType.BOTTOM, BottomLayer.EXPLODED_BLOCK):
                        elem_list.append(":boom:")
                    else:
                        elem_list.append(num_arr[block[LayerType.BOTTOM.value]])
                # 每七格就多一個空格，方便玩家目視對位子
                if ((x+2) % 7 == 0):
                    elem_list.append(" ")

            elem_list.append("\n")
            row_string = ''.join(elem_list)
            emoji_ct += board.board_w + 1
    
            # 若字串中的 Emoji 數量超過 message 限制，則將其分開並儲存在 msg_content_list 中
            if (emoji_ct > Limit.EMOJI_LIMIT.value):
                msg_content_list.append(''.join(row_list))
                row_list.clear()
                emoji_ct = board.board_w + 1
            row_list.append(row_string)
                    
        msg_content_list.append(''.join(row_list))

        # 印出訊息或修改訊息
        if printOut:
            await message.channel.send(f'''\
### 場地設定 
長：{board.board_h}  寬：{board.board_w}  地雷數量：{board.mine_nums}
### 操作說明
- 踩地雷，輸入動作(可以省略)'S'、X 座標字母、Y 座標字母，例如 `S A D` 或 `A D`
- 插旗子，輸入動作(不可省略)'F'、X 座標字母、Y 座標字母、旗子樣式(可以省略)，例如 `F A D` 或 `F A D :warning:`
- 停止遊戲 `stop`\
''')
            for msg in msg_content_list:
                sent_message = await message.channel.send(msg)
                sent_message_list.append(sent_message)
        else:
            for i, msg in enumerate(sent_message_list):
                # 如果 message 跟之前不一樣才需要修改，避免頻繁 request
                if (msg.content+"\n" != msg_content_list[i]):
                    new_msg = await msg.edit(content=msg_content_list[i])
                    sent_message_list[i] = new_msg
    

    def stepBlock(x, y):
        '''
        踩方塊，根據 x, y 的方塊的種類，決定踩下後的場地反應，修改 board。
        同時，決定是否勝利或失敗。
        '''
        # 如果是地雷就失敗，並踩完所有方塊顯示場地佈置
        if board.check_block(x, y, LayerType.BOTTOM, BottomLayer.MINE_BLOCK):
            board.set_block(x, y, LayerType.BOTTOM, BottomLayer.EXPLODED_BLOCK)
            board.is_lose = True
            for x in range(board.board_w):
                for y in range(board.board_h):
                    board.step(x, y)
            return
        
        # 已經踩過的方塊不會有反應
        elif board.check_block(x, y, LayerType.TOP, TopLayer.STEPED_BLOCK):
            return 
        
        # 已經立旗的方塊不會有反應
        elif board.check_block(x, y, LayerType.TOP, TopLayer.FLAG_BLOCK):
            return

        # 普通方塊
        elif board.check_block(x, y, LayerType.TOP, TopLayer.UNSTEP_BLOCK):
            board.step(x, y)
            
            # 如果是普通方塊(非數字方塊)，則開始做 BFS
            if board.check_block(x, y, LayerType.BOTTOM, BottomLayer.NORMAL_BLOCK):

                step_queue = Queue()
                step_queue.put((x, y))
                check = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
                
                while not step_queue.empty():
                    x, y = step_queue.get()
                    for xx, yy in check:
                        check_x = x + xx
                        check_y = y + yy
                        case1 = check_x >= 0 and check_x < board.board_w
                        case2 = check_y >= 0 and check_y < board.board_h

                        if case1 and case2:
                            if board.check_block(check_x, check_y, LayerType.TOP, TopLayer.UNSTEP_BLOCK):
                                board.step(check_x, check_y)
                                if board.check_block(check_x, check_y, LayerType.BOTTOM, BottomLayer.NORMAL_BLOCK):
                                    step_queue.put((check_x, check_y))
            
            # 判斷是否勝利
            if board.cur_unstep == board.mine_nums:
                board.is_win = True

# ==============================================================================================

    # 先印出場地
    await showBoard(printOut = True)
        
    # 遊戲的迴圈
    while (not(board.is_lose or board.is_win)):

        # 輸出 輸入
        def check(m):
            return m.channel == message.channel
        new_message = await client.wait_for('message', check=check)
        user_input = new_message.content.split(" ")

        # 執行指令
        commandType = checkTypeOfInput(user_input)
        if commandType == CommandType.ILLEGAL_COMMAND:
            continue
        else:
            ExecuteCommand(user_input, commandType)

        # 更新場地與刪除玩家訊息
        await showBoard(printOut = False)
        # if checkTypeOfInput(user_input) != ILLEGAL_COMMAND:
        await new_message.delete()
    
    # 勝利或失敗訊息
    if board.is_lose:
        await message.channel.send(f"Lose")
    else:
        await message.channel.send(f"Win")

# ==============================================================================================