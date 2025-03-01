from flask import Flask, render_template, request, session, jsonify
import openai
import os
import logging

# 環境変数から API キーを取得
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ログ設定
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = "supersecretkey"



# 質問リスト
questions = [
    {
        "question": "居住環境を教えてください",
        "choices": ["一戸建て", "集合住宅(単身向け)", "集合住宅(家族向け)"]
    },
    {
        "question": "家族構成を教えてください",
        "choices": ["一人暮らし", "既婚(子ども無し)", "既婚(子ども有り)"]
    },
    {
        "question": "主に世話をする方の年齢は？",
        "choices": ["～22歳", "23歳～35歳", "36歳～60歳", "61歳～"]
    },
    {
        "question": "犬に求める性格は？",
        "choices": ["穏やかで落ち着いている", "活発で遊び好き", "警戒心が強く番犬向き"]
    },
    {
        "question": "飼いたいサイズは？",
        "choices": ["小型犬（10kg未満）", "中型犬（10kg以上25kg未満）", "大型犬（25kg以上）"]
    },
    {
        "question": "希望する手入れの頻度は？",
        "choices": ["毎月サロンでのトリミングが可能", "週に数回のブラッシングが可能", "できるだけ手入れが少ない"]
    },
    {
        "question": "1日に犬と過ごせる平均時間は？",
        "choices": ["1～2時間", "2～4時間", "4時間以上"]
    },
    {
        "question": "毎日の散歩で歩ける時間は？",
        "choices": ["30分以内", "30分～1時間", "1時間以上"]
    }
]

@app.route("/")
def home():
    session.clear()
    session["answers"] = []
    session["current_question"] = 0
    return render_template("chat.html")

@app.route("/next_question", methods=["POST"])
def next_question():
    user_answer = request.json.get("answer")
    if user_answer:
        session["answers"].append(user_answer)
    question_index = session["current_question"]
    if question_index < len(questions):
        session["current_question"] += 1
        return jsonify({
            "question": questions[question_index]["question"],
            "choices": questions[question_index]["choices"]
        })
    else:
        return jsonify({"end": True})

@app.route("/get_recommendation", methods=["POST"])
def get_recommendation():
    user_answers = session.get("answers", [])

    prompt = f"以下の情報をもとに、適した犬種を2つ提案してください:\n{user_answers}"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは犬種診断の専門家です。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )
        result_text = response.choices[0].message.content.strip()

    except Exception as e:
        logging.error(f"OpenAI API エラー: {str(e)}")
        result_text = f"エラーが発生しました: {str(e)}"

    return jsonify({"result": result_text, "prompt": prompt})

# 🚀 Railway で PORT を環境変数から取得
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
