from time import sleep
from main import find_geocode
import csv

csv_columns = ['nome', 'endereco', 'lat', 'lng']


def read_from_csv(file):
    data = []
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for line in reader:
            data.append(line)
    return data


def save_to_csv(data):
    with open('places_latlng.csv', mode='w', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerows(data)
        return


def main():
    data = read_from_csv('places.csv')
    for n, d in enumerate(data):
        addr = d['endereco']
        print(f'\n#{n}/{len(data)}: {d}')
        print(f"\nCalling find_geocode({addr})")
        try:
            place_lat, place_lng = find_geocode(addr)
        except:
            place_lat = None
            place_lng = None
            continue
        print(f'✅ Found Place: [{place_lat} | {place_lng}]')
        d['lat'] = place_lat
        d['lng'] = place_lng
        # print(f'Final data: {d}')
        if n > 10:
            save_to_csv(data)
    return


if __name__ == '__main__':
    main()
