# Discord Bot 踩地雷小遊戲

## 動機
這是一個很簡單的專案，由於最近寫 Python 都是為了應付大學課堂和專題，很少有時間可以自己寫想寫的程式，因此趁著大四的空堂時間，生出了一個可以在 Discord 上玩的踩地雷小遊戲。至於為什麼是 DC、踩地雷，純粹是因為我一直覺得踩地雷如果能和朋友一起多人玩的話感覺就很有趣。

## 啟動方法
- 先創建一個 Discord Bot，並取得它的 TOKEN，放在 bot.py 的程式碼中。
> TOKEN = '這裡輸入 Discord 的 TOKEN'
- 運行 main.py 啟動 bot。
- 用 Invite Link 把 bot 邀請進某一個群組裡，輸入指令開始遊戲。

## Bot 指令
<img src="https://github.com/Gway0521/minesweeper_DC/assets/112754491/8e5b5e42-d468-4d6e-ba1c-2c35d6ff5098" alt="Example Image" width="600" height="400">

-  啟動踩地雷
> !minesweeper
- 啟動踩地雷並設定長、寬、地雷數量
> !minesweeper [height] [width] [mine_numbers]
- 踩 (x, y) 方塊，可省略 S
> S [x] [y] 或是 [x] [y]
- 在 (x, y) 方塊插旗幟，可省略 [emoji_string] 使用預設旗幟
> F [x] [y] [emoji_string] 或是 F [x] [y]
- 結束踩地雷
> stop

## 收穫
上一次寫 Discord Bot 已經是三年前了，這次回來幾乎等於全部重新學一遍，不過相較於過去，這次主要著重練習一些打 Code 的習慣、架構和我以前沒搞清楚過的一些程式碼。
- async / await 非同步函數

這個蠻有趣的，用在 AsyncIO、慢速 I/O，像是等待使用者的輸入或某些動作。AsyncIO 和 Threading、Multiprocessing 的使用場景不同，之後寫 Winform 之類有關 UI 的專案應該會更常接觸到。
- decorator 裝飾器

平常自己寫 Code 不會用到，但是一旦開始接觸其他專案 lib 就會很常遇到，本質是封裝。[這篇寫得很好](https://stackoverflow.com/questions/52689954/what-it-really-is-client-event-discord-py)，看完之後大概理解 Discord.py 的 @client.event 和其他裝飾器的運作方式。
- Breadth-first search 廣度優先搜尋演算法

BFS 我的演算法老朋友，自從準備完 CPE 之後就沒再碰過，最近因為輔系資工的程設實驗又再一次來複習了。
- Discord 的一些 API 和限制

比如字元數量限制、貼圖數量限制、request 頻率時間限制等。

## 結論
就是個小專案，回歸寫 Code 的初心。
