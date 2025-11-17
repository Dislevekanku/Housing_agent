import pandas as pd
from typing import List, Optional
from app.settings import settings

class ZoningIndex:
    def __init__(self, path: str | None = None):
        self.path = path or settings.PARCELS_PATH
        self.df = pd.read_csv(self.path)
        # Normalize column names: zone -> zoning_district
        if "zone" in self.df.columns and "zoning_district" not in self.df.columns:
            self.df["zoning_district"] = self.df["zone"]
        # Expected columns: parcel_id,address,zoning_district (or zone),lot_sqft,allowable_uses,vacancy_signal,transit_score
        # allowable_uses is a pipe-delimited string like "residential|mixed-use"

    def find_candidates(
        self,
        allowable_use: str,
        min_lot_sqft: Optional[float],
        max_results: int
    ) -> pd.DataFrame:
        df = self.df.copy()
        df = df[df["allowable_uses"].str.contains(allowable_use, case=False, na=False)]
        if min_lot_sqft:
            df = df[df["lot_sqft"] >= float(min_lot_sqft)]
        return df.head(max_results)
