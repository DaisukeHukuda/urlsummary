import os
import requests
from flask import Flask, request, render_template, jsonify
from bs4 import BeautifulSoup
from dotenv import load_dotenv

app = Flask(__name__)

# .envからAPIキーを取得
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"


def fetch_url_text(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # script, style, head, title, metaタグを除去
        for tag in soup(["script", "style", "head", "title", "meta", "noscript"]):
            tag.decompose()
        visible_text = ' '.join(soup.stripped_strings)
        return visible_text
    except Exception:
        return None


def summarize_text(text):
    if not GEMINI_API_KEY:
        return "Gemini APIキーが設定されていません。"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": f"次の内容を一文で要約してください: {text[:2000]}"}
                ]
            }
        ]
    }
    try:
        resp = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=15)
        if resp.status_code == 200:
            try:
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                return "要約取得に失敗しました。"
        else:
            return f"Gemini APIエラー: {resp.status_code}"
    except Exception:
        return "Gemini APIへのリクエストに失敗しました。"


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/summarize", methods=["POST"])
def summarize():
    url = request.form.get("url")
    if not url:
        return jsonify({"summary": "URLが指定されていません。"})
    text = fetch_url_text(url)
    if not text or len(text.strip()) == 0:
        return jsonify({"summary": "URLの内容取得に失敗しました。"})
    summary = summarize_text(text)
    return jsonify({"summary": summary})


if __name__ == "__main__":
    app.run(debug=True)
