import pandas as pd
from typing import Dict, Optional

def score_candidates(
    df: pd.DataFrame,
    weights: Dict[str, float],
    lot_norm_baseline: Optional[float] = None
) -> pd.DataFrame:
    """
    Score candidates using configurable weights.

    Args:
        df: Candidate dataframe
        weights: Dict with keys "vacancy", "transit", "lot_sqft"
        lot_norm_baseline: Optional baseline lot size used for normalization
    """
    df = df.copy()

    vacancy = df.get(
        "vacancy_signal", pd.Series([0] * len(df), index=df.index)
    ).fillna(0)
    transit = df.get(
        "transit_score", pd.Series([0] * len(df), index=df.index)
    ).fillna(0)

    if lot_norm_baseline is None:
        lot_norm_baseline = 1.0
        if "lot_sqft" in df.columns and not df["lot_sqft"].empty:
            lot_norm_baseline = max(df["lot_sqft"].max(), 1.0)
    if "lot_sqft" in df.columns:
        lot_sqft_series = df["lot_sqft"].fillna(0)
    else:
        lot_sqft_series = pd.Series([0] * len(df), index=df.index)
    lot_sqft = (lot_sqft_series / lot_norm_baseline).clip(upper=1.0)

    score_series = (
        weights.get("vacancy", 0.0) * vacancy +
        weights.get("transit", 0.0) * transit +
        weights.get("lot_sqft", 0.0) * lot_sqft
    )

    df["score"] = score_series
    df = df.sort_values("score", ascending=False)
    return df
