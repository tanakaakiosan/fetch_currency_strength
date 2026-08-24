import os
import json
import urllib.request
from google import genai

# GitHub Secrets等から環境変数を取得
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY が設定されていません。")

# Clientを初期化（引数なしでも自動認識されます）
client = genai.Client(api_key=api_key)

def get_currency_data():
    url = "https://currencystrengthmeter.org/data.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://currencystrengthmeter.org/"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def analyze():
    raw_data = get_currency_data()
    
    prompt = f"以下の通貨強弱データを分析し、最も強い通貨と弱い通貨、おすすめのペアを決定してください:\n{json.dumps(raw_data)}"
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )
    
    print(response.text)

if __name__ == "__main__":
    analyze()
