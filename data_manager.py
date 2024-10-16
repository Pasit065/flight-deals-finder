
import requests
import os

class DataManager:
    #This class is responsible for talking to the Google Sheet.
    def __init__(self):
        self.edited_data_dict = {}
        self.put_requests_url = os.environ.get("flight_sheety_put_url")
        self.get_requests_url = os.environ.get("flight_sheety_get_url")

    def get_google_sheet_data(self):
        return requests.get(url = self.get_requests_url)

    def set_editing_data_format(self, editing_col, new_data):
        self.edited_data_dict[editing_col] = new_data

    def get_iata_code(self, city_data, city_name):
        for city_component in city_data["locations"]:
            if city_component["name"] == city_name:
                return city_component["code"]
        
    def get_put_body_params(self):
        body = {
            "price": {}
        }

        for editing_col in self.edited_data_dict:
            body["price"][editing_col] = self.edited_data_dict[editing_col]

        return body

    def put_data(self, row_num, body):
        put_row_url = self.put_requests_url + row_num
        return requests.put(url = put_row_url, json = body)
