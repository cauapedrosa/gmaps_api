from logging import exception
import traceback
import requests
from urllib.parse import urlencode


def find_geocode(address):
    endpoint = f"https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "key": api_key,
        "address": address
    }
    url_params = urlencode(params)
    url = f"{endpoint}?{url_params}"
    r = requests.get(url)
    if r.status_code not in range(200, 299):
        print(f"⚠️ Error! Status Code: {r.status_code}:\n{r.json()}")
        return {}
    latlng = {}
    try:
        latlng = r.json()['results'][0]['geometry']['location']
    except:
        print(f'⚠️Exception: {r.json()}')
        traceback.print_exc()
    finally:
        print(f'📍 Input address ({address}) found geocode {latlng}')
        return latlng.get("lat"), latlng.get("lng")


def find_place(input, lat='-23.533773', lng='-46.625290'):
    locationbias = f"point:{lat},{lng}"
    endpoint = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "key": api_key,
        "input": input,
        "inputtype": "textquery",
        # "fields": "formatted_address,name,geometry,permanently_closed",
        "fields": "name,place_id",
        "locationbias": locationbias
    }
    url_params = urlencode(params)
    url = f"{endpoint}?{url_params}"
    # print(f'DEBUG: findplace calling url: {url}\n')
    r = requests.get(url)
    if r.status_code not in range(200, 299):
        print(f"⚠️ Error! Status Code: {r.status_code}:\n{r.json()}")
        return {}
    try:
        place_id = r.json()['candidates'][0]['place_id']
        place_name = r.json()['candidates'][0]['name']
    except:
        print(f'⚠️ Exception:\n{r.json()}')
        traceback.print_exc()
        pass
    finally:
        print(f'🗺️ find_place() found: {place_name}')
        return place_id


def find_distance(orig, dest):
    endpoint = f"https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": orig,
        "destinations": dest,
        "key": api_key
    }
    url_params = urlencode(params)
    url = f"{endpoint}?{url_params}"
    r = requests.get(url)
    if r.status_code not in range(200, 299):
        print(f"⚠️ Error! Status Code: {r.status_code}:\n{r.json()}")
        return {}
    try:
        # print(r.json())
        distance = r.json()['rows'][0]['elements'][0]['distance']['value']
    except:
        print(f'⚠️ Exception: {r.json()}')
        traceback.print_exc()
        distance = -1
        pass
    finally:
        print(
            f'🏃find_distance() found: {distance} meters')
    return distance


def main(api_key, address):
    api_key = api_key

    user_addr = address
    print(f'\nInitiating main() for address:({address})')
    user_lat, user_lng = find_geocode(user_addr)
    # print(f'DEBUG| find_geocode() returned: {user_lat}, {user_lng}')
    unit_place_id = find_place("UBS", user_lat, user_lng)
    # unit_place_id = find_place("UBS", user_addr)
    # print(f'DEBUG| find_place() returned: {unit_place_id}')
    user_origin = f'{user_lat},{user_lng}'
    # user_origin = f'{user_addr}'
    distance = find_distance(f'place_id:{unit_place_id}', user_origin)
    # print(f'DEBUG| find_distance() returned: {distance}m')
    return


if __name__ == "__main__":
    # Import API Key from "api-key.txt"
    api_file = open("api-key.txt", "r")
    api_key = api_file.read()
    api_file.close()
    if api_key == None:
        print("⚠️ API Key required!")
    else:
        print("\nAPI Key loaded!\nNow calling main()...\n")
        addresses = [
            'Av Paulista, 900',
            'Av Brigadeiro Faria Lima 500',
            'Av José Pinheiro Borges 6500',
            'R Virgílio Gonçalves Leite 400',
            'R Aristídes Belini 400'
        ]
    for address in addresses:
        main(api_key, address)
