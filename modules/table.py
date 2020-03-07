from prettytable import PrettyTable
import datetime


def table_creation(hotel_list):
    table_output = PrettyTable()
    table_output.field_names = ["Hotel Name", "Distance", "DistanceUnit", "Room Type", "Price", "Inventory"]
    for hotel_room in hotel_list:
        if "Skywalk" not in hotel_room.distance:
            distance = table_get_distance(hotel_room.distance)
            distance_unit = table_get_distanceunit(hotel_room.distance)
        elif "Skywalk" in hotel_room.distance:
            distance = "Skywalk"
            distance_unit = "*"
        table_output.add_row([hotel_room.name, distance, distance_unit, hotel_room.roomtype, hotel_room.price, hotel_room.inventory])
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