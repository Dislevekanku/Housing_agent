import hashlib
from typing import Optional, Tuple

import pandas as pd

from app.settings import settings


class ZoningIndex:
    def __init__(self, path: str | None = None):
        self.path = path or settings.PARCELS_PATH
        self.df: pd.DataFrame | None = None
        self.dataset_hash: Optional[str] = None
        self._load()

    def _load(self) -> None:
        self.df = pd.read_csv(self.path)
        # Normalize column names: zone -> zoning_district
        if "zone" in self.df.columns and "zoning_district" not in self.df.columns:
            self.df["zoning_district"] = self.df["zone"]
        # Ensure allowable uses list
        self.df["allowable_uses"] = self.df["allowable_uses"].fillna("")
        self.df["allowable_uses_list"] = self.df["allowable_uses"].apply(
            lambda v: [s.strip() for s in str(v).split("|") if s]
        )
        self.dataset_hash = self._compute_dataset_hash()

    def _compute_dataset_hash(self) -> str:
        try:
            with open(self.path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except OSError:
            return "unknown"

    def refresh(self) -> None:
        """Reload the parcel dataset from disk"""
        self._load()

    def find_candidates(
        self,
        allowable_use: str,
        min_lot_sqft: Optional[float],
        min_vacancy: Optional[float],
        min_transit: Optional[float],
        max_results: int
    ) -> Tuple[pd.DataFrame, int]:
        if self.df is None:
            raise ValueError("Zoning index is not initialized")

        df = self.df.copy()
        allowable_use_lower = allowable_use.lower()
        df = df[df["allowable_uses_list"].apply(
            lambda uses: any(allowable_use_lower == u.lower() for u in uses)
        )]
        if min_lot_sqft is not None:
            df = df[df["lot_sqft"] >= float(min_lot_sqft)]
        if min_vacancy is not None:
            df = df[df.get("vacancy_signal", 0).fillna(0) >= float(min_vacancy)]
        if min_transit is not None:
            df = df[df.get("transit_score", 0).fillna(0) >= float(min_transit)]

        total_available = len(df)
        df = df.head(max_results)
        return df, total_available
