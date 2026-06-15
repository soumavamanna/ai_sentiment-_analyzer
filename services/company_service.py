import pandas as pd
from functools import lru_cache


class CompanyService:

    def __init__(
        self,
        metadata_path="data/company_metadata.csv"
    ):

        self.df = pd.read_csv(
            metadata_path
        )

        self.company_map = {}

        self.alias_map = {}

        self._build_indexes()

    def _build_indexes(self):

        for _, row in self.df.iterrows():

            ticker = row["ticker"]

            company_data = {
                "ticker": ticker,
                "company_name":
                    row["company_name"],

                "sector":
                    row["sector"],

                "industry":
                    row["industry"],

                "market_cap":
                    row["market_cap"],

                "index_memberships":
                    str(
                        row[
                            "index_memberships"
                        ]
                    ).split("|"),

                "aliases":
                    str(
                        row["aliases"]
                    ).split("|")
            }

            self.company_map[
                ticker
            ] = company_data

            for alias in (
                company_data["aliases"]
            ):

                self.alias_map[
                    alias.lower()
                ] = ticker

            self.alias_map[
                company_data[
                    "company_name"
                ].lower()
            ] = ticker

    def get_company(
        self,
        ticker
    ):

        return self.company_map.get(
            ticker
        )

    def get_company_name(
        self,
        ticker
    ):

        company = (
            self.get_company(
                ticker
            )
        )

        if company:
            return company[
                "company_name"
            ]

        return None

    def get_sector(
        self,
        ticker
    ):

        company = (
            self.get_company(
                ticker
            )
        )

        if company:
            return company[
                "sector"
            ]

        return None

    def get_industry(
        self,
        ticker
    ):

        company = (
            self.get_company(
                ticker
            )
        )

        if company:
            return company[
                "industry"
            ]

        return None

    def get_market_cap(
        self,
        ticker
    ):

        company = (
            self.get_company(
                ticker
            )
        )

        if company:
            return company[
                "market_cap"
            ]

        return None

    def get_indices(
        self,
        ticker
    ):

        company = (
            self.get_company(
                ticker
            )
        )

        if company:
            return company[
                "index_memberships"
            ]

        return []

    def get_aliases(
        self,
        ticker
    ):

        company = (
            self.get_company(
                ticker
            )
        )

        if company:
            return company[
                "aliases"
            ]

        return []

    def get_all_tickers(
        self
    ):

        return list(
            self.company_map.keys()
        )

    def get_sector_tickers(
        self,
        sector_name
    ):

        sector_name = (
            sector_name.lower()
        )

        tickers = []

        for ticker, data in (
            self.company_map.items()
        ):

            if (
                data["sector"]
                .lower()
                == sector_name
            ):

                tickers.append(
                    ticker
                )

        return tickers

    def get_index_tickers(
        self,
        index_name
    ):

        index_name = (
            index_name.upper()
        )

        tickers = []

        for ticker, data in (
            self.company_map.items()
        ):

            if (
                index_name
                in
                data[
                    "index_memberships"
                ]
            ):

                tickers.append(
                    ticker
                )

        return tickers

    def alias_to_ticker(
        self,
        text
    ):

        text = text.lower()

        found = set()

        for alias, ticker in (
            self.alias_map.items()
        ):

            if alias in text:

                found.add(
                    ticker
                )

        return list(found)

    def is_valid_ticker(
        self,
        ticker
    ):

        return (
            ticker
            in
            self.company_map
        )


@lru_cache(maxsize=1)
def get_company_service():

    return CompanyService()