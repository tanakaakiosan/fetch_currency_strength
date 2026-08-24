import os
import json
import sys
import urllib.request
from html.parser import HTMLParser
from google import genai
from google.genai import types

# 1. APIキーの存在チェック
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("[ERROR] GEMINI_API_KEY 環境変数が設定されていません。")
    sys.exit(1)

client = genai.Client(api_key=api_key)

class TextExtractor(HTMLParser):
    """HTMLからテキストのみを抽出するパーサー"""
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        cleaned = data.strip()
        if cleaned:
            self.text.append(cleaned)

def get_currency_page_text():
    """Webページからテキストを取得"""
    url = "https://currencystrengthmeter.org/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        html_content = response.read().decode('utf-8')
        
    parser = TextExtractor()
    parser.feed(html_content)
    return " ".join(parser.text)

def analyze():
    print("データ取得中...")
    try:
        raw_text = get_currency_page_text()
    except Exception as e:
        print(f"[ERROR] データ取得に失敗しました: {e}")
        sys.exit(1)

    prompt = f"""
以下は "currencystrengthmeter.org" から取得したテキストデータです。
このデータの中から主要通貨（USD, EUR, GBP, JPY, AUD, CAD, CHF, NZD）の強弱関係を分析し、
最も強い通貨(strongest)、最も弱い通貨(weakest)、推奨される通貨ペア(recommended_pair)、および売買方向(bias: "BUY" or "SELL")を特定してJSON形式で出力してください。

【取得データ】
{raw_text[:3000]}
"""

    print("Gemini解析中 (モデル: gemini-3.5-flash-lite)...")
    
    try:
        # 最新の推奨モデルを指定
        chat = client.chats.create(
            model="gemini-3.5-flash-lite",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            )
        )
        
        response = chat.send_message(prompt)
        
        print("\n=== 解析結果 (JSON) ===")
        print(response.text)
        print("=======================\n")
        print("処理が正常に完了しました。")

    except Exception as e:
        print(f"[ERROR] Gemini API呼び出しエラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    analyze()
