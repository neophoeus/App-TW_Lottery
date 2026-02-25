import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

GAMES = {
    'big': {
        'url': 'http://www.lotto-8.com/listltobig.asp',
        'csv': os.path.join(DATA_DIR, 'big.csv'),
        'columns': ['date', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'special'],
        'cols_count': 8 
    },
    'power': {
        'url': 'http://www.lotto-8.com/listlto.asp',
        'csv': os.path.join(DATA_DIR, 'power.csv'),
        'columns': ['date', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'special'],
        'cols_count': 8
    },
    '539': {
        'url': 'http://www.lotto-8.com/listlto539.asp',
        'csv': os.path.join(DATA_DIR, '539.csv'),
        'columns': ['date', 'n1', 'n2', 'n3', 'n4', 'n5'],
        'cols_count': 6
    }
}

class LottoFetcher:
    def fetch_all(self):
        results = {}
        for game in ['power', 'big', '539']:
            success, msg = self.fetch_game(game)
            results[game] = msg
        return results

    def fetch_game(self, game_code, max_pages=5):
        # Default max_pages=5 for quick updates. Set higher for full init.
        if game_code not in GAMES:
            return False, "Invalid game code"
            
        conf = GAMES[game_code]
        all_data = []
        page = 1
        consecutive_empty = 0
        
        # Load existing date to stop early
        existing_latest_date = None
        if os.path.exists(conf['csv']):
            try:
                df_exist = pd.read_csv(conf['csv'])
                if not df_exist.empty:
                    existing_latest_date = df_exist['date'].max()
            except:
                pass

        print(f"Fetching {game_code}...")
        
        while page <= max_pages:
            url = f"{conf['url']}?indexpage={page}&orderby=new"
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code != 200: break
                resp.encoding = 'utf-8' # Force utf-8
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                tables = soup.find_all('table')
                found_new = False
                
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td', recursive=False)
                        if not cols: continue
                        
                        texts = [c.get_text(strip=True) for c in cols]
                        date_val = None
                        nums = []
                        required_nums = conf['cols_count'] - 1
                        
                        # Parsing logic from original script
                        if len(texts) >= 2:
                            match = re.search(r'(\d{4})/?(\d{2})/(\d{2})', texts[0])
                            if match:
                                date_val = f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
                                for c in cols[1:]:
                                    t = c.get_text(separator=' ', strip=True).replace(u'\xa0', ' ').replace(',', ' ')
                                    for p in t.split():
                                        if p.isdigit() and len(p)<=2: nums.append(p.zfill(2))
                        elif len(cols) == 1:
                            text = cols[0].get_text(separator=' ', strip=True).replace(u'\xa0', ' ').replace(',', ' ')
                            match = re.search(r'(\d{4})/?(\d{2})/(\d{2})', text)
                            if match:
                                date_val = f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
                                matched_str = match.group(0) # Store the original match string for splitting logic
                                parts = text.split()
                                found_d = False
                                for p in parts:
                                    if p == matched_str or p == getattr(match, 'string', ''): found_d = True
                                    elif found_d and p.isdigit() and len(p)<=2: nums.append(p.zfill(2))
                        
                        # Normalize date format to YYYY-MM-DD
                        if date_val:
                            date_val = date_val.replace('/', '-')
                            
                        # Stop if date exists
                        if date_val and existing_latest_date and date_val <= existing_latest_date:
                            # We found a date that is already in DB. Since we fetch 'new', we can stop?
                            # But sometimes order on page isn't perfect? URL says orderby=new.
                            # Let's just skip this row, if whole page is old, stop.
                            continue

                        if date_val and len(nums) >= required_nums:
                            nums = nums[:required_nums]
                            all_data.append([date_val] + nums)
                            found_new = True

                if not found_new:
                    consecutive_empty += 1
                    if consecutive_empty >= 2: break
                else:
                    consecutive_empty = 0
                    
                page += 1
                time.sleep(0.3)
                
            except Exception as e:
                return False, str(e)

        # Merge new data with old
        if all_data:
            new_df = pd.DataFrame(all_data, columns=conf['columns'])
            if os.path.exists(conf['csv']):
                old_df = pd.read_csv(conf['csv'])
                combined = pd.concat([old_df, new_df])
            else:
                combined = new_df
                
            # Clean up
            combined['date'] = pd.to_datetime(combined['date'])
            combined = combined.dropna(subset=['date'])
            combined = combined.drop_duplicates(subset=['date'])
            combined = combined.sort_values(by='date')  # Oldest -> Newest
            # Convert date back to string to avoid timestamp in CSV
            combined['date'] = combined['date'].dt.strftime('%Y-%m-%d')
            
            combined.to_csv(conf['csv'], index=False)
            return True, f"Updated {len(new_df)} new rows."
        else:
            return True, "No new data found."
