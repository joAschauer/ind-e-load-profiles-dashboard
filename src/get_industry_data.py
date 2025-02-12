"""Disaggregation of a german profile to a single county."""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent.parent.resolve() / "data"


def transform_data_to_industry_types(
    cap_and_site_data: pd.DataFrame, shares: pd.DataFrame
) -> pd.DataFrame:
    transformed = cap_and_site_data.merge(
        shares, left_on="wz2008_abteilung_name", right_on="sector_wz2008"
    )
    transformed["n_sites_per_industry_type"] = (
        transformed["n_sites"] * transformed["share"]
    )
    transformed["n_cap_per_industry_type"] = transformed["n_cap"] * transformed["share"]
    transformed = (
        transformed.drop(
            [
                "wz2008_abteilung",
                "wz2008_abteilung_name",
                "sector_wz2008",
                "n_sites",
                "n_cap",
                "share",
            ],
            axis=1,
        )
        .groupby(["id", "name", "sector_agg", "sector_agg_id"])
        .sum()
        .reset_index()
        .rename(
            {
                "n_sites_per_industry_type": "n_sites",
                "n_cap_per_industry_type": "n_cap",
            },
            axis=1,
        )
    )

    return transformed


def get_industry_type_regional_distribution() -> pd.DataFrame:
    # load cap and site data from database:
    cap_and_site_data = pd.read_csv(
        DATA_DIR / "cap_and_site_data.csv", dtype={"id": str}
    )

    # load weights for transforming to industry types:
    shares = pd.read_csv(DATA_DIR / "industry_type_2_wz2008_shares.csv")

    # transform data from wz2008 categories to industry types:
    industry_types = transform_data_to_industry_types(cap_and_site_data, shares)
    return industry_types
