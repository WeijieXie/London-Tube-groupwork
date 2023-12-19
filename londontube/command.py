from _ast import arguments
from argparse import ArgumentParser
from londontube.query.query import network_of_given_day, query_station_to_index
from datetime import datetime

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
        [start], _ = query_station_to_index([arguments.start])

    if type(arguments.destination) == str:
        [destination], _ = query_station_to_index([arguments.destination])

    network = network_of_given_day(current_date)
    path = network.dijkstra(start, destination)
    path_name = query_station_to_index(path)
    output = "Start: "
    for station in path_name[:len(path_name) - 1]:
        output += station + "\n"
    output += "End: " + path_name[len(path_name) - 1] + "\n"
    print(output)




if __name__ == "__main__":
    process()