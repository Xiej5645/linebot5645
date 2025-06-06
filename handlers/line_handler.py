from quart import Quart, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent, UnfollowEvent, FollowEvent
import os

configuration = Configuration(access_token=os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

def setup_line_handlers(app):
    @app.route("/callback", methods=['POST'])
    def callback():
        signature = request.headers['X-Line-Signature']
        body = request.get_data(as_text=True)
        app.logger.info("Request body: " + body)
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
            abort(400)
        return 'OK'

    @handler.add(MessageEvent, message=TextMessageContent)
    def handle_message(event):
        if event.message.text != 'commands':
            return
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=event.message.text)]
                )
            )
        return        

    @handler.default()
    def default(event):
        print(event)


    @handler.add(UnfollowEvent)
    def handle_unfollow(event):
        print(event)
    
    @handler.add(FollowEvent)
    def handle_follow(event):
        print(event)