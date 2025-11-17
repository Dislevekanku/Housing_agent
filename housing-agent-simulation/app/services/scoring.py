import pandas as pd

def score_candidates(df: pd.DataFrame) -> pd.DataFrame:
    # Simple normalized score: vacancy + transit bonuses
    # Assumes vacancy_signal (0..1), transit_score (0..1)
    w_vacancy = 0.6
    w_transit = 0.4

    df = df.copy()
    df["score"] = (
        w_vacancy * df.get("vacancy_signal", 0).fillna(0) +
        w_transit  * df.get("transit_score", 0).fillna(0)
    )
    df = df.sort_values("score", ascending=False)
    return df
