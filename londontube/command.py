from argparse import ArgumentParser
from londontube.query.query import (
    network_of_given_day,
    convert_indices_to_names,
    convert_names_to_indices,
    query_station_all_info
)
from datetime import datetime
import matplotlib.pyplot as plt


def convert_to_station_index(station):
    if station.isnumeric():
        return int(station)
    else:
        return convert_names_to_indices([station])[0]



def build_parser():
    parser = ArgumentParser(description="Journey Planner for London tube")

    parser.add_argument(
        "--plot", action="store_true", help="Generate a plot of the journey"
    )
    parser.add_argument(
        "start", help="Start station's name or index"
    )
    parser.add_argument(
        "destination", help="Destination stations's name or index"
    )
    parser.add_argument(
        "setoff_date",
        nargs="?",
        # Get the current date
        default=datetime.now().date().strftime("%Y-%m-%d"),
        help="The date of the journey (YYYY-MM-DD). Defalut value is today",
    )

    return parser


def main():
    # Create a parser
    parser = build_parser()
    arguments = parser.parse_args()

    start, destination = arguments.start, arguments.destination

    start_node = convert_to_station_index(start)
    end_node = convert_to_station_index(destination)

    network = network_of_given_day(arguments.setoff_date)
    path, travel_time = Network.dijkstra(network, start_node, end_node)
    path_name = convert_indices_to_names(path)

    # TODO: Add desired path output format
    output = f"Journey will take {travel_time} minutes.\nStart: "
    for name in path_name[:len(path_name)-1]:
        output += f"{name}\n"
    output += f"End: {path_name[len(path_name)-1]}\n"
    print(output)

    if arguments.plot:
        dict_indices_names, dict_names_indices, dict_position = query_station_all_info()
        all_stations_lat = [value['latitude'] for name, value in dict_position.items()]
        all_stations_long = [value['longitude'] for name, value in dict_position.items()]
        plt.figure()

        plt.scatter(all_stations_long,all_stations_lat,color='black',s=1)
        plt.title(f"journey from {arguments.start} to {arguments.destination}")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")

        path_lat = [dict_position[name]['latitude'] for name in path]
        path_long = [dict_position[name]['longitude'] for name in path]

        plt.plot(path_long,path_lat)

        file_string = (
            "journey_from_" + arguments.start + "_to_" + arguments.destination + ".png"
        )
        plt.savefig(file_string)
    


if __name__ == "__main__":
    main()
