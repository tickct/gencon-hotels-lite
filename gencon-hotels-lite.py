from configparser import ConfigParser
import requests
import json
import html
from html.parser import HTMLParser
import time
import datetime
from prettytable import PrettyTable

try:
    configfilename = "./gencon-hotels-lite.cfg"
    config = ConfigParser()
except Exception as e:
    print("Unable to load config file - please verify it exists and is named 'gencon-hotels-lite.cfg'")
    print(e)
    exit(1)

try:
    config.read(configfilename)
except Exception as e:
    print("Unable to read config file")
    print(e)
    exit(1)

# Values from config file #
account_config = config["account-config"]
housing_token = account_config["housing-token"]
housing_authstring = account_config["housing-authstring"]
check_frequency = int(account_config["check-frequency"])

search_filters = config["search-filters"]
filter_checkin = search_filters["check-in"]
filter_checkout = search_filters["check-out"]
filter_search_skywalk = search_filters["search-skywalk"]
filter_search_blocks = search_filters["search-blocks"]
filter_search_blocks_max = search_filters["max-blocks"]
filter_search_miles = search_filters["search-miles"]
filter_search_miles_max = search_filters["max-miles"]
filter_search_hotel_name_enabled = search_filters["hotel-name-filter-enabled"]
filter_search_hotel_name_string = search_filters["hotel-name-filter-keyword"]
filter_search_room_keyword_enabled = search_filters["hotel-room-filter-enabled"]
filter_search_room_keyword_include = search_filters["hotel-room-filter-filter-include"]
filter_search_room_keyword_exclude = search_filters["hotel-room-filter-filter-exclude"]

alert_actions = config["alerts-config"]
alert_send_email = alert_actions["send-email"]
alert_send_sms = alert_actions["send-sms"]

# Process the search variables from the config file
try:
    if filter_search_skywalk == "true":
        filter_search_skywalk = True
    elif filter_search_skywalk == "false":
        filter_search_skywalk = False
    else:
        print("Error in Search Filter - search-skywalk - must be true or false")
        exit(1)
except Exception as e:
    print("Error in Search Filter - search-skywalk - must be true or false")
    print(e)
    exit(1)

try:
    if filter_search_blocks == "true":
        filter_search_blocks = True
    elif filter_search_blocks == "false":
        filter_search_blocks = False
    else:
        print("Error in Search Filter - search-blocks - must be 'true' or 'false'")
        exit(1)
except Exception as e:
    print("Error in Search Filter - search-blocks - must be 'true' or 'false'")
    print(e)
    exit(1)

if filter_search_blocks:
    try:
        filter_search_blocks_max = int(filter_search_blocks_max)
    except Exception as e:
        print("Error in Search Filter - max-blocks - must be a number")
        print(e)
        exit(1)

try:
    if filter_search_miles == "true":
        filter_search_miles = True
    elif filter_search_miles == "false":
        filter_search_miles = False
    else:
        print("Error in Search Filter - search-miles - must be 'true' or 'false'")
        exit(1)
except Exception as e:
    print("Error in Search Filter - search-miles - must be 'true' or 'false'")
    print(e)
    exit(1)

try:
    if filter_search_miles:
        try:
            filter_search_miles_max = int(filter_search_miles_max)
        except Exception as e:
            print("Error in Search Filter - max-miles - must be a number")
            print(e)
            exit(1)
except Exception as e:
    print("Error in Search Filter - max-miles - must be a number")
    print(e)
    exit(1)

# Process the alert variables from the config file
try:
    if alert_send_email == "true":
        alert_send_email = True
    elif alert_send_email == "false":
        alert_send_email = False
    else:
        print("Error reading the alert email setting - must be 'true' or 'false'")
        exit(1)
except Exception as e:
    print("Error reading the alert email setting - must be 'true' or 'false'")
    print(e)
    exit(1)

try:
    if alert_send_email:
        import smtplib
        from email.mime.text import MIMEText

        email_config = config["email-send-config"]
        email_fromuser = email_config["from-user"]
        email_password = email_config["from-password"]
        email_sendto = []
        if ',' not in (email_config["send-to"]):
            email_sendto.append(email_config["send-to"])
        elif ',' in (email_config["send-to"]):
            for email_address in email_config["send-to"].split(','):
                email_sendto.append(email_address)
        email_smtpserver = email_config["smtp-server"]
        email_smtpport = int(email_config["smtp-port"])
except Exception as e:
    print("Unable to parse email send-to list - please make sure addresses are comma separated")
    print(e)
    exit(1)

try:
    if alert_send_sms == "true":
        alert_send_sms = True
    elif alert_send_sms == "false":
        alert_send_sms = False
    else:
        print("Error reading the alert sms setting - must be 'true' or 'false'")
        exit(1)
except Exception as e:
    print("Error reading the alert sms setting - must be 'true' or 'false'")
    print(e)
    exit(1)

try:
    if alert_send_sms:
        from twilio.rest import Client

        sms_config = config["sms-send-config"]
        sms_twiliosid = sms_config["twilio-account-sid"]
        sms_twilioauth = sms_config["twilio-account-auth"]
        sms_sendfrom = sms_config["from-number"]
        sms_sendto = []
        if ',' not in sms_config['to-numbers']:
            sms_sendto.append(sms_config['to-numbers'])
        elif ',' in sms_config['to-numbers']:
            for phone_number in sms_config["to-numbers"].split(','):
                sms_sendto.append(phone_number)
except Exception as e:
    print("Unable to parse sms target phone numbers send-to list - please make sure numbers are comma separated")
    print(e)
    exit(1)

try:
    if filter_search_hotel_name_enabled == "true":
        filter_search_hotel_name_enabled = True
    elif filter_search_hotel_name_enabled == "false":
        filter_search_hotel_name_enabled = False
    else:
        print("Error reading the Hotel Name Search Filter Switch - must be 'true' or 'false'")
        exit(1)
except Exception as e:
    print("Error reading the Hotel Name Search Filter Switch - must be 'true' or 'false'")
    print(e)
    exit(1)

try:
    if filter_search_room_keyword_enabled == "true":
        filter_search_room_keyword_enabled = True
    elif filter_search_room_keyword_enabled == "false":
        filter_search_room_keyword_enabled = False
    else:
        print("Error reading the Hotel Room Keyword Filter Switch - must be 'true' or 'false'")
        exit(1)
except Exception as e:
    print("Error reading the Hotel Room Keyword Filter Switch - must be 'true' or 'false'")
    print(e)
    exit(1)

# Other Variables Needed #
base_portal_url = "https://book.passkey.com"
housing_url_initial = base_portal_url + "/reg/{0}/{1}".format(housing_token, housing_authstring)
housing_url_post_base = base_portal_url + "/event/49822766/owner/10909638"
housing_url_available_post = housing_url_post_base + "/list/hotels/available"

# Create a user agent string for requests in case they start blocking it again #
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.37 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
user_agent_header = {
    'User-Agent': user_agent
}

class PassKeyParser(HTMLParser):
    def __init__(self, response):
        HTMLParser.__init__(self)
        self.json = None
        self.feed(response.text)
        self.close()

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'script':
            attrs = dict(attrs)
            if attrs.get('id', '').lower() == 'last-search-results':
                self.json = True

    def handle_data(self, data):
        if self.json is True:
            self.json = data


class hotelroom(object):
    name = ''
    distance = ''
    price = ''
    taxrate = ''
    taxcost = ''
    subtotal = ''
    inventory = 0
    roomtype = ''
    hotelID = ''
    roomID = ''

    def __init__(self, name, distance, price, taxrate, taxcost, subtotal, inventory, roomtype, hotelID, roomID):
        self.name = name
        self.distance = distance
        self.price = price
        self.taxrate = taxrate
        self.taxcost = taxcost
        self.subtotal = subtotal
        self.inventory = inventory
        self.roomtype = roomtype
        self.hotelID = hotelID
        self.roomID = roomID


def make_hotel_room_object(name, distance, price, taxrate, taxcost, subtotal, inventory, roomtype, hotelID, roomID):
    hotel_room = hotelroom(name, distance, price, taxrate, taxcost, subtotal, inventory, roomtype, hotelID, roomID)
    return hotel_room


def get_hotel_room_objects():
    post_room_select_url = housing_url_post_base + "/rooms/select"
    response = requests.get(housing_url_initial, headers=user_agent_header)
    response_cookies = response.cookies
    # This filters based on whether the rooms are actually available
    post_data = construct_showavail_post()
    requests.post(housing_url_available_post, data=post_data, headers=user_agent_header, cookies=response_cookies)
    # This constructs the search based on date
    post_data = construct_search_post()
    response = requests.post(post_room_select_url, data=post_data, headers=user_agent_header, cookies=response_cookies)

    try:
        parser = PassKeyParser(response)
        hotels = json.loads(parser.json)
    except TypeError:
        current_time = str(datetime.datetime.now())
        print(current_time + " - Error Scraping Page - Continuing Script")
        print("This is an expected occasional error - do not worry")
        return []
    except Exception as e:
        current_time = str(datetime.datetime.now())
        print(current_time + " - Error Scraping Page - Continuing Script")
        print("This is not an expected error - report this for repair")
        print(e)
        return []

    available_room_list = []

    if hotels:
        for hotel in hotels:
            for block in hotel['blocks']:
                hotel_name = html.unescape(hotel['name'])
                if hotel['distanceUnit'] == 0:
                    hotel_distance = "Skywalk"
                elif hotel['distanceUnit'] == 1:
                    hotel_distance = "{} Block(s)".format(hotel['distanceFromEvent'])
                elif hotel['distanceUnit'] == 3:
                    hotel_distance = "{} Mile(s)".format(hotel['distanceFromEvent'])
                else:
                    hotel_distance = "unknown"
                hotel_room_price = sum(inv['rate'] for inv in block['inventory'])
                hotel_room_inventory = min(inv['available'] for inv in block['inventory'])
                hotel_room_type = html.unescape(block['name'])
                hotel_room_hotelID = (hotel['id'])
                hotel_room_roomID = (block['id'])

                try:
                    hotel_room_tax_policy = html.unescape(block['taxPolicy'])
                    hotel_room_tax_rate = float((hotel_room_tax_policy.split("%")[0])[-2:])
                except Exception as e:
                    hotel_room_tax_rate = 17
                    print(e)

                try:
                    hotel_total_tax_cost = (float(hotel_room_price) * float(hotel_room_tax_rate))/100
                except Exception as e:
                    hotel_total_tax_cost = 200
                    print(e)

                hotel_room_subtotal = str(format(float(float(hotel_room_price) + float(hotel_total_tax_cost)), '.2f'))
                hotel_room_price = str(format(hotel_room_price, '.2f'))
                hotel_room_tax_rate = str(format(hotel_room_tax_rate, '.2f'))
                hotel_total_tax_cost = str(format(hotel_total_tax_cost, '.2f'))

                hotel_room_object = make_hotel_room_object(hotel_name, hotel_distance, hotel_room_price, hotel_room_tax_rate, hotel_total_tax_cost, hotel_room_subtotal, hotel_room_inventory, hotel_room_type, hotel_room_hotelID, hotel_room_roomID)
                available_room_list.append(hotel_room_object)
    else:
        print("error parsing hotels through filters - aborting this run")
    return available_room_list


def construct_showavail_post():
    showavailable = True
    payload = {
        'showAvailable': showavailable
    }
    return payload


def construct_search_post():
    search_hotel_id = 0
    search_block_id = 0
    search_numberofguests = 1
    search_numberofrooms = 1
    search_numberofchildren = 0
    payload = {
        'hotelId': search_hotel_id,
        'blockMap.blocks[0].blockId': search_block_id,
        'blockMap.blocks[0].checkIn': filter_checkin,
        'blockMap.blocks[0].checkOut': filter_checkout,
        'blockMap.blocks[0].numberOfGuests': search_numberofguests,
        'blockMap.blocks[0].numberOfRooms': search_numberofrooms,
        'blockMap.blocks[0].numberOfChildren': search_numberofchildren
    }
    return payload


def filter_hotel_room_objects(hotel_room_object_list):
    if hotel_room_object_list:
        hotel_room_object_list = filter_hotel_room_objects_distance(hotel_room_object_list)
    else:
        return hotel_room_object_list
    if filter_search_hotel_name_enabled:
        if hotel_room_object_list:
            hotel_room_object_list = filter_hotel_room_objects_hotelname(hotel_room_object_list)
        else:
            return hotel_room_object_list
    if filter_search_room_keyword_enabled:
        if hotel_room_object_list:
            hotel_room_object_list = filter_hotel_room_objects_roomkeyword(hotel_room_object_list)
        else:
            return hotel_room_object_list
    # This is a sanity check to make sure rooms available exceeds 0
    # Sometimes setting the "only show available" fails, so this is here to avoid false positives
    hotel_room_object_list = filter_hotel_room_objects_availablecheck(hotel_room_object_list)
    return hotel_room_object_list


def filter_hotel_room_objects_distance(hotel_room_object_list):
    filtered_list = []
    for hotel_room in hotel_room_object_list:
        if filter_search_skywalk:
            if 'Skywalk' in hotel_room.distance:
                filtered_list.append(hotel_room)
        if filter_search_blocks:
            if 'Block' in hotel_room.distance:
                block_distance = hotel_room.distance.split(" ")[0]
                block_distance = float(block_distance)
                if block_distance < filter_search_blocks_max:
                    filtered_list.append(hotel_room)
        if filter_search_miles:
            if 'Mile' in hotel_room.distance:
                miles_distance = (hotel_room.distance).split(" ")[0]
                miles_distance = float(miles_distance)
                if miles_distance < filter_search_miles_max:
                    filtered_list.append(hotel_room)
    return filtered_list


def filter_hotel_room_objects_hotelname(hotel_room_object_list):
    filtered_list = []
    for hotel_room in hotel_room_object_list:
        if filter_search_hotel_name_string in hotel_room.name:
            filtered_list.append(hotel_room)
    return filtered_list


def filter_hotel_room_objects_roomkeyword(hotel_room_object_list):
    filtered_list = []
    for hotel_room in hotel_room_object_list:
        if filter_search_room_keyword_include in hotel_room.roomtype:
            if filter_search_room_keyword_exclude not in hotel_room.roomtype:
                filtered_list.append(hotel_room)
    return filtered_list


def filter_hotel_room_objects_availablecheck(hotel_room_object_list):
    filtered_list = []
    for hotel_room in hotel_room_object_list:
        if hotel_room.inventory > 0:
            filtered_list.append(hotel_room)
    return filtered_list


def send_alerts(hotel_room_object_list):
    for hotel_room in hotel_room_object_list:
        if alert_send_email:
            send_email_alert(hotel_room)
        if alert_send_sms:
            send_sms_alert(hotel_room)


def send_email_alert(hotel_room):
    for sendto_target in email_sendto:
        message = """\
        New Hotel Found\n\n
        Hotel - {0}\n
        Distance - {1}\n
        Total Stay Price - {2}\n
        Inventory Available - {3}\n
        Type of Room - {4}""".format(hotel_room.name, hotel_room.distance, hotel_room.price, hotel_room.inventory, hotel_room.roomtype)

        msg = MIMEText(message, 'plain')
        msg['Subject'] = "Gencon Hotel Alert"
        msg['From'] = email_fromuser
        msg['To'] = sendto_target

        try:
            server = smtplib.SMTP_SSL(email_smtpserver, email_smtpport)
            server.ehlo()
            server.login(email_fromuser, email_password)
            server.sendmail(email_fromuser, sendto_target, msg.as_string())
            server.quit()
        except Exception as e:
            print("Can't send email to {0}".format(sendto_target))
            print(e)


def send_sms_alert(hotel_room):
    message = "Hotel Alert\n{0}\n{1}\nPrice - {2}\n Avail - {3}\n Type - {4}".format(hotel_room.name, hotel_room.distance, hotel_room.price, hotel_room.inventory, hotel_room.roomtype)
    client = Client(sms_twiliosid, sms_twilioauth)
    for phone_number in sms_sendto:
        try:
            client.messages.create(
                from_=sms_sendfrom,
                body=message,
                to=phone_number
            )
        except Exception as e:
            print("Could not send SMS to {0}".format(phone_number))
            print(e)


def table_creation(hotel_list):
    table_output = PrettyTable()
    table_output.field_names = ["Hotel Name", "Distance", "DistanceUnit", "Room Type", "Price", "Total Price", "Inventory"]
    for hotel_room in hotel_list:
        if "Skywalk" not in hotel_room.distance:
            distance = table_get_distance(hotel_room.distance)
            distance_unit = table_get_distanceunit(hotel_room.distance)
        elif "Skywalk" in hotel_room.distance:
            distance = "Skywalk"
            distance_unit = "*"
        table_output.add_row([hotel_room.name, distance, distance_unit, hotel_room.roomtype, hotel_room.price, hotel_room.subtotal, hotel_room.inventory])
    table_output.sortby = "Distance"
    table_output.reversesort = False
    title_string = str("Gencon Hotel Rooms Status - Updated " + str(datetime.datetime.now()))
    table_output.title = title_string
    return table_output


def table_get_distance(combined_input):
    try:
        distance_measure = combined_input.split(" ")
        distance_measure = distance_measure[0]
    except Exception as e:
        print("Error converting Distance for Table")
        print(e)
        distance_measure = " "
    return distance_measure


def table_get_distanceunit(combined_input):
    try:
        distance_unit = combined_input.split(" ")
        distance_unit = distance_unit[1]
    except Exception as e:
        print("Error converting Distance Unit for Table")
        print(e)
        distance_unit = " "
    return distance_unit


def search_workflow():
    hotel_room_objects = get_hotel_room_objects()
    alerts_triggered = 0
    hotel_room_objects_filtered = filter_hotel_room_objects(hotel_room_objects)
    if hotel_room_objects_filtered:
        print("\n" * 30)
        output_table = table_creation(hotel_room_objects)
        print(output_table)
        if alert_send_email or alert_send_sms:
            send_alerts(hotel_room_objects_filtered)
            print("\n" * 3)
            print("Alerts Sent Out")
            alerts_triggered = 1
    if alerts_triggered == 1:
        time.sleep(60)


print("Gencon-Hotels-Lite is running")
while True:
    try:
        search_workflow()
        time.sleep(check_frequency)
    except Exception as e:
        print(e)
