import os

from fastapi import FastAPI, Header, HTTPException, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# FastAPIのインスタンス
app = FastAPI()

# LINEのアクセストークンとチャネルシークレットを環境変数から取得
line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

line_id = ""


# / にGETリクエストが来たときに呼ばれる関数
@app.get("/")
def home():
    message = "こんにちは！"

    # プッシュメッセージを送る
    line_bot_api.push_message(
        line_id,
        TextSendMessage(text=message)
    )


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

    # プロフィールを読み込み、IDを取得
    profile = line_bot_api.get_profile(event.source.user_id)

    global line_id
    line_id = profile.user_id

    # 返信する (リプライトークンを使用してテキストで返信する)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="hey")
    )
