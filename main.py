# This file will need to use the DataManager,FlightSearch, FlightData, NotificationManager classes to achieve the program requirements.
from flight_search import FlightSearch
from flight_data import FlightData
from notification_manager import NotificationManager
from data_manager import DataManager
import datetime as dt
import smtplib
import requests
import os
from twilio.rest import Client
from csv_service import CsvService
import pandas
import json

def status_code_value_error_occur():
    ''' Raise for api error. '''
    raise ValueError("Api searching process are incomplete or get error.")

def dump_json_file(json_file_path, data):
    ''' Update json file data for flight. '''
    print(data)
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent = len(data))

# Get sms id and token from twilio to initialize 'client' object for managing sms sending.
ACCOUNT_SID = os.environ.get('account_sid')
auth_token = os.environ.get('auth_token')    

# Get twilio account generated phone number.
twilio_phone_number = os.environ.get("twilio_phone_number")

# Get recieved sms phone number.
my_phone_number = os.environ.get("my_phone_number")

# Determine connection object for send email when error occur.
my_email = os.environ.get('my_email')
smtp_pass = os.environ.get('smtp_pass')

# Determine every object.
flight_search = FlightSearch()
flight_data = FlightData()
notification_manager = NotificationManager(client = Client(ACCOUNT_SID, auth_token))
data_manager = DataManager()
csv_service = CsvService()

now = dt.datetime.now().replace(microsecond = 0)

# Determine connection object for send email when error occur.
connection = smtplib.SMTP("smtp.gmail.com", port = 587)
connection.starttls()
connection.login(my_email, smtp_pass)

STARTING_POINT_CITY = "Bangkok"

# Get json and csv file path.
json_file_path = "./json/current_available_flight.json"
csv_file_path = "./csv/sms_flight_record.csv"

# Read csv file and get current dataframe.
try:
    flight_data.sms_flights_dataframe = csv_service.get_csv_file_data(file_path = csv_file_path)
except FileNotFoundError:
    flight_data.set_sms_flights_dataframe_to_empty()
except pandas.errors.EmptyDataError:
    flight_data.set_sms_flights_dataframe_to_empty()
    csv_service.update_data_to_csv(data = flight_data.sms_flights_dataframe, file_path = csv_file_path)

# Get kiwi api key
kiwi_api_key = os.environ.get("kiwi_api_key")

# Determine parameter for api get.
kiwi_headers = {
    "apikey": kiwi_api_key
}

body = {
        "term": STARTING_POINT_CITY,
        "location_types": "city"
    }

# Get starting city data.
response = requests.get(url = "https://api.tequila.kiwi.com/locations/query", params = body, headers = kiwi_headers)

try:
    response.raise_for_status()
except:
    connection.sendmail(from_addr = my_email, to_addrs = my_email, msg = f"Subject:Api search are failed.\nplease check your code or calling to address {my_email}.")
    status_code_value_error_occur()

flight_data.set_starting_city_data(city_name = STARTING_POINT_CITY, iata_code = response.json()["locations"][0]["code"])
response = data_manager.get_google_sheet_data()

try:
    response.raise_for_status()
except:
    connection.sendmail(from_addr = my_email, to_addrs = my_email, msg = f"Subject:Api search are failed.\nplease check your code or calling to address {my_email}.")
    status_code_value_error_occur()

# Set endpoint_city_data from every data that get from google sheet.
flight_data.set_endpoint_city_data(data = response.json()["prices"])

# Gets and put iata code of endpoint city that determined in google sheet.
for row in flight_data.endpoint_city_data:
    if row["iataCode"] == "":
        # Determine parameter for api searching location data.
        params = {
            "term": row["city"],
            "location_types": "city"
        }
        
        # Searching city that you have defined.
        response = flight_search.searching_endpoint_city(kiwi_headers = kiwi_headers, params = params)

        try:
            response.raise_for_status()
        except:
            connection.sendmail(from_addr = my_email, to_addrs = my_email, msg = f"Subject:Api search are failed.\nplease check your code or calling to address {my_email}.")
            status_code_value_error_occur()

        # Determine row_num for define real row num in google sheet.
        # row_num is row no in google sheet.
        row_num = row["id"]
        endpoint_list_index = row_num - 2

        # Get iata code from data that you have import from api get and update data to endpoint city data dict.
        city_iata_code = data_manager.get_iata_code(city_data = response.json(), city_name = row["city"])
        flight_data.set_iata_to_endpoint_city_data(iata_code = city_iata_code, index = endpoint_list_index)

        # Set body parameter for api put.
        data_manager.set_editing_data_format(editing_col = "iataCode", new_data = city_iata_code)
        body = data_manager.get_put_body_params()

        # Api put.
        response = data_manager.put_data(row_num = row_num, body = body)

        try:
            response.raise_for_status()
        except:
            connection.sendmail(from_addr = my_email, to_addrs = my_email, msg = f"Subject:Api search are failed.\nplease check your code or calling to address {my_email}.")
            status_code_value_error_occur()

# Get date_from and date_to that define the range of departure time.
date_from = (now + dt.timedelta(days = 1)).date()
date_to = (date_from + pandas.DateOffset(months = 6)).date()

for endpoint_city in flight_data.endpoint_city_data:
    # Set body parameter.
    params = {
        "fly_from": flight_data.starting_city_data["iataCode"],
        "fly_to": endpoint_city["iataCode"],
        "date_from": dt.datetime.strftime(date_from, "%d/%m/%Y"),
        "date_to": dt.datetime.strftime(date_to, "%d/%m/%Y"),
        "return_from": dt.datetime.strftime(date_from, "%d/%m/%Y"),
        "return_to": dt.datetime.strftime(date_to, "%d/%m/%Y"),
        "curr": "USD",
        "max_stopovers": 0
    }

    # Searching for flight trips.
    response = flight_search.searching_flight(headers = kiwi_headers, params = params)

    try:
        response.raise_for_status()
    except:
        connection.sendmail(from_addr = my_email, to_addrs = my_email, msg = f"Subject:Api search are failed.\nplease check your code or calling to address {my_email}.")
        status_code_value_error_occur()

    # Set response.json() data to 'every_flight_for_each_city'.
    flight_data.set_every_flight_for_each_city(city_flights = response.json()["data"])

    # Filter every trips that the trip duration is around 7 days to 28 days. 
    available_total_days_trip_flights = flight_data.get_available_total_days_trip_flights(min_days_trip = 7, max_days_trip = 28)

    # Filter every trips that total price is lower than lowestprice that you have defined in google sheet.
    available_flights = flight_data.filter_the_lowerprice_trips(available_total_days_trip_flights = available_total_days_trip_flights, endpoint_city = endpoint_city)

    # Check is trips is available.
    is_send_notification = notification_manager.is_send_notification(the_amount_of_available_flights = len(available_flights))

    if is_send_notification:
        # Get only one flight from every available flight.
        send_sms_flight = notification_manager.get_randomaly_notification_flight(available_flight_list = available_flights)

        # Get notification message.
        send_sms_flight["sms_message"] = notification_manager.get_notification_message(send_sms_flight = send_sms_flight)

        # Send sms.
        notification_manager.sending_notification(body = send_sms_flight["sms_message"], send_from = twilio_phone_number, send_to = my_phone_number)

        # Set sms send time and date to record into csv and json file.
        send_sms_flight["time"] = str(now.time())
        send_sms_flight["date"] = str(dt.datetime.strftime(now.date(), "%Y-%m-%d"))
        
        # Update recorded send sms flight. 
        flight_data.update_sms_flights_dataframe(flight = send_sms_flight)

        # Update for new current available flight.
        flight_data.add_new_available_flight_to_all_current_flights(new_available_flight = send_sms_flight)

    # Display sms result for each endpoint city trip.
    notification_manager.display_notification_status(start_city = STARTING_POINT_CITY, endpoint_city = endpoint_city["city"], is_send_notification = is_send_notification)

# Update data to csv and json file.
csv_service.update_data_to_csv(data = flight_data.sms_flights_dataframe, file_path = csv_file_path)

# Update all available flight counting from todays (execute time is today) to json file. 
json_current_available_flights = {
    "finisihed_sms_sending_script_at": f"date: {str(now.date())} time: {str(now.time())}",
    "flights_data": flight_data.all_current_available_flights
}

# Get overall of available flights json data.
try:
    with open(json_file_path, "r") as file:
        overall_json_flights_data = json.load(file)

    if type(overall_json_flights_data) != list:
        overall_json_flights_data = []
except FileNotFoundError:
    overall_json_flights_data = []
except json.decoder.JSONDecodeError:
    overall_json_flights_data = []

overall_json_flights_data.append(json_current_available_flights)
dump_json_file(json_file_path = json_file_path, data = overall_json_flights_data)