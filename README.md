# Flight-Deal-Finder
**Flight-Deal-Finder** is Python-based tool designed to notify users of affortable flight deals for every required city trip. This project help user to find the best deals for affotable price that significant saving your money for using with other purpose.

## Overview
This Python script leverage *Sheety API* with arrival cities data in Google Sheet and *flight search API* to evaluate direct flight trip compare to predefined thresholds in Google Sheet. Once affortable deal is found for desired cities, script will notify users via SMS and store data to `csv` and `json` directory. 

## API
In **Flight-Deal-Finder** project utilize 3 different API.

- *Sheety API* used for connect Google Sheet, allowing the script to edit, delete or insert data to specific Google Sheet. Visit *[Sheety API website](https://sheety.co/)* here. 

- *Kiwi Partners Flight Search API* used for searching flights trip deals for helping you to booking trips and provide IATA code for specific city. This is the *[Kiwi Flight Search API](https://tequila.kiwi.com/portal/login)*.

- *Twilio API* is used for sending SMS to authorized phone numbers. You can registers you new account to get `token` for sending SMS *[Twilio webpage](https://www.twilio.com/)*.

## Data Storage.
The project provide two files for store available flight data.

- `sms_flight_record.csv` is stored inside `csv` directory which is used to store details of each sms that has been send to user.

- `current_available_flight.json` is stored inside `json` directory which is used to store every available price flight deals.

## Diagram.
### Simplified Overview

![](./public/simplified_processes.png)

### Flowchart

![](./public/flight-deals-search-flowchart.png)

## Usage
Before executing project, a few setup are required.

### Initial Setup
1. **Google Sheet Data Setup**: Determine the `City` and `Lowest Price` values for arrival cities in Google Sheet. The data is connected to **Sheety API**.

    ![](./public/initial_google_sheet_setup.png)

    The above image is an example of determine initial values for google sheet.

2. **Install `requirements.txt`** for neccessary packages.

    ```Bash
    pip install -r requirements.txt
    ```

3. **Set up `STARTING_POINT_CITY`** in `main.py`
    ```Python
    STARTING_POINT_CITY = "Bangkok"
    ```

4. **Twilio Setup**: Sign up twilio to obtain `auth_token` and `ACCOUNT_SID`, determine values to `main.py`. as environment variable
    ```Python
    ACCOUNT_SID = os.environ.get('account_sid')
    auth_token = os.environ.get('auth_token') 
    ```

    Twilio provides phone numnber for registered users, determine that phone number and user number in `main.py` as environment variable
    ```Python
    # Get twilio account generated phone number.
    twilio_phone_number = os.environ.get("twilio_phone_number")

    # Get recieved sms phone number.
    my_phone_number = os.environ.get("my_phone_number")
    ```

6. **Kiwi Tequila token**: Sign in *Kiwi Partners Flight Search API* to obtain `api_key` and configure it into `kiwi_api_key` in `main.py`. By default `kiwi_api_key` determined as environment variable.
    ```Python
    # Get kiwi api key
    kiwi_api_key = os.environ.get("kiwi_api_key")
    ```

### Custom Setup
There are some variables that is flexible to adjust for user's purpose, the list is shown as following. 

1. `City` and `Lowest Price` column in Google Sheet can be changed or inserted by new row. 

    Please note that `IATA code` is not required, the project script can provide this column.

2. `STARTING_POINT_CITY` in `main.py` is flexible, user can change to desired city.
    ```Python
    STARTING_POINT_CITY = "Kyoto"
    ```

3. `my_phone_number` and `my_email` in environment variables can be adjusted but please bear in mind, `my_phone_number` value must be a phone number that verified by Twilio.

4. `date_from` and `date_to` values can be modifed for change to different intervals of searched trips
    ```Python
    date_from = (now + dt.timedelta(days = 1)).date()
    date_to = (date_from + pandas.DateOffset(months = 10)).date()
    ```

5.  In `min_days_trip` and `max_days_trip` can be adjusted, users can customize total min and max trip days as desired.
    ```Python
    available_total_days_trip_flights = flight_data.get_available_total_days_trip_flights(min_days_trip = 9, max_days_trip = 15)
    ```

6. In every `connection.sendmail()` function, `to_addrs` parameter can be adjuted which is recieved email when exception is occur.
    ```Python
    connection.sendmail(from_addr = my_email, to_addrs = "<recieved_email>", msg = f"Subject:Api search are failed.\nplease check your code or calling to address {my_email}.")
    ```
### Execute Project
Once the **Initial Setup** is provided , user can start execute package by
```Bash
python main.py
```