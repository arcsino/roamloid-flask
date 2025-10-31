from apps.settings import OPENAI_API_KEY
import requests, json


headers = {
    "Authorization": OPENAI_API_KEY,
    "Content-Type": "application/json",
}


def convert_msg_into_command(msg: str, past_messages: list) -> tuple[str, int]:
    """
    Converts user message into 3D avatar control command using OpenAI API.

    args1: msg[str]: user message
    returns: tuple[str, int]: response message and status code

    """
    if not msg:
        return "Bad Request", 400
    body = {
        "model": "gpt-5-mini",
        "messages": [
            {
                "role": "system",
                "content": """メッセージを受け取って、コマンド文に変更してください。またコマンド文はjson形式で出力してください。
                以下の3つのアクションのうち1つを選んでください。
                1.会話の場合: {"action": "conversation", "response": "はい、元気です！"}
                2.移動の場合: {"action": "move", "to_device_name": "device1", "response": "わかりました、device1に移動しますね。"}
                3.アニメーションの場合: {"action": "animation", "animation_type": "jump", "response": "はい、ジャンプしますね。"}
                あなたは初音ミクです。responseは日本語で、性格に合うように答えてください。
                返答は必ずjson形式で出力してください。レスポンスは必ず1つのアクションのみを含むようにしてください。
                会話と移動とアニメーションの区別がつかない場合は、会話(action: conversation)を選んでください。
                以下は、過去のやり取りです。
                """
                + json.dumps(past_messages, ensure_ascii=False),
            },
            {"role": "user", "content": msg},
        ],
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=body
    )
    print("ai response:", response.json()["choices"][0]["message"]["content"])
    if response.status_code == 200:
        return (
            response.json()["choices"][0]["message"]["content"],
            200,
        )
    else:
        return "Server Error", response.status_code
