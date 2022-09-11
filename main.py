import csv
import traceback
import requests
from urllib.parse import urlencode

csv_columns = ['ano', 'entrada', 'num_vo', 'nome', 'sexo', 'data de nasc', 'idade', 'nome da mãe', 'endereço', 'lat', 'long', 'dist', 'municipio ', 'area resid', 'CEP', 'ocupação ', 'escolaridade', 'Data do óbito', 'H do óbito', 'unidade de atendimento', 'tipo de caso', 'tratamento anterior', 'Forma clínica 1', 'Forma clínica 2', 'Forma clínica 3', 'classificação', 'tipo de descoberta', 'baciloscopia escarro', 'baciloscopia outro material',
               'cultura escarro', 'cultura outro mataterial', 'RXtoráx', 'Anti-HIV', 'necrópsia ', 'outros exames', 'tratamento', 'tratamento inicial', 'tratamento atual', 'comunicantes total', 'comunicantes examinados', 'comunicantes adoeceram', 'total de internações', 'data de encerramento do caso', 'conclusão do caso', 'tuberculose pulmonar', 'tuberculose ganglionar', 'tuberculose cerebral', 'tuberculose miliar disseminada', 'outros órgãos']
search_term_list = ["UBS", "AMA", "CTA", "UPA", "SAE", "CRST", "URSI", "PS Municipal"]

# Import API Key from "api-key.txt"
api_file = open("api-key.txt", "r")
api_key = api_file.read()
api_file.close()
print(f'\n👍 Loaded Api Key! {api_key[:5]}...')


def find_geocode(address):
    latlng = {}
    lat, lng = '', ''
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
    try:
        latlng = r.json()['results'][0]['geometry']['location']
        lat = latlng.get("lat")
        lng = latlng.get("lng")
    except:
        print(f'⚠️ Exception: {r.json()}')
        traceback.print_exc()
    finally:
        print(f'📍 Input address ({address}) found geocode {latlng}')
    return lat, lng


def find_place(input, lat='-23.533773', lng='-46.625290'):
    locationbias = f"point:{lat},{lng}"
    endpoint = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "key": api_key,
        "input": input,
        "inputtype": "textquery",
        "fields": "name,place_id",
        "locationbias": locationbias
    }
    url_params = urlencode(params)
    url = f"{endpoint}?{url_params}"
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
        return None
    finally:
        print(f'🗺️ find_place() found: {place_name}')
        return place_id


def find_distance_from_points(orig, dest):
    distance = -1
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
    finally:
        print(f'find_distance: [Origin: {orig}]-[Destination:{dest}]')
        print(f'🏃find_distance() found: {distance} meters.')
    return distance


def get_distance(user_addr, search_term):
    print(f'\nInitiating Operation for address:({user_addr})')
    user_lat, user_lng = find_geocode(user_addr)
    unit_place_id = find_place(search_term, user_lat, user_lng)
    distance = find_distance_from_points(
        f'place_id:{unit_place_id}',
        f'{user_lat},{user_lng}'
    )
    return distance


def save_to_csv(data):
    with open('out.csv', mode='w', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerows(data)
        return


def read_from_csv(file):
    patient_list = []
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for line in reader:
            patient_list.append(line)
    return patient_list


def main(api_key):
    api_key = api_key

    data = read_from_csv('tb.csv')
    for n, user in enumerate(data):
        user_dist_shortest = 99999
        user_dist = -1
        user_addr = user['endereço']
        if (user_addr.upper() != 'IGNORADO') & (user_addr.upper() != 'MORADOR DE RUA') & (user_addr.upper() != 'SEM INFORMAÇÃO'):
            for i, search_term in enumerate(search_term_list):
                print(f'#{i+1}/{len(search_term_list)} Searching for {search_term} near {user_addr}')
                user_dist = get_distance(user_addr, search_term)
                print(f'DEBUG: Found distance ({user_dist}). Comparing to shortest ({user_dist_shortest})')
                if user_dist <= user_dist_shortest:
                    print(f'DEBUG: Found shorter distance. user: {user_dist} | shortest: {user_dist_shortest}')
                    user_dist_shortest = user_dist
        else:
            print(f"Address [{user_addr}] is invalid, skipping...")
        print(f'✅{n+1}/{len(data)}: Shorter distance found was {user_dist_shortest}. Saving to dict...')
        data[n]['dist'] = (user_dist)

    save_to_csv(data)


if __name__ == "__main__":

    if api_key == None:
        print("⚠️ API Key required!")
    else:
        print("\nAPI Key loaded!\nNow calling main()...\n")
        main(api_key)
