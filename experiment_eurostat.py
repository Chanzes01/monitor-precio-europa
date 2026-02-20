import eurostat
import pandas as pd

def search_data():
    # 1. Search for datasets
    print("Searching for datasets...")
    toc_df = eurostat.get_toc_df()
    wine_datasets = toc_df[toc_df['title'].str.contains('wine', case=False, na=False)]
    print("\nPotential Datasets:")
    print(wine_datasets[['code', 'title']].head(10))
    
    # Common dataset for CN8 trade is 'DS-058213' or 'DS-057380' or similar. 
    # Often 'DS-045409' (easy Comext) or 'DS-059322'.
    # Actually the standard monthly dataset code often changes or is 'DS-059322' (Easy Comext).
    # Let's try to look for 'DS-045409' which is "EU Trade Since 2015 by CN8".
    
    # 2. Targeted search for Trade Data
    print("\nChecking for Trade Datasets (DS-045409)...")
    dataset_code = 'DS-045409' # Often used for CN8 detailed trade
    
    # Verify if it exists in TOC
    if dataset_code in toc_df['code'].values:
        print(f"Dataset {dataset_code} found.")
        
    # 3. Get Parameters (Dimensions)
        # pars = eurostat.get_pars(dataset_code)
        # print(f"Dimensions: {pars}")
        
        # 4. Fetch Data Sample
        # Flow 2 = Exports
        # Reporter ES = Spain
        # Partner EU27_2020 = Intra-EU
        # Product 220429?? = Bulk Wine (checking validity)
        # freq M = Monthly
        
        print("Fetching data for ES exports of 220429...")
        params = {
            'freq': 'M',
            'reporter': 'ES',
            'partner': 'EU27_2020',
            'product': '220429', # CN6 prefix might work? otherwise try specific CN8
            'flow': '2',
            'indicators': 'VALUE_IN_EUR' # and QUANTITY_IN_KG?
        }
        
        # Note: Eurostat API filtering often requires specific codes. 
        # For CN8, '220429' might not be a valid leaf code.
        # Let's try to get data without product filter first, but filtered by other dims to find product codes?
        # No, that's too big.
        
        # Let's try a valid CN8 code for bulk wine.
        # 2204 29 93 ? White wine > 10L?
        # Let's try querying a broader set or just try 220429 to see if it aggregates.
        
        # Partner EU27_2020 failed. Trying specific partners (FR, IT) and World (WORLD).
        # Removed startPeriod (query param issue). Fetching full history for specific intersection.
        
        filter_pars = {
            'freq': ['M'],
            'reporter': ['ES'],
            'partner': ['FR', 'IT'], 
            'flow': ['2'],
            'product': ['22042993', '22042994', '22042293', '22042294'] # Sample CN8 codes (White/Red > 10L vs 2-10L)
        }
        
        try:
            # Fix: filter_pars should be passed as keyword argument or correct position.
            # Signature: get_data_df(code, flags=False, cflags=False, verbose=False, filter_pars=None, ...)
            df = eurostat.get_data_df(dataset_code, filter_pars=filter_pars)
            print(f"Data fetched: {len(df)} rows")
            print(df.head())
        except Exception as e:
            print(f"Error fetching: {e}")
            
            # If 220429 fails, maybe it expects full CN8.
            print("Retrying with specific CN8 codes (e.g., 22042911)...")
            # 2204 29 is the sub-heading.
            # We might need to look up codes.

    else:
        print(f"Dataset {dataset_code} not found in TOC. Searching for 'traditional' trade datasets...")
        trade_datasets = toc_df[toc_df['title'].str.contains('CN8', case=False, na=False)]
        print(trade_datasets[['code', 'title']].head(5))

if __name__ == "__main__":
    search_data()
