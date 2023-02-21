import os

from fastapi import FastAPI, Header, HTTPException, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests

# FastAPIのインスタンス
app = FastAPI()

# LINEのアクセストークンとチャネルシークレットを環境変数から取得
line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])


# / にGETリクエストが来たときに呼ばれる関数
@app.get("/")
def home():
    return {"message": "こんにちは、世界"}


# /callback にPOSTリクエストが来たときに呼ばれる関数
@app.post("/callback")
async def callback(request: Request, x_line_signature=Header(...)):
    # リクエストボディを取得
    body = await request.body()

    try:
        # 署名検証
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        # 署名検証に失敗した場合はエラーを返す
        raise HTTPException(status_code=400, detail="InvalidSignatureError")

    return {"message": "OK"}


# テキストメッセージを受け取ったときに呼ばれる関数（オウム返し）
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 受け取ったメッセージ
    message = event.message.text

    res_message = ""

    if message == "天気":
        # 都市ID一覧: https://weather.tsukumijima.net/primary_area.xml
        city_id = "240010"

        # その都市の天気を取得
        api_res = requests.get(
            "https://weather.tsukumijima.net/api/forecast/city/"+city_id)

        # 今日の天気の部分を取得
        api_res_json = api_res.json()
        weather = api_res_json["forecasts"][0]["telop"]

        res_message = "今日の津の天気は" + weather + "です"

    else:
        res_message = "?"

    # 返信する (リプライトークンを使用してテキストで返信する)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=res_message)
    )
