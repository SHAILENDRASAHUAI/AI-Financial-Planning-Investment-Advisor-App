from __future__ import annotations

from typing import List

import yfinance as yf

from .models import MarketInstrumentAnalysis


def research_instruments(symbols: List[str]) -> List[MarketInstrumentAnalysis]:
    analyses: List[MarketInstrumentAnalysis] = []
    for symbol in symbols:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
        analyses.append(
            MarketInstrumentAnalysis(
                symbol=symbol,
                long_name=info.get("longName"),
                current_price=info.get("currentPrice"),
                pe_ratio=info.get("trailingPE"),
                pb_ratio=info.get("priceToBook"),
                market_cap=info.get("marketCap"),
                revenue_growth=info.get("revenueGrowth"),
                profit_growth=info.get("earningsGrowth"),
                dividend_yield=info.get("dividendYield"),
                debt_ratio=info.get("debtToEquity"),
            )
        )
    return analyses
