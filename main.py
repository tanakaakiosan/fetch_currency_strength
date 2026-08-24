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

    # 複数ペア（Top 3）を出力させるプロンプト調整
    prompt = f"""
以下は "currencystrengthmeter.org" から取得したテキストデータです。
このデータの中から主要通貨（USD, EUR, GBP, JPY, AUD, CAD, CHF, NZD）の強弱関係を分析し、以下のフォーマットでJSONを出力してください。

【出力要件】
- strongest: 最も強い通貨
- weakest: 最も弱い通貨
- currency_ranks: 各通貨の強さランキング（強い順の配列）
- recommended_pairs: 強弱の差が大きい上位3つの推奨通貨ペアの配列。各要素には pair, bias ("BUY" または "SELL"), reason を含めること。

【取得データ】
{raw_text[:3000]}
"""

    print("Gemini解析中 (モデル: gemini-3.5-flash-lite)...")
    
    try:
        chat = client.chats.create(
            model="gemini-3.5-flash-lite",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            )
        )
        
        response = chat.send_message(prompt)
        result_data = json.loads(response.text)
        
        # コンソール出力
        print("\n=== 解析結果 ===")
        print(json.dumps(result_data, indent=2, ensure_ascii=False))
        print("================\n")
        
        # 2. JSONファイルとして保存 (result.json)
        output_filename = "result.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=4, ensure_ascii=False)
            
        print(f"解析結果を '{output_filename}' に保存しました。")

    except Exception as e:
        print(f"[ERROR] Gemini API呼び出しまたはファイル保存エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    analyze()
