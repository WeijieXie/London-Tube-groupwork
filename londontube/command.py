from _ast import arguments
from argparse import ArgumentParser
from londontube.query.query import (
    network_of_given_day,
    convert_idices_to_names,
    convert_names_to_indices,
)
from datetime import datetime
import matplotlib.pyplot as plt


def convert_to_station_index(station):
    if station.isalpha():
        return convert_names_to_indices([station])[0]
    else:
        return int(station)


def build_parser():
    parser = ArgumentParser(description="Journey Planner for London tube")

    parser.add_argument(
        "--plot", action="store_true", help="Generate a plot of the journey"
    )
    parser.add_argument(
        "start", type=process_station, help="Start station's name or index"
    )
    parser.add_argument(
        "destination", type=process_station, help="Destination stations's name or index"
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
    path, travel_time = network.dijkstra(start_node, end_node)
    path_name = convert_idices_to_names(path)

    # TODO: Add desired path output format

    if arguments.plot:
        (
            all_stations_index,
            all_stations_name,
            all_stations_lat,
            all_stations_long,
        ) = query_station_info([])
        plt.scatter(all_stations_lat, all_stations_long)
        plt.title("Simple Scatter Plot")
        plt.xlabel("X Axis")
        plt.ylabel("Y Axis")

        file_string = (
            "journey_from_" + arguments.start + "_to_" + arguments.destination + ".png"
        )
        plt.savefig(file_string)
    


if __name__ == "__main__":
    main()
