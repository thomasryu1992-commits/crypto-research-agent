# Crypto Research Agent V2.3

V2.3 improves report wording quality.

Key changes:
- No direct entry/exit commands
- Uses “상방/하방 시나리오가 강화됩니다” wording
- Uses “시장 전체 OI” instead of long/short OI
- Separates previous snapshot change from 24h change
- Adds post-processing to clean risky wording

Run:
```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
ollama pull qwen2.5:3b
python main.py
```
