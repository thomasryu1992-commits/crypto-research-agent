# V2.4 Patch

Included files:

- services/market_interpreter.py
- agents/report_agent.py
- services/report_post_processor.py
- services/llm_service.py

Expected terminal output:

V2.4 market interpretation applied
V2.4 post processor applied

V2.4 changes:

- Python calculates Funding Rate percent before sending to LLM.
- Python creates bias_text, structure_text, funding_text, oi_text, positioning_text.
- LLM should only summarize Python interpretation.
- Post processor removes "진입을 고려합니다" style language.
