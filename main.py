
import os
import json

from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, render_template, request, redirect, url_for

# .envからAPIキーを読み込む
load_dotenv()

# OpenAI APIを利用するためのクライアントを作成
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
api_key = os.getenv("OPENAI_API_KEY")
print("APIキー読み込み:", api_key is not None)

# Flaskアプリを作成
app = Flask(__name__)

# 質問を一時的に保存するリスト
questions_list = []


# トップページを表示する
@app.route("/")
def home():
    return render_template(
        "index.html",
        questions=questions_list
    )


# HTMLから質問を受け取る
@app.route("/questions", methods=["POST"])
def questions():
    question = request.form.get("question", "").strip()

    # 空欄でなければ質問を追加
    if question:
        questions_list.append(question)

    return redirect(url_for("home"))


# 質問を個別に削除する
@app.route("/delete/<int:index>", methods=["POST"])
def delete_question(index):
    if 0 <= index < len(questions_list):
        questions_list.pop(index)

    return redirect(url_for("home"))


# 質問をすべて削除する
@app.route("/delete_all", methods=["POST"])
def delete_all():
    questions_list.clear()

    return redirect(url_for("home"))


# 質問を編集する
@app.route("/edit/<int:index>", methods=["POST"])
def edit_question(index):
    new_question = request.form.get("question", "").strip()

    # 指定された番号が正しく、入力が空欄でない場合に変更
    if 0 <= index < len(questions_list) and new_question:
        questions_list[index] = new_question

    return redirect(url_for("home"))


# 質問をAIでグループ分けする
@app.route("/group", methods=["POST"])
def group():
    # 質問が1件もない場合はトップページに戻る
    if not questions_list:
        return redirect(url_for("home"))

    # OpenAI APIに質問一覧を送信する
    response = client.responses.create(
        model="gpt-5.6",

        # AIに実行してほしい処理を指示する
        instructions="""
あなたは質問を分類するAIです。

与えられた複数の質問を、意味や内容が近いもの同士で
グループ化してください。

各グループには、内容を表す簡潔な名前を付けてください。

必ず以下のJSON形式で出力してください。
JSON以外の文章は出力しないでください。

{
  "groups": [
    {
      "name": "グループ名",
      "questions": ["質問1", "質問2"]
    }
  ]
}
""",

        # 保存した質問一覧をAIに渡す
        input=json.dumps(questions_list, ensure_ascii=False)
    )

    # AIの回答をJSON文字列からPythonの辞書に変換
    result = json.loads(response.output_text)

    # グループ分け結果を画面に渡す
    return render_template(
        "index.html",
        questions=questions_list,
        groups=result["groups"]
    )


# このファイルを直接実行した場合にサーバーを起動
if __name__ == "__main__":
    app.run(debug=True)
