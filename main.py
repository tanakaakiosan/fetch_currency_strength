import os
import json
import urllib.request
from html.parser import HTMLParser
from google import genai
from google.genai import types

# APIキーの取得
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY が設定されていません。")

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
    """Webページからテキストを安全に取得"""
    url = "https://currencystrengthmeter.org/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        html_content = response.read().decode('utf-8')
        
    parser = TextExtractor()
    parser.feed(html_content)
    return " ".join(parser.text)

def analyze():
    print("データ取得中...")
    raw_text = get_currency_page_text()
    
    prompt = f"""
以下は "currencystrengthmeter.org" から取得したHTMLテキストデータです。
このデータの中から主要通貨（USD, EUR, GBP, JPY, AUD, CAD, CHF, NZD）の強弱関係を分析し、
最も強い通貨(strongest)、最も弱い通貨(weakest)、および推奨される通貨ペアと売買方向(BUY/SELL)を特定してJSON形式で出力してください。

【取得データ】
{raw_text[:3000]}
"""
    
    print("Gemini解析中...")
    
    # 推奨されている Chat セッション経由で呼び出し
    chat = client.chats.create(
        model="gemini-2.5-flash-lite",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )
    
    response = chat.send_message(prompt)
    
    print("--- 解析結果 ---")
    print(response.text)

if __name__ == "__main__":
    analyze()
