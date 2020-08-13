import discord
import requests
import json
import gspread
import datetime
from asyncio import sleep
import re

#async def delmessage():
#    deleted = await channel.purge(limit=2, check=is_me)
#    await channel.send('Deleted {} message(s)'.format(len(deleted)))
token = os.environ['DISCORD_BOT_TOKEN']
# APIキーの指定
apikey = "eedb415d2305d34fc77258806faa19c0"
client = discord.Client()
# 天気を調べたい都市の一覧
cities = ["Tokyo,JP"]

# APIのひな型
api = "http://api.openweathermap.org/data/2.5/weather?q={city}&APPID={key}"


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
# defチャンネル名解決
def ch_uni(search_item):
    # チャンネルリストを取得し、入力された
    chlstfile = 'ch.lst' # チャンネル変換表　"正規名,変換対象文字列１,変換対象文字列２,・・・"
#    search_item = 'bbbb' #　BOT入力待ちから取得した文字列 半角置換しておく
    search_item_str = search_item.upper()
    ld = open(chlstfile)
    lines = ld.readlines()
    ld.close()
    for line in lines:
        if line.find(search_item_str) >= 0:
            chnamelst = line[:-1].split(',')
            fullchname = chnamelst[0]
            return(fullchname)


@client.event
async def on_message(message):
    #BOTメッセージは除外
    if message.author.bot:
        return
    def check(msg):
        return msg.author == message.author
        
    #　ヘルプ
    if message.content.startswith("!!!help"):
        m = "\n!!!gm:ギルドミッション登録\n!!!gc:ギルドミッション進行中リスト表示\n"
        await message.channel.send(m)
    #お天気
    if message.content.startswith("!!!天気"):
        # 場所特定
        cities = ["Tokyo,JP"]
            
        # 温度変換（ケルビン→摂氏）
        k2c = lambda k: k - 273.15
        # 各都市の温度を取得する
        for name in cities:
            # APIのURLを得る
            url = api.format(city=name, key=apikey)
            # 実際にAPIにリクエストを送信して結果を取得する
            r = requests.get(url)
            # 結果はJSON方式なので、デコードする
            data = json.loads(r.text)
            # 結果を画面に表示
            m = "場所：" + data["name"] + "\n天気：" + data["weather"][0]["description"] + "\n最低気温：" + str(format(k2c(data["main"]["temp_max"]), '.2f')) + "℃\n最低気温：" + str(format(k2c(data["main"]["temp_min"]), '.2f')) + "℃\n湿度：" + str(data["main"]["humidity"]) + "%\n\n"
                
            await message.channel.send(m)
    # 「おはよう」で始まるか調べる
    if message.content.startswith("!!!おはよう"):
        # メッセージを書きます
        m = "おはようございます!" + message.author.mention + "さん！"
        # メッセージが送られてきたチャンネルへメッセージを送ります
        await message.channel.send(m)
    elif message.content.startswith("!!!天才"):
        # メッセージを書きます
        m = "すごい!すごぉーい!! " + message.author.mention + "さん！"
        # メッセージが送られてきたチャンネルへメッセージを送ります
        await message.channel.send(m)
        
    ##################### 「!gm」で始まるか調べる
    if message.content.startswith("!!!gm"):
        ##################### まずはチャンネル取得
        m = "どこのチャンネル?"
        # メッセージが送られてきたチャンネルへメッセージを送ります
        await message.channel.send(m)

        # ユーザからのメッセージを待つ
        wait_message = await client.wait_for("message", check=check)
        if wait_message.content == "q":
            await message.channel.send("またね〜")
        else:
            channelname = ch_uni(wait_message.content)
            # メッセージが打ち込まれたのを確認できると、出力する
            await message.channel.send("チャンネルはここでいいかな?　\n合っていたらyを押してね　間違っていたらもう一度チャンネルを教えてね\n" + channelname)
        # 取得したメッセージを書き込まれたチャンネルに出力
#        await message.channel.send(channelname)
            # ユーザからのメッセージを待つ
            wait_message = await client.wait_for("message", check=check)
            while True:
                if wait_message.content == "q":
                    message_delete()
                    break
                if channelname == "y" or wait_message.content != "y":
                    channelname = ch_uni(wait_message.content)
                    # メッセージが打ち込まれたのを確認できると、出力する
                    await message.channel.send("チャンネルはここでいいかな?　\n合っていたらyを押してね　間違っていたらもう一度チャンネルを教えてね\n" + channelname)
                    # ユーザからのメッセージを待つ
                    wait_message = await client.wait_for("message", check=check)
                if wait_message.content == "y":
        ##################### ここまで　チャンネル取得
        ##################### ギルミ内容取得
                    m = "どんなギルミするの?"
                    # メッセージが送られてきたチャンネルへメッセージを送ります
                    await message.channel.send(m)
                    # ユーザからのメッセージを待つ
                    wait_message = await client.wait_for("message", check=check)
                
                    missionname = wait_message.content
                    # メッセージが打ち込まれたのを確認できると、出力する
                    await message.channel.send("ギルミはこれでいいかな?　\n合っていたらyを押してね　間違っていたらもう一度教えてね\n" + missionname)
                    # ユーザからのメッセージを待つ
                    wait_message = await client.wait_for("message", check=check)
                
                    while True:
                        if wait_message.content == "q":
                            message_delete()
                            break
                        if wait_message.content != "y" or missionname == "y":
                            # メッセージが打ち込まれたのを確認できると、出力する
                            await message.channel.send("ギルミはこれでいいかな?　\n合っていたらyを押してね　間違っていたらもう一度教えてね\n" + wait_message.content)
                            # 取得したメッセージを書き込まれたチャンネルに出力
                            await message.channel.send(wait_message.content)
                            missionname = wait_message.content
                            # ユーザからのメッセージを待つ
                            wait_message = await client.wait_for("message", check=check)
                        if wait_message.content == "y":
                            m = "これで登録したよ\nCH　　→" + channelname + "\nギルミ→" + missionname
                            await message.channel.send(m)
                            message_delete()
                            break

        ######
        #
        ######
        #########################
        # スプシ入力
        #########################
            #スプレッドシート指定　URLから拾える。
            SPREADSHEET_KEY = '1OaR39bFJKaG5wN-tji2NBT0q4t6yaLfQZ26nvBDlFoY'
        
            #認証情報設定
            from oauth2client.service_account import ServiceAccountCredentials
        
            #2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
            #OAuth2の資格情報を使用してGoogle APIにログイン
            #秘密鍵
            credentials = ServiceAccountCredentials.from_json_keyfile_name('sherlocknote-c9c3e0f036dc.json', scope)
            gc = gspread.authorize(credentials)
            wb = gc.open_by_key(SPREADSHEET_KEY)
            ws = wb.worksheet('list')           # シート名'list'
            nowtime = datetime.datetime.now()   # 現在時刻を取得
            chname = channelname                # CH名　DCより入力された値
            mission = missionname               # ミッション内容
            status = "未"                        # 報告状況
            inputname = message.author.nick     # 入力者
            updatename = ""            # 更新者
            datas = []                          #入力用データリスト配列
            
            # リストに値を格納
            datas.append(nowtime.strftime('%Y/%m/%d %H:%M:%m')) # 日付フォーマット文字列化
            datas.append(status)                # 未済
            datas.append(chname)                # ch
            datas.append(mission)               # 内容
            datas.append(inputname)             # 入力
            datas.append(updatename)            # 更新
            
            #リスト内容をスプシ最新行に出力 [時間,未,ch,内容,入力者,更新者]
            ws.append_row(datas)
        ##################### 「!gc」で始まるか調べる
        
    if message.content.startswith("!!!gc"):
        #スプレッドシート指定　URLから拾える。
        SPREADSHEET_KEY = '1OaR39bFJKaG5wN-tji2NBT0q4t6yaLfQZ26nvBDlFoY'
          
        #認証情報設定
        from oauth2client.service_account import ServiceAccountCredentials
          
        #2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        #OAuth2の資格情報を使用してGoogle APIにログイン
        #秘密鍵
        credentials = ServiceAccountCredentials.from_json_keyfile_name('sherlocknote-c9c3e0f036dc.json', scope)
        gc = gspread.authorize(credentials)
        wb = gc.open_by_key(SPREADSHEET_KEY)
        ws = wb.worksheet('list')           # シート名'list'
        nowtime = datetime.datetime.now()   # 現在時刻を取得
        ##################### 未ステータスのギルミ内容取得
        m = "終わっていないギルミはこれだよ"
        # メッセージが送られてきたチャンネルへメッセージを送ります
        await message.channel.send(m)
        m = ""
        #########################
        # スプシ検索　status="未"
        #########################
        findcell = ws.findall("未")

        for cell in findcell:
            findtime = ws.acell('A' + str(cell.row)).value
            findch =  ws.acell('C' + str(cell.row)).value
            findmission =  ws.acell('D' + str(cell.row)).value

            m = m + "\nNo: " + str(cell.row) + "\tch: " + findch + "\t内容: " + findmission + "\t登録時間:" + findtime

#            await message.channel.send(m)
        m = "```" + m + "```"
        await message.channel.send(m)
 #update
        while True:
            m = "どれか報告済にする?報告をするならｙ・しないならｎを押してね"
            await message.channel.send(m)
            # ユーザからのメッセージを待つ
            wait_message = await client.wait_for("message", check=check)
            
            if wait_message.content == "y" or wait_message.content == "ｙ":
                updateflg = 1 #updateフラグON
                break
            elif wait_message.content == "n" or wait_message.content == "ｎ":
                updateflg = 0 #updateフラグOFF
                break
            else:
                continue
        if updateflg == 1:
            m = "どれを報告済にする?"
            await message.channel.send(m)
            # ユーザからのメッセージを待つ
            wait_message = await client.wait_for("message", check=check)
            updatetarget = wait_message.content   # 更新対象row
            updatename = message.author.nick   # 更新者名
            ws.update_cell(updatetarget,2, "済")
            ws.update_cell(updatetarget,6, updatename)
            m = "このギルミを報告済にしたよ!おつかれさま!ありがとう!!"
            await message.channel.send(m)
            updaterowtime = ws.acell('A' + str(updatetarget)).value
            updaterowch = ws.acell('C' + str(updatetarget)).value
            updaterowmission = ws.acell('D' + str(updatetarget)).value
            m = "```No: " + str(updatetarget) + "\tch: " + updaterowch + "\t内容: " + updaterowmission + "\t登録時間:" + updaterowtime + "```"
            await message.channel.send(m)

bot.run(token)
