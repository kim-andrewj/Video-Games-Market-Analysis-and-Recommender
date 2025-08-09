import requests
import pandas as pd
import time
import os
import os
import requests
from dotenv import load_dotenv

load_dotenv()
# API key from .env file
CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
CLIENT_SECRET = os.getenv("IGDB_CLIENT_SECRET")

auth_url = "https://id.twitch.tv/oauth2/token"
auth_params = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "client_credentials",
}

auth_response = requests.post(auth_url, data=auth_params)
# Helpful debugging if it fails
try:
    auth_response.raise_for_status()
except requests.HTTPError:
    print("Auth status:", auth_response.status_code)
    print("Auth body:", auth_response.text)
    raise

data = auth_response.json()

if "access_token" not in data:
    # Twitch returns JSON like: {"status":401,"message":"invalid client"}
    raise RuntimeError(f"Auth failed; response was: {data}")

access_token = data["access_token"]
print("Access token acquired.")

headers = {
    "Client-ID": CLIENT_ID,
    "Authorization": f"Bearer {access_token}",
}

# initial array for all game titles
all_games = []

# parameters
batch_size = 500
total_records = 30000
num_batches = total_records//batch_size

# helper function: extracting dev/pub companies
def extract_devs_and_pubs(involved_companies):
    developers = []
    publishers = []
    for entry in involved_companies or []:
        if entry.get('developer') and entry.get('company'):
            developers.append(entry['company']['name'])
        if entry.get('publisher') and entry.get('company'):
            publishers.append(entry['company']['name'])
    return developers, publishers

# loading in data in batches due to API only accepting 500 at a time
for i in range(num_batches):
    offset = i * batch_size
    print(f"Fetching offset {offset}")

    query = f"""
    fields 
        name, 
        genres.name, 
        involved_companies.developer, 
        involved_companies.publisher, 
        involved_companies.company.name, 
        total_rating, 
        total_rating_count, 
        platforms.name, 
        release_dates.y, 
        game_modes.name, 
        themes.name; 
    where total_rating_count != null;
    sort total_rating_count desc;
    limit {batch_size};
    offset {offset};
    """

    response = requests.post(
        'https://api.igdb.com/v4/games',
        headers=headers,
        data=query
    )

    if response.status_code != 200:
        print("Error:", response.status_code)
        break

    games_data = response.json()

    # loading data into initial all_games array
    for game in games_data:
        devs, pubs = extract_devs_and_pubs(game.get('involved_companies'))
        all_games.append({
            'Name': game.get('name'),
            'Genres': [g['name'] for g in game.get('genres', [])],
            'Developers': devs,
            'Publishers': pubs,
            'Rating': game.get('total_rating'),
            'Rating Count': game.get('total_rating_count'),
            'Platforms': [p['name'] for p in game.get('platforms', [])],
            'Release Years': [r['y'] for r in game.get('release_dates', []) if r.get('y')],
            'Game Modes': [m['name'] for m in game.get('game_modes', [])],
            'Themes': [t['name'] for t in game.get('themes', [])],
        })
    time.sleep(0.3)

df = pd.DataFrame(all_games)

games_data = response.json()

print(df.head())
print(df.count)
df.to_csv('raw_data.csv', index=False)