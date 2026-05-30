import unittest

from app.engine import analyze_finances, determine_risk_profile, generate_recommendations, loan_calculator, sip_calculator
from app.models import (
    ChildExpense,
    HousingType,
    LoanCalculatorInput,
    LoanInput,
    MaritalStatus,
    RiskAssessmentAnswers,
    RiskProfile,
    SIPInput,
    UserFinancialProfile,
)


class EngineTests(unittest.TestCase):
    def _profile(self) -> UserFinancialProfile:
        return UserFinancialProfile(
            age=34,
            marital_status=MaritalStatus.married,
            family_members=4,
            dependent_family_members=2,
            children_count=1,
            children_ages=[8],
            monthly_salary=80000,
            business_income=10000,
            rental_income=5000,
            freelance_income=0,
            additional_income_sources={"bonus": 5000},
            housing_type=HousingType.rented,
            monthly_rent=15000,
            home_loan_status=False,
            loans=[
                LoanInput(
                    name="car",
                    outstanding_amount=400000,
                    interest_rate=10,
                    monthly_emi=9000,
                    remaining_tenure_months=48,
                )
            ],
            child_expenses=[
                ChildExpense(
                    name="child1",
                    school_fees=3000,
                    tuition_fees=1000,
                    transportation_expenses=1000,
                    medical_expenses=500,
                    monthly_maintenance_cost=1500,
                )
            ],
            monthly_expenses={
                "food": 8000,
                "electricity": 2000,
                "internet": 1000,
                "mobile_bills": 1200,
                "transportation": 3000,
                "insurance": 2500,
                "medical_expenses": 1000,
                "entertainment": 2500,
                "shopping": 2000,
                "subscriptions": 800,
                "miscellaneous_expenses": 2000,
            },
            existing_investments={"cash": 80000, "fixed_deposits": 120000, "mutual_funds": 50000},
            goals=[],
            risk_assessment=RiskAssessmentAnswers(
                risk_tolerance=4,
                investment_experience=4,
                time_horizon=4,
                market_understanding=3,
                loss_tolerance=4,
            ),
        )

    def test_risk_profile_logic(self):
        self.assertEqual(determine_risk_profile(2.2), RiskProfile.conservative)
        self.assertEqual(determine_risk_profile(3.1), RiskProfile.moderate)
        self.assertEqual(determine_risk_profile(4.1), RiskProfile.aggressive)

    def test_financial_analysis_surplus_and_recommendations(self):
        result = analyze_finances(self._profile())
        self.assertGreater(result.monthly_surplus, 0)
        self.assertEqual(result.risk_profile, RiskProfile.aggressive)
        self.assertTrue(any(item.category == "Index Funds" for item in result.recommendations))

    def test_non_positive_surplus_returns_stabilization_plan(self):
        recs = generate_recommendations(-1, RiskProfile.conservative)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0].category, "Stabilization Plan")

    def test_sip_and_loan_calculators(self):
        sip = sip_calculator(SIPInput(monthly_investment=10000, annual_return_percent=12, years=10))
        self.assertGreater(sip.estimated_value, sip.invested_amount)

        loan = loan_calculator(LoanCalculatorInput(principal=500000, annual_interest_percent=9.5, tenure_months=60))
        self.assertGreater(loan.total_payment, 500000)


if __name__ == "__main__":
    unittest.main()
