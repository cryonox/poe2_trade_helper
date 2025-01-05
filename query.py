
import requests
import time
from rich import print
import json
from tqdm import tqdm
import pdb
from config import C
import utils


output = ''
class POETradeAPI:
    def __init__(self):
        self.base_url = "https://www.pathofexile.com/api/trade2"
        self.headers = {
            'Cookie': f'POESESSID={C.POESESSID}',
            "User-Agent": "POE-Trade-Search/1.0",
        }

    def search(self, league="Standard", online_only=True, min_div=1):
        search_payload = {
            "query": {
                "status": {"option": "online" if online_only else "any"},
                "name": "Against the Darkness",
                "filters": {
                    "type_filters": {
                        "filters": {
                            "category": "jewel",
                            "price": {"min": min_div, "option": "divine"}
                        }
                    }
                }
            },
            "sort": {"price": "asc"}
        }

        try:
            # Initial search request
            search_url = f"{self.base_url}/search/{league}"
            search_response = requests.post(
                search_url, headers=self.headers, json=search_payload)
            search_response.raise_for_status()

            search_data = search_response.json()
            if not search_data.get("result"):
                return []

            item_ids = search_data["result"]
            time.sleep(0.5)
            results = []
            for i in range(0, len(item_ids), 10):
                fetch_url = f"{self.base_url}/fetch/{','.join(item_ids[i:i+10])}"
                fetch_response = requests.get(fetch_url, headers=self.headers)
                fetch_response.raise_for_status()
                results.extend(fetch_response.json()["result"])
                # must be around number, based on rate limit header, 12:4:60,16:12:60
                # 12 requests in 4 seconds
                # 16 requests in 12 seconds
                # not follow and timeout for 60 second
                time.sleep(0.5)
            return results

        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return None

def check_match(r):
    global output
    try:

        if not r['item']['identified']:
            return
        if r['id'] in C.ignore_ids:
            return
        # do filter
        search_text = 'of damage as extra [cold] damage'
        #search_text = 'of damage as extra [lightning] damage'

        if search_text in r['item']['explicitMods'][0].lower() or search_text in r['item']['explicitMods'][1].lower():
            match = {
                'price': r['listing']['price']['amount'],
                'explicitMods': r['item']['explicitMods'],
                'whisper': r['listing']['whisper'],
                'id': r['id']
            }
            if match['price'] <= C.max_div:
                output += str(match['explicitMods']) + '\n'
                output += str(match['whisper']) + '\n'
                print(f'[green]{match["price"]} [/green]')
                print(match['explicitMods'])
                print(f'[red]{match["whisper"]} [/red]')
                if C.use_sound:
                    utils.play('assets/found2.mp3')
    except Exception as e:
        # maybe doesnt have explicit mods
        print(e)
        print(r)
        pass


def check_matches(results):
    for r in results:
        check_match(r)



def search():
    api = POETradeAPI()
    print("Searching...")
    results = []
    for i in tqdm(range(C.min_div, C.max_div+1)):
        search_results = api.search(min_div=i)
        check_matches(search_results)
        results.extend(search_results)

    with open('search_results.json', 'w', encoding='utf8') as f:
        json.dump(results, f, ensure_ascii=False)
    with open('output.txt', 'w',encoding='utf8') as f:
        f.write(output)

if __name__ == "__main__":
    search()
