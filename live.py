import websocket
import json
import threading
import requests
import time
from config import C
from rich import print
import utils


def check_match(r):
    try:

        if not r['item']['identified']:
            return
        if r['id'] in C.ignore_ids:
            return
        # do filter
        search_text = '[cold] damage'

        if search_text in r['item']['explicitMods'][0].lower() or search_text in r['item']['explicitMods'][1].lower():
            match = {
                'price': r['listing']['price']['amount'],
                'explicitMods': r['item']['explicitMods'],
                'whisper': r['listing']['whisper'],
                'id': r['id']
            }
            if match['price'] <= C.max_div:
                print(match['explicitMods'])
                print(f'[red]{match["whisper"]} [/red]')
                utils.play('assets/found2.mp3')
    except Exception as e:
        # maybe doesnt have explicit mods
        print(e)
        print(r)
        pass



class POETradeClient:
    def __init__(self):
        self.poesessid = C.POESESSID
        self.ws = None
        self.base_url = "https://www.pathofexile.com/api/trade2"
        self.headers = {
            'Cookie': f'POESESSID={self.poesessid}',
            "User-Agent": "POE-Trade-Search/1.0",
        }

    def create_search(self, league, search_criteria):
        """Create a search and get search ID"""
        search_url = f"{self.base_url}/search/{league}"
        response = requests.post(
            search_url, json=search_criteria, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            return data.get('id')
        else:
            raise Exception(f"Failed to create search: {response.status_code}")

    def on_message(self, ws, message):
        data = json.loads(message)
        if 'new' in data:
            items = data['new']
            # Fetch item details
            ids = ','.join(items)
            fetch_url = f"{self.base_url}/fetch/{ids}"
            response = requests.get(fetch_url, headers=self.headers)
            if response.status_code == 200:
                for r in response.json()['result']:
                    check_match(r)
                # print(f"New items found: {json.dumps(item_details, indent=2)}")

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")

    def on_open(self, ws):
        print("WebSocket connection established")

    def connect_live_search(self, search_id):
        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            f"wss://www.pathofexile.com/api/trade2/live/poe2/Standard/{search_id}",
            header=self.headers,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )

        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

    def disconnect(self):
        if self.ws:
            self.ws.close()


# Usage example
if __name__ == "__main__":
    search_criteria = {
        "query": {
            "status": {"option": "online"},
            "name": "Against the Darkness",
            "filters": {
                    "type_filters": {
                        "filters": {
                            "category": "jewel",
                            # "price": {"min": min_div, "option": "divine"}
                        }
                    }
            }
        },
        "sort": {"price": "asc"}
    }

    client = POETradeClient()

    # Create search and get search ID
    # Replace league name as needed
    search_id = client.create_search("Standard", search_criteria)
    print(f"Search ID: {search_id}")

    # Connect to live search
    client.connect_live_search(search_id)

    # Keep main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.disconnect()
