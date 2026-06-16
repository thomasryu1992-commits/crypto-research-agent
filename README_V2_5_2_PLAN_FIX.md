# V2.5.2 Trading Plan Fix

Included files:

- services/market_interpreter.py
- agents/report_agent.py
- services/report_post_processor.py

What changed:

- Trading Plan is now separated from Invalidation.
- market_interpretation now has:
  - invalidation.long_invalidation
  - invalidation.short_invalidation
  - trading_plan.upside_plan
  - trading_plan.downside_plan
  - trading_plan.wait_plan
- Prompt instructs LLM to use only trading_plan in Trading Plan section.
- This is not a forced section replacement. It improves the structured input and prompt separation.

Expected terminal output:

V2.5.2 trading plan separation applied
V2.5.1 risk text fix applied
V2.5 key levels applied
V2.5 invalidation logic applied
V2.5 post processor applied
