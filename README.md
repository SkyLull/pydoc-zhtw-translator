# Python Doc 繁中 GPT 翻譯助手
這是一個很簡單的翻譯助手，自動讀取你所翻譯中的 `.po` 文件並抓取其原始說明文件作為參考，並加上提示詞工程調整過後的提示並以gpt-4o進行翻譯。

提示詞請看 `translator.py` 和 `predescription.txt`，其中包含術語表可自行更新。

利用`polib`處裡所有翻譯，輸入的格式（主要是單行字數限制）會自動整理好，你只需要輸入正確譯文即可。

單次輸入約消耗8000\~30000不等的token，每次調用依據原始文件長度，約須消耗1.2\~6塊台幣不等。

`2024/08/09 gpt-4o 0.005 USD / 1k tokens`

```
Prompt 結構
系統
  [1] 基本指令
  [2] 用字用詞簡述
  [3] 術語表
  [4] rst說明
  [5] 原文.rst檔 （自動偵測並抓取當文件的原文，長度隨原文浮動）
使用者
  [1] 任務指令

輸入
  [1] 待翻譯段落
```

## 需求
  - Python = 3.11 （已受測試，其他版本未知）
  - 自備 Openai API key

## 安裝
```bash
git clone https://github.com/SkyLull/pydoc-zhtw-translator.git
cd pydoc-zhtw-translator
pip install -r requirments.txt
```

## 啟動
```bash
python main.py
```

## 使用
![image](https://github.com/user-attachments/assets/88e0f845-1f8f-472e-b342-1082a5b9e63f)

  1. 右上角按鈕打開一個 .po 檔 （必須使用pydoc-zhtw官方的repo結構，以免抓不到原始資料）。
  2. 右下角輸入你的 Api key, 並點選 connect。下方文字顯示 Connected 就是成功連上線。
  3. 上半視窗任選一個條目。
  4. 若想呼喚 GPT 協助則按下 GPT help 按鈕。
  5. 變更完譯文記得存檔。不存檔時換到其他 entry 則直接丟棄該結果。

## 已知問題
  - ubuntu 無法在界面內輸入注音
  - 點選文字列表時不能按最左邊的灰色行頭
  - ~~gpt回應格式並不嚴格，目前的 parsing 是暴力硬切，有時候會切到回應文字本體，有時後會放跑無意義文字~~
    + 變更為使用openai提供的格式化回應
  - codebase很醜

## changelog
  - V 1.0 working
  - V 1.1 working
    + 使用 structured response

## TODO
 - [ ] 跳轉功能（拔除或實作）
 - [ ] 自動儲存
 - [ ] fuzzy標記
 - [ ] 即時更新已翻譯標記
 - [ ] 加入doc strings
 - [ ] 提高prompt模組化程度
