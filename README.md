# Gemini Terminal Chatbot

`uv`(Python 3.12)와 `google-genai` Interactions API(`gemini-3.1-flash-lite`)로 동작하는 무상태(메모리 없음) 터미널 챗봇입니다.

## 설정

1. `.env.example`을 복사해 `.env` 파일을 생성하고 [Google AI Studio](https://aistudio.google.com/apikey)에서 발급받은 API 키를 입력합니다.
   ```powershell
   Copy-Item .env.example .env
   ```
2. `.env` 파일 수정:
   ```dotenv
   GEMINI_API_KEY=your_actual_api_key
   GEMINI_MODEL=gemini-3.1-flash-lite
   ```

## 실행

```powershell
uv run chatbot
```

## 테스트 및 린트

```powershell
uv run ruff check src tests
uv run pytest
```
