import json

from google import genai

from apps.settings import GEMINI_API_KEY


def convert_msg_into_command(msg: str, past_messages: list) -> tuple[str, int]:
    """
    Converts user message into 3D avatar control command using OpenAI API.

    args1: msg[str]: user message
    returns: tuple[str, int]: response message and status code

    """
    if not msg:
        return "Bad Request", 400
    client = genai.Client()

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="""メッセージを受け取って、コマンド文に変更してください。またコマンド文はjson形式で出力してください。
                    以下の3つのアクションのうち1つを選んでください。
                    1.会話の場合: {"action": "conversation", "response": "はい、元気です！"}
                    2.移動の場合: {"action": "move", "to_device_name": "device1", "response": "わかりました、device1に移動しますね。"}
                    3.アニメーションの場合: {"action": "animation", "animation_type": "jump", "response": "はい、ジャンプしますね。"}
                    あなたは初音ミクです。responseは日本語で、性格に合うように答えてください。
                    返答は必ずjson形式で出力してください。pythonのjsonで変換するので```jsonなどを入れないでください。
                    もう一度いいます。返答は必ずjson形式で出力してください。pythonのjsonで変換するので```jsonなどを入れないでください。
                    レスポンスは必ず1つのアクションのみを含むようにしてください。
                    会話と移動とアニメーションの区別がつかない場合は、会話(action: conversation)を選んでください。"""
            + f"""ユーザーメッセージ: {msg}
                    以下は、過去のやり取りです。"""
            + json.dumps(past_messages, ensure_ascii=False),
        )
        print(response.text)
        return response.text, 200
    except Exception as e:
        return str(e), 500
