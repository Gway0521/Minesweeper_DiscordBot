# Discord 踩地雷

## 研究動機
這是一個很簡單的專案，由於最近寫 Python 都是為了應付大學課堂和專題，很少有時間可以自己寫想寫的程式，因此趁著大四的空堂時間，生出了一個可以在 Discord 上玩的踩地雷小遊戲。至於為什麼是 DC、踩地雷，純粹是因為我一直覺得踩地雷如果能和朋友一起多人玩的話一定會很有趣。

## Bot 啟動方法
- 先創建一個 Discord Bot，並取得它的 TOKEN，放在 bot.py 的程式碼中。
> TOKEN = '這裡輸入 Discord 的 TOKEN'
- 運行 main.py 啟動 bot。

## Bot 指令
-  啟動踩地雷
> !minesweeper
- 啟動踩地雷並設定長、寬、地雷數量
> !minesweeper [height] [width] [mine_numbers]
- 踩 (x, y) 方塊
> S [x] [y]
可省略 S 只打
> [x] [y]

- 'F [x] [y] [emoji_string]' 在 (x, y) 方塊插旗幟，可省略 [emoji_string] 使用預設旗幟
- 'stop' 結束踩地雷
