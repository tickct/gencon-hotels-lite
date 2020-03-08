import modules
import html


class HotelRoom(object):
    name = ''
    distance = ''
    price = ''
    inventory = 0
    roomtype = ''
    hotelID = ''
    roomID = ''

    def __init__(self, name, distance, price, inventory, roomtype, hotel_id, room_id):
        self.name = name
        self.distance = distance
        self.price = price
        self.inventory = inventory
        self.roomtype = roomtype
        self.hotelID = hotel_id
        self.roomID = room_id


def make_hotel_room_object(name, distance, price, inventory, roomtype, hotel_id, room_id):
    hotel_room = HotelRoom(name, distance, price, inventory, roomtype, hotel_id, room_id)
    return hotel_room


def hotel_room_parser(hotel_json, config):
    available_room_list = []
    for hotel in hotel_json:
        for block in hotel['blocks']:
            room_avail_event = True
            room_inventory = 99999
            nightly_rate = block['averageRate']
            for room in block['inventory']:
                if room_avail_event is False:
                    break
                room_date = (str(room['date']).replace("[", "")).replace("]", "")
                if room_date in modules.all_dates_list(config.check_in, config.check_out):
                    if room['available'] == 0 or room['available'] == room['wlAvailable']:
                        room_avail_event = False
                        room_inventory = 0
                        break
                    elif room['available'] < room_inventory:
                        room_inventory = int(room['available'])
            if room_avail_event:
                if hotel['distanceUnit'] == 0:
                    hotel_distance = "Skywalk"
                elif hotel['distanceUnit'] == 1:
                    hotel_distance = "{} Block(s)".format(hotel['distanceFromEvent'])
                elif hotel['distanceUnit'] == 3:
                    hotel_distance = "{} Mile(s)".format(hotel['distanceFromEvent'])
                else:
                    hotel_distance = "unknown"
                hotel_name = html.unescape(hotel['name'])
                hotel_room_inventory = room_inventory
                hotel_room_type = html.unescape(block['name'])
                hotel_room_hotel_id = (hotel['id'])
                hotel_room_room_id = (block['id'])
                hotel_room_price = str(format(nightly_rate, '.2f'))
                hotel_room_object = make_hotel_room_object(hotel_name, hotel_distance, hotel_room_price,
                                                           hotel_room_inventory, hotel_room_type, hotel_room_hotel_id,
                                                           hotel_room_room_id)
                available_room_list.append(hotel_room_object)
    return available_room_list
