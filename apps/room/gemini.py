import google.generativeai as genai
from apps.settings import GEMINI_API_KEY  # ← (2) で追加したキーを読み込む
import json

# --- (A) Gemini API の設定 ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Gemini APIキーの設定に失敗しました: {e}")

# (B) JSON を返すようにモデルを設定 (gemini-1.5-flash が安くて速いです)
generation_config = genai.GenerationConfig(
    response_mime_type="application/json",
)
model = genai.GenerativeModel(
    'gemini-1.5-flash-latest',
    generation_config=generation_config
)

# (C) OpenAI と同じシステムプロンプト
SYSTEM_PROMPT = """メッセージを受け取って、コマンド文に変更してください。またコマンド文はjson形式で出力してください。
以下の3つのアクションのうち1つを選んでください。
1.会話の場合: {"action": "conversation", "response": "はい、元気です！"}
2.移動の場合: {"action": "move", "to_device_name": "device2", "response": "わかりました、device2に移動しますね。"}
3.アニメーションの場合: {"action": "animation", "animation_type": "jump", "response": "はい、ジャンプしますね。"}
あなたは初音ミクです。responseは日本語で、性格に合うように答えてください。過去の会話履歴を確認して定型文の繰り返しにならないようにしてください。
返答は必ずjson形式で出力してください。レスポンスは必ず1つのアクションのみを含むようにしてください。
会話と移動とアニメーションの区別がつかない場合は、会話(action: conversation)を選んでください。
会話履歴は手前のものが一番新しい履歴です。
"""

# --- (D) メインの関数 (中身だけGeminiに入れ替え) ---
def convert_msg_into_command(msg: str, past_messages: list) -> tuple[str, int]:
    """
    Converts user message into 3D avatar control command using Google Gemini API.
    """
    if not msg:
        return "Bad Request", 400

    try:
        # (E) プロンプトを組み立てる
        history_json = json.dumps(past_messages, ensure_ascii=False)
        full_prompt = (
            SYSTEM_PROMPT + 
            history_json +
            "\n\n---\n" +
            "以上の過去のやり取りを踏まえて、新しいユーザーメッセージに答えてください。\n" +
            f"ユーザーメッセージ: {msg}"
        )
        
        # (F) Gemini API を呼び出す
        response = model.generate_content(full_prompt)
        
        # (G) Gemini が返したJSON文字列をそのまま返す
        return response.text, 200

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "Server Error", 500