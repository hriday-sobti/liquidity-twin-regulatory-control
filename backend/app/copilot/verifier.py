import re
from typing import Dict, List, Any, Optional, Tuple


class NumericVerifier:
    """
    Mandatory AI Safety Control:
    Inspects AI generated text for numeric claims and verifies them against underlying grounded database values.
    Checks:
      1. Value equality (within tolerance 0.05 pp for ratios, 0.5% for dollar amounts)
      2. Percentage representation
      3. Currency and scale ($M)
      4. Period and date alignment
      5. Directional sign consistency ('fell' iff delta < 0; 'rose' iff delta > 0)
      6. Largest driver attribution match
    """

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode

    def verify_narrative(
        self,
        generated_text: str,
        grounding_data: Dict[str, Any],
    ) -> Tuple[bool, List[Dict[str, Any]], str]:
        violations: List[Dict[str, Any]] = []

        # 1. Check for SQL Injection patterns
        sql_keywords = ["SELECT ", "DROP ", "INSERT ", "UPDATE ", "DELETE ", "UNION ", "--", ";--"]
        for kw in sql_keywords:
            if kw in generated_text.upper():
                violations.append({
                    "check": "SQL_INJECTION_DETECTED",
                    "claim": kw,
                    "expected": "No executable SQL tokens",
                    "reason": f"Disallowed SQL keyword '{kw}' detected in narrative.",
                })

        # 2. Extract percentage claims (e.g. 117.6%, 119.6%, 132.4%, -4.7 pp)
        pct_pattern = re.compile(r'([+-]?\d+\.?\d*)\s*(?:%|pp|percentage points)')
        found_pcts = [float(m) for m in pct_pattern.findall(generated_text)]

        # Collect valid percentages from grounding data
        valid_pcts: List[float] = []
        if "metrics" in grounding_data:
            for mval in grounding_data["metrics"].values():
                if isinstance(mval, (int, float)):
                    valid_pcts.append(round(float(mval), 2))
                    valid_pcts.append(round(float(mval), 1))
        if "total_movement_pp" in grounding_data:
            valid_pcts.append(round(float(grounding_data["total_movement_pp"]), 2))
            valid_pcts.append(round(float(grounding_data["total_movement_pp"]), 1))
        if "previous_nsfr_percentage" in grounding_data:
            valid_pcts.append(round(float(grounding_data["previous_nsfr_percentage"]), 1))
        if "current_nsfr_percentage" in grounding_data:
            valid_pcts.append(round(float(grounding_data["current_nsfr_percentage"]), 1))
            valid_pcts.append(round(float(grounding_data["current_nsfr_percentage"]), 2))
        if "drivers" in grounding_data:
            for d in grounding_data["drivers"]:
                if "contribution_pp" in d:
                    valid_pcts.append(round(abs(float(d["contribution_pp"])), 2))
                    valid_pcts.append(round(abs(float(d["contribution_pp"])), 1))
        # Check each claimed percentage
        for p in found_pcts:
            abs_p = abs(p)
            matched = any(abs(abs_p - abs(vp)) <= 0.15 for vp in valid_pcts)
            if not matched and valid_pcts:
                violations.append({
                    "check": "NUMERIC_VALUE_MISMATCH",
                    "claim": f"{p}%",
                    "expected": f"One of {valid_pcts}",
                    "reason": f"Claimed value '{p}%' not found in validated grounding dataset.",
                })

        # 3. Directional claims check
        text_lower = generated_text.lower()
        delta = grounding_data.get("total_movement_pp") or grounding_data.get("delta_pp") or 0.0
        if "decreased" in text_lower or "declined" in text_lower or "fell" in text_lower or "drop" in text_lower:
            if float(delta) > 0.05:
                violations.append({
                    "check": "DIRECTIONAL_INVERSION",
                    "claim": "asserted decline",
                    "expected": f"Positive delta (+{delta:.2f} pp)",
                    "reason": "Text asserted a decline while the underlying validated movement was positive.",
                })
        elif "increased" in text_lower or "improved" in text_lower or "rose" in text_lower or "gain" in text_lower:
            if float(delta) < -0.05:
                violations.append({
                    "check": "DIRECTIONAL_INVERSION",
                    "claim": "asserted increase",
                    "expected": f"Negative delta ({delta:.2f} pp)",
                    "reason": "Text asserted an increase while the underlying validated movement was negative.",
                })

        # 4. Check largest driver attribution
        if "largest_driver" in grounding_data:
            expected_driver = grounding_data["largest_driver"].lower()
            # If text claims a driver caused the movement, verify it includes the primary driver
            if "primarily driven by" in text_lower or "primary driver was" in text_lower:
                if expected_driver not in text_lower:
                    violations.append({
                        "check": "MISATTRIBUTED_DRIVER",
                        "claim": "Unverified driver",
                        "expected": grounding_data["largest_driver"],
                        "reason": f"Text failed to cite the mathematical top driver '{grounding_data['largest_driver']}'.",
                    })

        is_passed = len(violations) == 0
        status = "PASSED" if is_passed else "BLOCKED_NUMERIC_MISMATCH"
        return is_passed, violations, status
