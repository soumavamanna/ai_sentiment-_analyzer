import os
import pandas as pd
from flashtext import KeywordProcessor


class TickerResolver:

    def __init__(
        self,
        metadata_filename: str = "nse_company_metadata.csv"
    ):

        self.keyword_processor = KeywordProcessor(
            case_sensitive=False
        )

        current_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        metadata_path = os.path.join(
            current_dir,
            "data",
            metadata_filename
        )

        if not os.path.exists(metadata_path):
            raise FileNotFoundError(
                f"Could not find metadata file at: {metadata_path}"
            )

        df = pd.read_csv(metadata_path)

        self.alias_map = {}

        for _, row in df.iterrows():

            aliases_str = (
                str(row["aliases"])
                if pd.notna(row["aliases"])
                else str(row["company_name"])
            )

            aliases = [
                a.strip().lower()
                for a in aliases_str.split("|")
                if a.strip()
            ]

            aliases.append(
                str(row["company_name"]).strip().lower()
            )

            company_data = {
                "company_name": row["company_name"],
                "ticker": row["ticker"],
                "sector": row["sector"],
                "industry": row["industry"],
                "market_cap": row["market_cap"]
            }

            for alias in set(aliases):

                self.alias_map[alias] = company_data

                self.keyword_processor.add_keyword(
                    alias,
                    company_data
                )

    def extract_ticker_info(self, text):

        results = self.keyword_processor.extract_keywords(
            text
        )

        seen = set()
        output = []

        for company in results:

            ticker = company["ticker"]

            if ticker not in seen:

                output.append(company)
                seen.add(ticker)

        return output