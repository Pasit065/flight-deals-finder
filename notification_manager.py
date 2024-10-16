import random

class NotificationManager:
    #This class is responsible for sending notifications with the deal flight details.
    # Client should be this class attribute
    def __init__(self, client):
        self.client = client
        
    def sending_notification(self, body, send_from, send_to):
        message = self.client.messages.create(
            from_ = send_from,
            body = body,
            to = send_to
        )

    def display_notification_status(self, start_city, endpoint_city, is_send_notification):
        if is_send_notification:
            print(f"The sms has been send for {start_city} to {endpoint_city} trips.\n")
        elif not is_send_notification:
            print(f"There are no low price for {start_city} to {endpoint_city} trips.\nSo sms hasn't been send.\n")

    def get_notification_message(self, send_sms_flight):
        return f"""Low price alert! Only ${send_sms_flight['price']} 
to fly from {send_sms_flight['city_from']} to {send_sms_flight['city_to']}, 
From {send_sms_flight['trip_start_date']} to {send_sms_flight['trip_end_date']}."""

    def is_send_notification(self, the_amount_of_available_flights):
        if the_amount_of_available_flights > 0:
            return True
        else:
            return False
        
    def get_randomaly_notification_flight(self, available_flight_list):
        # get_random_notification_flight
        return random.choice(available_flight_list)


