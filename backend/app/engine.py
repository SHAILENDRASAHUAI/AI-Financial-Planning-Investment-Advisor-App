from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
from typing import Dict, List

from .models import (
    AllocationRecommendation,
    CoachAnswer,
    CoachQuestion,
    DISCLAIMER,
    FinancialAnalysisResult,
    LoanCalculatorInput,
    LoanCalculatorResult,
    RiskProfile,
    SIPInput,
    SIPResult,
    UserFinancialProfile,
)

ESSENTIAL_EXPENSE_KEYS = {
    "food",
    "electricity",
    "internet",
    "mobile_bills",
    "transportation",
    "insurance",
    "medical_expenses",
    "rent",
}


def determine_risk_profile(score: float) -> RiskProfile:
    if score <= 2.4:
        return RiskProfile.conservative
    if score <= 3.7:
        return RiskProfile.moderate
    return RiskProfile.aggressive


def _clamp_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def analyze_finances(profile: UserFinancialProfile) -> FinancialAnalysisResult:
    total_income = profile.total_monthly_income
    expenses = sum(profile.monthly_expenses.values())
    total_child_expenses = sum(child.total for child in profile.child_expenses)
    loan_emi = sum(loan.monthly_emi for loan in profile.loans)
    housing_emi = profile.home_loan_monthly_emi if profile.home_loan_status else 0
    rent = profile.monthly_rent if profile.housing_type.value == "rented" else 0
    total_emi = loan_emi + housing_emi
    essential_costs = sum(
        amount
        for key, amount in profile.monthly_expenses.items()
        if key.lower() in ESSENTIAL_EXPENSE_KEYS
    ) + rent

    monthly_surplus = total_income - expenses - total_emi - essential_costs - total_child_expenses
    savings_rate = (max(monthly_surplus, 0) / total_income * 100) if total_income else 0
    debt_to_income = (total_emi / total_income * 100) if total_income else 0

    risk_answers = profile.risk_assessment
    risk_avg = (
        risk_answers.risk_tolerance
        + risk_answers.investment_experience
        + risk_answers.time_horizon
        + risk_answers.market_understanding
        + risk_answers.loss_tolerance
    ) / 5
    risk_profile = determine_risk_profile(risk_avg)

    debt_risk_score = _clamp_score(100 - (debt_to_income * 1.6))
    savings_score = _clamp_score(savings_rate * 2.2)
    emergency_months = _calculate_emergency_buffer_months(profile, expenses + total_child_expenses)
    emergency_score = _clamp_score(emergency_months / 6 * 100)
    investment_readiness = _clamp_score((savings_score * 0.5) + (debt_risk_score * 0.2) + (emergency_score * 0.3))
    financial_health = _clamp_score((debt_risk_score * 0.35) + (savings_score * 0.35) + (investment_readiness * 0.3))

    recommendations = generate_recommendations(monthly_surplus, risk_profile)

    return FinancialAnalysisResult(
        total_monthly_income=round(total_income, 2),
        total_monthly_expenses=round(expenses, 2),
        total_monthly_emi=round(total_emi, 2),
        total_child_expenses=round(total_child_expenses, 2),
        monthly_surplus=round(monthly_surplus, 2),
        savings_rate_percent=round(savings_rate, 2),
        debt_to_income_ratio_percent=round(debt_to_income, 2),
        financial_health_score=financial_health,
        debt_risk_score=debt_risk_score,
        savings_score=savings_score,
        investment_readiness_score=investment_readiness,
        risk_profile=risk_profile,
        recommendations=recommendations,
    )


def _calculate_emergency_buffer_months(profile: UserFinancialProfile, monthly_spend: float) -> float:
    emergency_assets = profile.existing_investments.get("cash", 0) + profile.existing_investments.get(
        "fixed_deposits", 0
    )
    if monthly_spend <= 0:
        return 0
    return emergency_assets / monthly_spend


def _allocation_template_for_risk(risk_profile: RiskProfile) -> Dict[str, float]:
    if risk_profile == RiskProfile.conservative:
        return OrderedDict(
            {
                "Emergency Fund": 0.20,
                "Debt Funds": 0.35,
                "Index Funds": 0.20,
                "Gold ETF": 0.15,
                "Cash Reserve": 0.10,
            }
        )
    if risk_profile == RiskProfile.moderate:
        return OrderedDict(
            {
                "Emergency Fund": 0.20,
                "Index Funds": 0.32,
                "Flexi Cap Mutual Funds": 0.20,
                "Debt Funds": 0.15,
                "Gold ETF": 0.08,
                "Cash Reserve": 0.05,
            }
        )
    return OrderedDict(
        {
            "Emergency Fund": 0.15,
            "Index Funds": 0.35,
            "Flexi Cap Mutual Funds": 0.25,
            "Large & Midcap Stocks/ETFs": 0.15,
            "Gold ETF": 0.05,
            "Cash Reserve": 0.05,
        }
    )


def generate_recommendations(monthly_surplus: float, risk_profile: RiskProfile) -> List[AllocationRecommendation]:
    if monthly_surplus <= 0:
        return [
            AllocationRecommendation(
                category="Stabilization Plan",
                amount=0,
                explanation=(
                    "Your current monthly surplus is non-positive. Focus on reducing discretionary "
                    "spending and high-interest debt before starting new investments."
                ),
            )
        ]

    allocation = _allocation_template_for_risk(risk_profile)
    recommendations: List[AllocationRecommendation] = []

    for category, ratio in allocation.items():
        amount = round(monthly_surplus * ratio, 2)
        recommendations.append(
            AllocationRecommendation(
                category=category,
                amount=amount,
                explanation=(
                    f"Allocate {int(ratio * 100)}% of your monthly surplus to {category.lower()} "
                    "to balance growth, stability, and liquidity."
                ),
            )
        )
    return recommendations


def answer_financial_coach(question: CoachQuestion) -> CoachAnswer:
    language = question.language.strip().lower()
    question_text = question.question.strip()

    if language in {"hindi", "hi"}:
        answer = (
            f"आपका प्रश्न: '{question_text}'। सुरक्षित योजना के लिए पहले 6 महीने का आपातकालीन फंड रखें, "
            "फिर जोखिम प्रोफाइल के अनुसार SIP निवेश करें और महंगे कर्ज को प्राथमिकता से चुकाएँ।"
        )
        return CoachAnswer(language="hindi", answer=answer)

    if language in {"hinglish"}:
        answer = (
            f"Aapka sawaal: '{question_text}'. Pehle emergency fund (6 months expenses) build karo, "
            "phir risk profile ke hisaab se SIP start karo aur high-interest loan jaldi close karo."
        )
        return CoachAnswer(language="hinglish", answer=answer)

    answer = (
        f"Your question: '{question_text}'. Build an emergency fund covering 6 months of expenses, "
        "prioritize high-interest debt repayment, and then automate monthly SIPs aligned to your risk profile."
    )
    return CoachAnswer(language="english", answer=answer)


def sip_calculator(data: SIPInput) -> SIPResult:
    monthly_rate = data.annual_return_percent / 12 / 100
    months = data.years * 12
    invested = data.monthly_investment * months
    future_value = data.monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
    return SIPResult(invested_amount=round(invested, 2), estimated_value=round(future_value, 2))


def loan_calculator(data: LoanCalculatorInput) -> LoanCalculatorResult:
    monthly_rate = data.annual_interest_percent / 12 / 100
    factor = (1 + monthly_rate) ** data.tenure_months
    emi = data.principal * monthly_rate * factor / (factor - 1)
    total_payment = emi * data.tenure_months
    total_interest = total_payment - data.principal
    return LoanCalculatorResult(
        emi=round(emi, 2),
        total_interest=round(total_interest, 2),
        total_payment=round(total_payment, 2),
    )


def goal_progress_summary(profile: UserFinancialProfile) -> Dict[str, float]:
    current_year = datetime.utcnow().year
    total_investments = sum(profile.existing_investments.values())
    result: Dict[str, float] = {}
    for goal in profile.goals:
        years_left = max(goal.target_year - current_year, 0)
        weight = {"high": 1.0, "medium": 0.7, "low": 0.5}[goal.priority_level.value]
        projected = total_investments * (1.08**years_left) * weight
        probability = 0 if goal.goal_amount <= 0 else min(100.0, (projected / goal.goal_amount) * 100)
        result[goal.goal_name] = round(probability, 2)
    return result


def portfolio_template(risk_profile: RiskProfile) -> Dict[str, int]:
    if risk_profile == RiskProfile.conservative:
        return {"Debt": 50, "Index Funds": 25, "Gold": 15, "Cash": 10}
    if risk_profile == RiskProfile.moderate:
        return {"Equity": 60, "Debt": 20, "Gold": 10, "Cash": 10}
    return {"Equity": 80, "Debt": 10, "Gold": 5, "Cash": 5}
