import os
import requests
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

GEMINI_API_KEY = "AIzaSyAD1JsEmsMm2CSbfxG2x1mJR-f3Y0Q9nTQ"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=" + GEMINI_API_KEY


def fetch_url_text(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return None


def summarize_text(text):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": f"次の内容を一行で要約してください: {text[:2000]}"}
                ]
            }
        ]
    }
    resp = requests.post(GEMINI_API_URL, headers=headers, json=data)
    if resp.status_code == 200:
        try:
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return "要約取得に失敗しました。"
    else:
        return "Gemini APIエラー: " + resp.text


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/summarize", methods=["POST"])
def summarize():
    url = request.form.get("url")
    if not url:
        return jsonify({"summary": "URLが指定されていません。"})
    text = fetch_url_text(url)
    if not text:
        return jsonify({"summary": "URLの内容取得に失敗しました。"})
    summary = summarize_text(text)
    return jsonify({"summary": summary})


if __name__ == "__main__":
    app.run(debug=True)
