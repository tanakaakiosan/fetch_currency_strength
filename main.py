import os
import json
import re
import requests
from bs4 import BeautifulSoup
from google import genai

# APIキーの取得
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY が設定されていません。")

client = genai.Client(api_key=api_key)

def get_currency_data():
    """Webページから直接通貨データを取得"""
    url = "https://currencystrengthmeter.org/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    # ページのHTML解析
    soup = BeautifulSoup(response.text, "html.parser")
    
    # ページ内の全テキストを取得してGeminiに直接解析させるための準備
    # (テキスト情報から通貨強弱の数値を抽出)
    page_text = soup.get_text(separator=' ', strip=True)
    return page_text[:4000]  # 必要な部分（先頭テキスト）を抽出

def analyze():
    print("データ取得中...")
    raw_text = get_currency_data()
    
    prompt = f"""
以下は "currencystrengthmeter.org" から取得したWebページのテキストデータです。
この中から各通貨（USD, EUR, GBP, JPY, AUD, CAD, CHF, NZDなど）の強弱情報や数値データを抽出し、
最も強い通貨と最も弱い通貨、および推奨トレードペア（JSON形式）を特定してください。

【取得テキストデータ】:
{raw_text}
"""
    
    print("Gemini解析中...")
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )
    
    print("--- 解析結果 ---")
    print(response.text)

if __name__ == "__main__":
    analyze()
