
import requests

class FlightSearch:
    #This class is responsible for talking to the Flight Search API.
    def searching_endpoint_city(self, kiwi_headers, params):
        return requests.get(url = "https://api.tequila.kiwi.com/locations/query", headers = kiwi_headers, params = params)

    def searching_flight(self, params, headers):
        return requests.get(url = "https://api.tequila.kiwi.com/search", params = params, headers = headers)