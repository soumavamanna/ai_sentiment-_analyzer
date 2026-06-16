import csv
import os

# Dynamically locate the CSV file based on this script's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
METADATA_FILE = os.path.join(BASE_DIR, 'data', 'nse_company_metadata.csv')

def load_metadata():
    """Reads the CSV and returns a list of dictionaries."""
    metadata = []
    try:
        with open(METADATA_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                metadata.append(row)
    except FileNotFoundError:
        print(f"⚠️ Warning: Metadata file not found at {METADATA_FILE}")
    
    return metadata

def get_universe():
    """Returns the list of tickers for the data collectors."""
    metadata = load_metadata()
    # Extract just the ticker column
    return [row['ticker'].strip() for row in metadata if row.get('ticker')]

def get_ticker_aliases():
    """
    Builds a dynamic dictionary mapping base tickers to their aliases.
    Example output: {'RELIANCE': ['RELIANCE', 'RELIANCE INDUSTRIES', 'RIL'], ...}
    """
    metadata = load_metadata()
    aliases_dict = {}

    for row in metadata:
        ticker = row.get('ticker', '')
        if not ticker:
            continue
            
        # Get the base ticker (e.g., RELIANCE.NS -> RELIANCE)
        base_ticker = ticker.replace(".NS", "").strip().upper()

        # Parse the pipe-separated aliases
        raw_aliases = row.get('aliases', '').split('|')

        # Clean them up and uppercase them for matching
        clean_aliases = [alias.strip().upper() for alias in raw_aliases if alias.strip()]

        # Safety net: Add the official company name just in case it wasn't in the aliases list
        company_name = row.get('company_name', '').strip().upper()
        if company_name:
            clean_aliases.append(company_name)

        # Remove any duplicates using set() and assign to the dictionary
        aliases_dict[base_ticker] = list(set(clean_aliases))

    return aliases_dict