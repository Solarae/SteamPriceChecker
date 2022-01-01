import requests
import json
import os 

KEY = '7be447da09c12bc36d535acf3741ae46360f34c2'
dir_path = os.path.dirname(os.path.realpath(__file__))
data_file = os.path.join(dir_path, 'data.json')

def populate_DB():
    response = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
    apps = response.json()['applist']['apps']

    params = {
        'key': KEY,
        'shops': 'steam'
    }
    response = requests.get('https://api.isthereanydeal.com/v01/game/plain/list/', params=params)
    plains = response.json()['data']['steam']

    # new_plains = dict((int(v[0].split('/')[-1]),k) for k,v in plains.items())
    # new_plains = dict((int(k.split('/')[-1]),v) for k,v in plains.items())

    data = []
    for app in apps:
        key = 'app/{}'.format(app['appid'])
        if key in plains:
            data.append({ 'appid': app['appid'], 'name': app['name'], 'plain': plains[key]})
    
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=4)

    print('Finished populating DB')

populate_DB()