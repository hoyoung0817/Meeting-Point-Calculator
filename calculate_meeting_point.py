import os
import requests

class MeetingPointCalculator:
    def __init__(self, addresses):
        self.addresses = addresses
        self.locations = self.load_locations_from_addresses()

    def get_coordinates_from_address(self, address):
        KAKAO_API_KEY = os.environ.get('KAKAO_API_KEY')
        if KAKAO_API_KEY is None:
            raise ValueError("API Key not set")

        url = 'https://dapi.kakao.com/v2/local/search/address.json'
        headers = {'Authorization': f'KakaoAK {KAKAO_API_KEY}'}
        params = {'query': address}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error in get_coordinates_from_address(): {e}")

        data = response.json()

        if 'documents' not in data or len(data['documents']) == 0:
            raise ValueError(f"No data found for address {address}")

        document = data['documents'][0]
        return document['y'], document['x']

    def load_locations_from_addresses(self):
        locations = {}
        for i, address in enumerate(self.addresses):
            lat, lon = self.get_coordinates_from_address(address)
            if lat is not None and lon is not None:
                locations[f'friend{i + 1}'] = (float(lat), float(lon), 1)
        return locations

    def weighted_average(self, coordinates, weights):
        if len(coordinates) == 0 or len(weights) == 0 or len(coordinates) != len(weights):
            raise ValueError("Invalid input")

        weighted_sum = sum(coord * weight for coord, weight in zip(coordinates, weights))
        total_weight = sum(weights)
        return weighted_sum / total_weight

    def find_meeting_point(self):
        lats, lons, weights = zip(*[location_data for location_data in self.locations.values() if location_data[0] is not None and location_data[1] is not None])
        try:
            average_lat = self.weighted_average(lats, weights)
            average_lon = self.weighted_average(lons, weights)
        except ValueError as e:
            print(f"Error in find_meeting_point(): {e}")
            return None, None

        return average_lat, average_lon

def main():
    addresses = [
        '서울 북아현동 988', 
        '서울 영신로39길 16-1',
        '서울 난계로 169',
        '서울 대흥동 12-33',
        '서울 사당동 1034-27'
    ]
    calculator = MeetingPointCalculator(addresses)
    meeting_point = calculator.find_meeting_point()
    if meeting_point is None:
        print("Error: failed to calculate meeting point")
    else:
        print("Meeting point's latitude and longitude:", meeting_point)

if __name__ == "__main__":
    main()
