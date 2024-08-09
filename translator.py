import json
import openai


class Prompter():
    def __init__(self, plain_doc: str):
        with open("predescription.txt", "r", encoding='UTF-8') as f:
            self.predescription = f.read()
        self.plain_doc = f"[@5]完整原文(plain text)\n```\n{plain_doc}\n```\n\n"
        self.system_prompt = self.predescription + self.plain_doc
        self.client = None

    
    def init_connection(self, key: str):
        if key is not None:
            self.client = openai.OpenAI(api_key=key)
            try:
                info = self.client.models.retrieve('gpt-4o')
                print("Model is present.")
                return "Connected."
            except openai.AuthenticationError:
                print("Invalid API key.")
                self.client = None
                return "Invalid key."
            except Exception as e:
                print(f"An error occurred: {e}")
                self.client = None
                return str(e)


    def compose_request(self, request):
        return "以下是你應當翻譯的RST原文(英文)輸入，請在兼顧語境" \
            "([@5]段落的完整原文可供參考)、用詞用字(已經在[@2]及" \
            "[@3]段落描述過)及合理的RST語法(已經在[@4]段落描述過" \
            ")的前提下將其翻譯為符合RST格式的繁體中文(臺灣)字串。" \
            "翻譯結果必須以```程式碼區塊```的方式呈現。\n" + "```\n" + request + "\n```\n"


    def translate(self, request):
        if self.client is not None:
            print("prompt sent.")
            completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": self.compose_request(request)}
                ]
            )
            print(completion.choices[0].message.content)
            return completion.choices[0].message.content[6:-3]
