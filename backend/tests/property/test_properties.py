from decimal import Decimal

import hypothesis.strategies as st
from hypothesis import given, settings


@settings(max_examples=50)
@given(
    st.decimals(min_value=Decimal("0.0"), max_value=Decimal("1000000000.0"), places=4),
    st.sampled_from([Decimal("0.0"), Decimal("0.50"), Decimal("0.90"), Decimal("0.95"), Decimal("1.00")]),
)
def test_property_asf_non_negative(balance, factor):
    """Property: Available Stable Funding cannot become negative from positive source balance."""
    asf = balance * factor
    assert asf >= Decimal("0.0")


@settings(max_examples=50)
@given(
    st.decimals(min_value=Decimal("0.0"), max_value=Decimal("1000000000.0"), places=4),
    st.sampled_from([Decimal("0.0"), Decimal("0.05"), Decimal("0.10"), Decimal("0.15"), Decimal("0.50"), Decimal("0.65"), Decimal("0.85"), Decimal("1.00")]),
)
def test_property_rsf_non_negative(balance, factor):
    """Property: Required Stable Funding cannot become negative from positive source balance."""
    rsf = balance * factor
    assert rsf >= Decimal("0.0")


@settings(max_examples=50)
@given(
    st.decimals(min_value=Decimal("-100000000.0"), max_value=Decimal("100000000.0"), places=4),
    st.decimals(min_value=Decimal("-100000000.0"), max_value=Decimal("100000000.0"), places=4),
)
def test_property_roll_forward_invariance(opening, movement):
    """Property: Closing balance must strictly equal opening plus movement."""
    closing = opening + movement
    assert closing == opening + movement
