import requests
import json

LANG = {
    # main: 主となる言語名ひとつ（国名そのままなど）
    # sub: 別名（そのまま記載）
    "BG": {
        "main": "ブルガリア"
    },
    "CS": {
        "main": "チェコ"
    },
    "DA": {
        "main": "デンマーク"
    },
    "DE": {
        "main": "ドイツ"
    },
    "EL": {
        "main": "ギリシャ"
    },
    "EN-GB": {
        "sub": ["イギリス英語", "イギリス"]
    },
    "EN-US": {
        "sub": ["アメリカ英語", "アメリカ", "英語"]
    },
    "ES": {
        "main": "スペイン"
    },
    "ET": {
        "main": "エストニア"
    },
    "FI": {
        "main": "フィンランド"
    },
    "FR": {
        "main": "フランス"
    },
    "HU": {
        "main": "ハンガリー"
    },
    "IT": {
        "main": "イタリア"
    },
    "JA": {
        "main": "日本"
    },
    "LT": {
        "main": "リトアニア"
    },
    "LV": {
        "main": "ラトビア"
    },
    "NL": {
        "main": "オランダ"
    },
    "PL": {
        "main": "ポーランド"
    },
    "PT-PT": {
        "main": "ポルトガル"
    },
    "PT-BR": {
        "sub": ["ブラジル"]
    },
    "RO": {
        "main": "ルーマニア"
    },
    "RU" : {
        "main": "ロシア"
    },
    "SK" : {
        "main": "スロバキア"
    },
    "SL": {
        "main": "スロベニア"
    },
    "SV": {
        "main": "スウェーデン"
    },
    "ZH": {
        "main": "中国"
    }
}

class TransMocho:
    def __init__(self, auth):
        self.authkey = auth
        self.LANGDIC = {}
        for k, v in LANG.items():
            if "main" in v:
                self.LANGDIC[v["main"]] = k 
                self.LANGDIC[v["main"]+"語"] = k 
            if "sub" in v:
                for l in v["sub"]:
                    self.LANGDIC[l] = k

    def apisend(self, lang, text):
        if lang not in self.LANGDIC:
            return ""
        data = {
            'auth_key': self.authkey, 
            'text': text, 
            'target_lang': self.LANGDIC[lang]
        }

        print("Translate Request:", data)
        response = requests.post(
            'https://api-free.deepl.com/v2/translate',
            data=data
        )

        print(response.status_code, response.text)

        if response.status_code >= 400:
            return ""

        json_resp = json.loads(response.text) 
        return json_resp["translations"][0]["text"] 
    
    def mocho_response(self, lang, text):
        res = self.apisend(lang, text)
        
        if res != "":
            return f"\"{res}\" だよ！！(o・▽・o)"
        else:
            return "わかんない！(o・▽・o)"
    
if __name__ == "__main__":
    t = TransMocho("auth")
    print(t.mocho_response("日本語", "はれはれゆかい"))