from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .engine import (
    analyze_finances,
    answer_financial_coach,
    goal_progress_summary,
    loan_calculator,
    portfolio_template,
    sip_calculator,
)
from .market import research_instruments
from .models import (
    CoachAnswer,
    CoachQuestion,
    DISCLAIMER,
    FinancialAnalysisResult,
    LoanCalculatorInput,
    LoanCalculatorResult,
    MarketInstrumentAnalysis,
    RiskProfile,
    SIPInput,
    SIPResult,
    UserFinancialProfile,
)

router = APIRouter(prefix="/api/v1")


class MarketResearchRequest(BaseModel):
    symbols: List[str] = Field(default_factory=list)


class PortfolioRequest(BaseModel):
    risk_profile: RiskProfile


@router.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "disclaimer": DISCLAIMER}


@router.post("/analysis", response_model=FinancialAnalysisResult)
def financial_analysis(profile: UserFinancialProfile) -> FinancialAnalysisResult:
    return analyze_finances(profile)


@router.post("/market-research", response_model=List[MarketInstrumentAnalysis])
def market_research(payload: MarketResearchRequest) -> List[MarketInstrumentAnalysis]:
    return research_instruments(payload.symbols)


@router.post("/portfolio")
def portfolio(payload: PortfolioRequest) -> Dict[str, int]:
    return portfolio_template(payload.risk_profile)


@router.post("/coach", response_model=CoachAnswer)
def coach(payload: CoachQuestion) -> CoachAnswer:
    return answer_financial_coach(payload)


@router.post("/calculators/sip", response_model=SIPResult)
def calculate_sip(payload: SIPInput) -> SIPResult:
    return sip_calculator(payload)


@router.post("/calculators/loan", response_model=LoanCalculatorResult)
def calculate_loan(payload: LoanCalculatorInput) -> LoanCalculatorResult:
    return loan_calculator(payload)


@router.post("/goals/progress")
def goal_progress(payload: UserFinancialProfile) -> Dict[str, float]:
    return goal_progress_summary(payload)
