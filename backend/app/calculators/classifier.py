from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from backend.app.models.regulatory import RegulatoryRule


class ClassificationResult:
    def __init__(
        self,
        rule_id: str,
        rule_version: str,
        category_code: str,
        factor: Decimal,
        framework: str,
        rule_type: str,
        source_reference: str,
        methodology_note: str,
    ):
        self.rule_id = rule_id
        self.rule_version = rule_version
        self.category_code = category_code
        self.factor = factor
        self.framework = framework
        self.rule_type = rule_type
        self.source_reference = source_reference
        self.methodology_note = methodology_note

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_version": self.rule_version,
            "category_code": self.category_code,
            "factor": float(self.factor),
            "framework": self.framework,
            "rule_type": self.rule_type,
            "source_reference": self.source_reference,
            "methodology_note": self.methodology_note,
        }


class RegulatoryClassifier:
    """
    Centralized, deterministic classification engine mapping banking instruments,
    counterparties, maturities, and encumbrance states to Basel regulatory factors.
    """

    def __init__(self, db: Session):
        self.db = db
        self.rules: list[RegulatoryRule] = db.query(RegulatoryRule).filter_by(active=True).all()

    def classify_position(
        self,
        product_code: str,
        side: str,
        counterparty_type: str,
        residual_maturity_days: int,
        is_insured: bool = False,
        is_operational: bool = False,
        is_encumbered: bool = False,
        risk_weight: float = 100.0,
    ) -> dict[str, ClassificationResult]:
        """
        Returns classifications for both NSFR and LCR frameworks.
        """
        results: dict[str, ClassificationResult] = {}
        
        # 1. Available Stable Funding (ASF) for liabilities & equity
        if side in ("LIABILITY", "EQUITY"):
            rule = self._match_asf_rule(
                product_code, counterparty_type, residual_maturity_days, is_insured, is_operational
            )
            if rule:
                results["ASF"] = ClassificationResult(
                    rule_id=rule.rule_id,
                    rule_version=rule.rule_version,
                    category_code=f"CAT_{rule.rule_id.replace('-', '_')}",
                    factor=rule.factor,
                    framework="NSFR",
                    rule_type="ASF",
                    source_reference=rule.source_reference,
                    methodology_note=rule.methodology_note,
                )

        # 2. Required Stable Funding (RSF) for assets & OBS
        if side in ("ASSET", "OFF_BALANCE_SHEET"):
            rule = self._match_rsf_rule(
                product_code, counterparty_type, residual_maturity_days, is_encumbered, risk_weight
            )
            if rule:
                results["RSF"] = ClassificationResult(
                    rule_id=rule.rule_id,
                    rule_version=rule.rule_version,
                    category_code=f"CAT_{rule.rule_id.replace('-', '_')}",
                    factor=rule.factor,
                    framework="NSFR",
                    rule_type="RSF",
                    source_reference=rule.source_reference,
                    methodology_note=rule.methodology_note,
                )

        return results

    def _match_asf_rule(
        self,
        product_code: str,
        counterparty_type: str,
        tenor: int,
        is_insured: bool,
        is_operational: bool,
    ) -> RegulatoryRule | None:
        # Capital & Long-Term Liabilities (>= 1Y)
        if tenor >= 365 or product_code in ("EQUITY_CET1", "TIER2_SUB_DEBT", "SR_TERM_NOTES"):
            return self._find_rule("RULE-ASF-01")

        # Stable Retail Deposits
        if "RET" in product_code and is_insured:
            return self._find_rule("RULE-ASF-02")

        # Less Stable Retail Deposits
        if "RET" in product_code and not is_insured:
            return self._find_rule("RULE-ASF-03")

        # Operational Corporate Deposits
        if is_operational or "OPERATIONAL" in product_code:
            return self._find_rule("RULE-ASF-05")

        # Non-Financial Corporate Deposits & Funding < 1Y
        if counterparty_type in ("NON_FINANCIAL_CORPORATE", "SOVEREIGN", "PSE"):
            return self._find_rule("RULE-ASF-04")

        # Wholesale Funding 6M to < 1Y
        if 180 <= tenor < 365 or product_code == "CERT_OF_DEPOSIT":
            return self._find_rule("RULE-ASF-06")

        # Short Financial Counterparty Liabilities < 6M
        return self._find_rule("RULE-ASF-07")

    def _match_rsf_rule(
        self,
        product_code: str,
        counterparty_type: str,
        tenor: int,
        is_encumbered: bool,
        risk_weight: float,
    ) -> RegulatoryRule | None:
        if is_encumbered or product_code == "PREMISES_NPL":
            return self._find_rule("RULE-RSF-08")

        if product_code == "CASH_RESERVES":
            return self._find_rule("RULE-RSF-01")

        if product_code == "SOV_BOND_L1":
            return self._find_rule("RULE-RSF-02")

        if product_code == "CORP_BOND_L2A":
            return self._find_rule("RULE-RSF-04")

        if product_code == "INTERBANK_REV_REPO":
            return self._find_rule("RULE-RSF-03")

        if product_code == "PRIME_MORTGAGE":
            return self._find_rule("RULE-RSF-05")

        if product_code == "CORP_SHORT_LOAN" or tenor < 365:
            return self._find_rule("RULE-RSF-05")

        if product_code == "CORP_LONG_LOW_RW" or risk_weight <= 35.0:
            return self._find_rule("RULE-RSF-06")

        if product_code in ("CORP_LONG_STD_RW", "RETAIL_UNSECURED"):
            return self._find_rule("RULE-RSF-07")

        if product_code == "COMMITTED_CREDIT":
            return self._find_rule("RULE-RSF-09")

        return self._find_rule("RULE-RSF-08")

    def _find_rule(self, rule_id: str) -> RegulatoryRule | None:
        for r in self.rules:
            if r.rule_id == rule_id:
                return r
        return None
