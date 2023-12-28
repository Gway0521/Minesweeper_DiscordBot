from queue import Queue
import numpy as np
import asyncio
import discord
import random

NORMAL_BLOCK = 0
MINE_BLOCK = 10

UNSTEP_BLOCK = 0
STEPED_BLOCK = 1
FLAG_BLOCK = 2

ILLEGAL_COMMAND = 0
TWO_WORD_COMMAND = 1
THREE_WORD_COMMAND = 2
FOUR_WORD_COMMAND = 3
STOP_COMMAND = 4

EMOJI_LIMIT = 199

class Board:
    '''
    遊戲的各種數據、以及其訪問函數定義
    '''
    def __init__(self, board_w = 8, board_h = 8, mine_nums = 10):
        self.board_w = board_w
        self.board_h = board_h
        self.mine_nums = mine_nums
        self.cur_unstep = board_w * board_h
        self._is_loose = False
        self._is_win   = False

        self.flag_board = np.zeros((board_h, board_w), dtype=str)
        self.board = np.zeros((board_h, board_w, 3), dtype=np.uint8)
        shuf_arr = list(range(board_w * board_h))
        random.shuffle(shuf_arr)

        check = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
        for i in range(mine_nums):
            mine_loc = shuf_arr.pop()
            self.board[mine_loc//board_h, mine_loc%board_w, 0] = MINE_BLOCK
            for x, y in check:
                check_x = mine_loc% board_w + x
                check_y = mine_loc//board_h + y
                case1 = check_x >=0 and check_x < board_w
                case2 = check_y >=0 and check_y < board_h

                if case1 and case2:
                    if self.board[check_y, check_x, 0] != MINE_BLOCK:
                        self.board[check_y, check_x, 0] += 1

    @property
    def is_win(self):
        return self._is_win
    @is_win.setter
    def is_win(self, value):
        self._is_win = value

    @property
    def is_loose(self):
        return self._is_loose
    @is_loose.setter
    def is_loose(self, value):
        self._is_loose = value

    def set_block(self, x, y, z, block):
        self.board[y, x, z] = block
    def step(self, x, y):
        '''
        將 x, y 方塊轉為 STEPED_BLOCK，並減少 1 個 unstep 數量
        '''
        self.board[y, x, 1] = STEPED_BLOCK
        self.cur_unstep -= 1

    def set_flag(self, x, y, flag_name = "🔳"):
        '''
        將 x, y 方塊轉為 FLAG_BLOCK
        '''
        self.board[y, x, 1] = FLAG_BLOCK
        self.flag_board[y, x] = flag_name

    def remove_flag(self, x, y):
        '''
        將 x, y 方塊轉為 UNSTEP_BLOCK
        '''
        self.board[y, x, 1] = UNSTEP_BLOCK
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
        檢查輸入是否正確，若開頭為 'S' 'F' 則會確認參數數量是否正確、X Y 位置是否越界
        在部分非法輸入時跳出提示訊息

        Parameters
        -----------
        userInput: :class:`list`
            含有將 message.content.split(" ") 後數個 String 的 List
        
        Returns
        -----------
        :class:`bool`
            回傳是否是合法輸入
        '''
        if len(userInput) == 1:
            if userInput[0].lower() == "stop":
                return STOP_COMMAND
                    
        if len(userInput) == 2:
            if len(userInput[0]) == 1 and len(userInput[1]) == 1:
                if userInput[0].isalpha() and userInput[1].isalpha():
                    return TWO_WORD_COMMAND
            
        elif len(userInput) == 3:
            if userInput[0] in ['S', 'F', 's', 'f'] and len(userInput[1]) == 1 and len(userInput[2]) == 1:
                if userInput[1].isalpha() and userInput[2].isalpha():
                    return THREE_WORD_COMMAND

        elif len(userInput) == 4:
            if userInput[0] in ['F', 'f'] and len(userInput[1]) == 1 and len(userInput[2]) == 1:
                if userInput[1].isalpha() and userInput[2].isalpha():
                    return FOUR_WORD_COMMAND
        
        return ILLEGAL_COMMAND
    

    async def showBoard(printOut = False):
        '''
        顯示場地

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
            if ((i+2) % 7 == 0):
                first_row_list.append(' ')
        first_row_list.append(alpha_arr[board.board_w-1])
        first_row_list.append('\n')
        first_row = ''.join(first_row_list)

        #first_row += ''.join([char + '\u200b' for char in alpha_arr[:board.board_w-1]] + [alpha_arr[board.board_w-1]])
        #first_row += "\n"
        row_list = [first_row]
        emoji_ct = board.board_w + 1
        
        # 其餘所有字串
        for i, row_board in enumerate(board.board):
            
            elem_list = []
            elem_list.append(f"{alpha_arr[i]}")
            for j, block in enumerate(row_board):
                if block[1] == UNSTEP_BLOCK:
                    elem_list.append("⬜")
                elif block[1] == FLAG_BLOCK:
                    elem_list.append(board.flag_board[i, j])            
                elif block[1] == STEPED_BLOCK:
                    if block[0] == NORMAL_BLOCK:
                        elem_list.append("⬛")
                    elif block[0] == MINE_BLOCK:
                        elem_list.append("🤍")
                    else:
                        elem_list.append(num_arr[block[0]])
                if ((j+2) % 7 == 0):
                    elem_list.append(" ")

            elem_list.append("\n")
            row_string = ''.join(elem_list)
            emoji_ct += board.board_w + 1
    
            # 若字串中的 Emoji 數量超過 message 限制，則將其分開並儲存在 msg_content_list 中
            if (emoji_ct > EMOJI_LIMIT):
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
                if (msg.content+"\n" != msg_content_list[i]):
                    new_msg = await msg.edit(content=msg_content_list[i])
                    sent_message_list[i] = new_msg
    

    def stepBlock(x, y):
        '''
        根據 x, y 的方塊的種類，決定踩下後的整個場地反應、是否勝利或失敗，並修改 board
        '''
        if board.board[y, x, 0] == MINE_BLOCK:

            board.is_loose = True
            for x in range(board.board_w):
                for y in range(board.board_h):
                    board.step(x, y)
            return

        elif board.board[y, x, 1] == STEPED_BLOCK:
            return 

        elif board.board[y, x, 1] == FLAG_BLOCK:
            return

        elif board.board[y, x, 1] == UNSTEP_BLOCK:

            board.step(x, y)
                
            if board.board[y, x, 0] == NORMAL_BLOCK:

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
                            if board.board[check_y, check_x, 1] == UNSTEP_BLOCK:
                                board.step(check_x, check_y)
                                if board.board[check_y, check_x, 0] == NORMAL_BLOCK:
                                    step_queue.put((check_x, check_y))
            
            if board.cur_unstep == board.mine_nums:
                board.is_win = True

# ==============================================================================================

    # 先印出場地
    await showBoard(printOut = True)
        
    # 遊戲的迴圈
    while (not(board.is_loose or board.is_win)):

        # 輸出 輸入
        def check(m):
            return m.channel == message.channel
        new_message = await client.wait_for('message', check=check)
        user_input = new_message.content.split(" ")

        # 如果不符合輸入標準則跳出提示 再從頭運行迴圈
        case, select_x, select_y, flag_name = 0, 0, 0, ""
        if checkTypeOfInput(user_input) == ILLEGAL_COMMAND:
            continue
        elif checkTypeOfInput(user_input) == TWO_WORD_COMMAND:
            case = 's'
            select_x = ord(user_input[0].lower()) - ord('a')
            select_y = ord(user_input[1].lower()) - ord('a')
            stepBlock(select_x, select_y)
        elif checkTypeOfInput(user_input) == THREE_WORD_COMMAND:
            case = user_input[0].lower()
            select_x = ord(user_input[1].lower()) - ord('a')
            select_y = ord(user_input[2].lower()) - ord('a')
            if case == 's':
                stepBlock(select_x, select_y)
            elif case == 'f':
                if board.board[select_y, select_x, 1] == UNSTEP_BLOCK:
                    board.set_flag(select_x, select_y)
                elif board.board[select_y, select_x, 1] == FLAG_BLOCK:
                    board.remove_flag(select_x, select_y)
        elif checkTypeOfInput(user_input) == FOUR_WORD_COMMAND:
            case = 'f'
            select_x = ord(user_input[1].lower()) - ord('a')
            select_y = ord(user_input[2].lower()) - ord('a')
            flag_name = user_input[3].lower()
            board.set_flag(select_x, select_y, flag_name)
        elif checkTypeOfInput(user_input) == STOP_COMMAND:
            board.is_loose = True

        # 更新場地與刪除玩家訊息
        await showBoard(printOut = False)
        if checkTypeOfInput(user_input) != ILLEGAL_COMMAND:
            await new_message.delete()
    
    if board.is_loose:
        await message.channel.send(f"Lose")
    else:
        await message.channel.send(f"Win")

# ==============================================================================================




if __name__ == '__main__':
    startGame()