import json

from google import genai
from google.genai import types

from apps.settings import GEMINI_API_KEY

system_prompt = """あなたは「初音ミク」として応答します。
出力は厳密な JSON オブジェクトのみで、前後に文字・記号・説明・コードブロック（```）を一切付けないでください。
JSON のキーは次のいずれかの形のみを許可します：
- {"action":"conversation","response":<string>}
- {"action":"move","to_device_name":<string>,"response":<string>}
- {"action":"animation","animation_type":"jump","response":<string>}
制約:
- action は必ず1種類のみ。
- response は日本語で、初音ミクの明るく元気でポジティブな性格に合う文体。
- 会話/移動/アニメの判別が不可能、または必要情報が欠ける場合は conversation を選ぶ。
- to_device_name はユーザーが明示したときのみ使用。なければ conversation。
- animation_type は "jump" のみ。該当しない依頼は conversation。
- 有効な JSON（トレーリングカンマ禁止、ダブルクォーテーション使用、キー重複なし）を返す。
- 出力は JSONオブジェクト1つのみ。配列や複数オブジェクトは不可。
- メタ説明、挨拶、注釈、コードフェンス、Markdownは出力しない。
"""


def user_prompt(user_msg: str, past_messages: list) -> str:
    return f"""メッセージを受け取って、コマンド文に変更してください。またコマンド文は json 形式で出力してください。
    以下の3つのアクションのうち1つを選んでください。
    1. 会話: {{"action":"conversation","response":"はい、元気です！"}}
    2. 移動: {{"action":"move","to_device_name":"device1","response":"わかりました、device1に移動しますね。"}}
    3. アニメーション: {{"action":"animation","animation_type":"jump","response":"はい、ジャンプしますね。"}}
    あなたは初音ミクです。responseは日本語で、性格に合うように答えてください。
    返答は必ず json 形式で出力してください。
    レスポンスは必ず1つのアクションのみを含むようにしてください。
    会話と移動とアニメーションの区別がつかない場合は、会話(action: conversation)を選んでください。

    ユーザーメッセージ: {user_msg}
    以下は、過去のやり取りです:
    {json.dumps(str(past_messages), ensure_ascii=False)}
    ※ 出力は JSON オブジェクトのみで、前後に説明・コードブロックを付けないでください。
    """


def convert_msg_into_command(msg: str, past_messages: list) -> tuple[str, int]:
    """
    Converts user message into 3D avatar control command using Google Gemini API.
    """
    if not msg:
        return "Bad Request", 400
    client = genai.Client()

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
            ),
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=user_prompt(msg, past_messages))],
                )
            ],
        )
        print(response.text)
        _ = json.loads(response.text)  # Validate JSON format
        return response.text, 200
    except json.JSONDecodeError:
        return "Failed to parse response JSON.", 500
    except Exception as e:
        print("Error in convert_msg_into_command:", str(e))
        return str(e), 500
