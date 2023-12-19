from _ast import arguments
from argparse import ArgumentParser
from londontube.query.query import network_of_given_day, query_station_info
from datetime import datetime
import matplotlib.pyplot as plt

def process_station(string: str):
    if string.isdigit():
        return int(string)
    else:
        return string
        

def process():
    parser = ArgumentParser(description="journey planner")
    
    parser.add_argument('--plot', action="store_true")
    parser.add_argument('start', type=process_station)
    parser.add_argument('destination',type=process_station)
    parser.add_argument('setoff_date', nargs='?')
    
    arguments = parser.parse_args()

    current_date = None
    if arguments.setoff_date is None:
        # Get the current date
        current_date = datetime.now().date()
        current_date = current_date.strftime("%Y-%m-%d")

    start, destination = arguments.start, arguments.destination
    if type(arguments.start) == str:
        [start], _, _, _ = query_station_info([arguments.start])

    if type(arguments.destination) == str:
        [destination], _, _, _ = query_station_info([arguments.destination])

    network = network_of_given_day(current_date)
    path = network.dijkstra(start, destination)
    path_name = query_station_info(path)
    output = "Start: "
    for station in path_name[:len(path_name) - 1]:
        output += station + "\n"
    output += "End: " + path_name[len(path_name) - 1] + "\n"

    if arguments.plot:
        all_stations_index, all_stations_name, all_stations_lat, all_stations_long = query_station_info([])
        plt.scatter(all_stations_lat, all_stations_long)
        plt.title('Simple Scatter Plot')
        plt.xlabel('X Axis')
        plt.ylabel('Y Axis')

        file_string = "journey_from_" + arguments.start + "_to_" + arguments.destination + ".png"
        plt.savefig(file_string)






if __name__ == "__main__":
    process()