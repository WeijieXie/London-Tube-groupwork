from argparse import ArgumentParser
from londontube.query.query import network_of_given_day

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
    parser.add_argument('setoff-date', nargs='?')
    
    arguments = parser.parse_args()
    
    print(arguments)

if __name__ == "__main__":
    process()