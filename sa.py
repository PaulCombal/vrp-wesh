#!/bin/env python

import psutil, os, random, time, numpy as np, math, copy, sys, argparse, matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("-d", help="dataset file", default=False)
parser.add_argument("-n", help="noninteractive", default=False)
parser.add_argument("-k", help="trucks", default=1)
parser.add_argument("-r", help="trucks", default=20)
args = parser.parse_args()
memory = psutil.Process(os.getpid()).memory_info
time_start = None
report_file = open("report.csv", "w")

# Déclaration de fonctions
def generate_cities(howmany = int(args.r), max_coordinates = 100):
    return [random.sample(range(max_coordinates), 2) for _ in range(howmany)]

def generate_random_tour(cities):
    city_count = len(cities)
    return random.sample(range(city_count), city_count)

def generate_good_random_tour(cities, howmany=10000):
    best_tour = generate_random_tour(cities)
    lowest = distance(best_tour, cities)
    for _ in range(howmany):
        tour = generate_random_tour(cities)
        dist = distance(tour, cities)
        if dist < lowest:
            lowest = dist
            best_tour = copy.copy(tour)

    print("Lowest tour has distance {}".format(lowest))
    return best_tour

def import_dataset(filename):
    with open(filename) as fp:  
        line = fp.readline()
        arr = []
        while line:
            xy = line.strip().split(" ")
            xy = [int(e) for e in xy]
            #print(xy)
            arr.append(xy)
            line = fp.readline()

        return arr
    
def dataset_name():
    return args.d

def distance_between(tour, cities, i, j):
    city_count = len(cities)
    return sum([math.sqrt(sum([(cities[tour[(k+1) % city_count]][d] - cities[tour[k % city_count]][d])**2 for d in [0,1] ])) for k in [j,j-1,i,i-1]])

def distance_to_next(tour, cities, index):
    city_count = len(cities)
    return sum([math.sqrt(sum([(cities[tour[(k+1) % city_count]][d] - cities[tour[k % city_count]][d])**2 for d in [0,1] ])) for k in [index]])

def distance(tour, cities):
    city_count = len(cities)
    return sum([math.sqrt(sum([(cities[tour[(k+1) % city_count]][d] - cities[tour[k % city_count]][d])**2 for d in [0,1] ])) for k in range(city_count)])

def temperature_noninteractive():
    return np.logspace(0,5,num=100000)[::-1]

def temperature_interactive():
    alpha = 0.999
    temp = 10 ** 2
    while True:
        temp = alpha * temp
        if temp < 0.1:
            temp = 10 ** 1
        yield temp

def explain_tour(tour, cities):
    lgth = len(tour)
    for step in range(lgth):
        curr = tour[step % lgth]
        next = tour[(step + 1) % lgth]
        distance = distance_between(tour, cities, step, step + 1)

        print("{} -> {}  \t(distance: {:10.4f})\t From {}, To: {}".format(curr, next, distance, cities[curr], cities[next]))

def live_plot(tour, cities):
    city_count = len(cities)
    cities_x = [cities[tour[i % city_count]][0] for i in range(city_count + 1)]
    cities_y = [cities[tour[i % city_count]][1] for i in range(city_count + 1)]

    plt.clf()
    plt.plot(cities_x, cities_y, 'xb-')
    plt.pause(0.1)

def report(what):
    report_file.write(what + "\n")

def array_part_loop(arr, start, end):
    arr_len = len(arr)
    ret = []

    if start > end:
        nb_elements = arr_len - start
        nb_elements += end
    else:
        return arr[start:(end + 1) % arr_len]
    
    for i in range(nb_elements):
        ret.append(arr[(start + i) % arr_len])

    ret.append(arr[(start + nb_elements) % arr_len])
    return ret


def SA(cities, temperatures):
    iteration = 0
    tour = generate_good_random_tour(cities)
    city_count = len(cities)
    lowest_tour = None
    lowest_distance = np.inf
    report("iterations,temps,distance,temperature,memory")
    try:
        for temperature in temperatures():
            iteration = iteration + 1

            [i,j] = sorted(random.sample(range(city_count),2))
            newTour = tour[:i] + tour[j:j+1] + tour[i+1:j] + tour[i:i+1] + tour[j+1:]

            oldDistances = distance_between(tour, cities, i, j)
            newDistances = distance_between(newTour, cities, i, j)
            newTotalDist = distance(newTour, cities)

            if math.exp( (oldDistances - newDistances) / temperature) > random.random():
                tour = copy.copy(newTour)
            
            if newTotalDist < lowest_distance:
                lowest_distance = newTotalDist
                lowest_tour = copy.copy(tour)

            if(iteration % 5000 == 0):
                seconds_elapsed = time.time() - time_start
                print("Iteration: " + str(iteration))
                print("Elapsed: {:10.4f}s".format(seconds_elapsed))
                print("New distance: {:10.4f}".format(newTotalDist))
                print("Best distance: {:10.4f}".format(lowest_distance))
                print("Temperature: " + str(temperature))
                print("Memory used: " + str(memory().rss))
                print("======")
                report("{},{},{},{},{}".format(iteration, seconds_elapsed, lowest_distance, temperature, memory().rss))
                live_plot(lowest_tour, cities)
    
    except KeyboardInterrupt:
        print("Interrupted")


    if lowest_tour == None:
        return tour
    else:
        return lowest_tour


# Initialisation des données

plt.ion()
plt.show()
external_dataset = dataset_name()
time_start = time.time()
if external_dataset:
    cities = import_dataset(external_dataset)
else:
    cities = generate_cities()

city_count = len(cities)

# Application de la métaheuristique
if args.n:
    # Non interactif: On est dans une range de solutions relativement petite
    print("Run non interactif, fin dans 30s")
    tour = SA(cities, temperature_noninteractive)
else:
    # Interactif: tourne à l'infini jusqu'à l'arrêt
    print("Run interactif, Ctrl+c quand fini")
    tour = SA(cities, temperature_interactive)

report_file.close()

# Affichage de détails
explain_tour(tour, cities)

# Division en k camions
k = int(args.k)
tour_distance = distance(tour, cities)
position_first_city = tour.index(0)
position_relative_next_stop_city = 0
initial_tour = copy.copy(tour)

for truck in range(k-1):
    distance_cumulee = 0
    while distance_cumulee < (tour_distance / k):
        curr = initial_tour[(position_first_city + position_relative_next_stop_city) % city_count]
        distance = distance_to_next(initial_tour, cities, position_first_city + position_relative_next_stop_city)
        distance_cumulee += distance
        position_relative_next_stop_city += 1

    tour.insert((position_first_city + position_relative_next_stop_city) % city_count, 0)

if int(args.k) <= 1:
    live_plot(tour, cities)
else:
    # On insère le dernier tour
    zero_positions = [i for i, e in enumerate(tour) if e == 0]
    number_zeros = len(zero_positions)
    plt.clf()

    for zero_pos_i in range(len(zero_positions)):
        tour_start_index = zero_positions[zero_pos_i]
        tour_end_index = zero_positions[(zero_pos_i + 1) % number_zeros]
        truck_tour = array_part_loop(tour, tour_start_index, tour_end_index)
        truck_tour_len = len(truck_tour)

        cities_x = [cities[truck_tour[i % truck_tour_len]][0] for i in range(truck_tour_len + 1)]
        cities_y = [cities[truck_tour[i % truck_tour_len]][1] for i in range(truck_tour_len + 1)]
        plt.plot(cities_x, cities_y, '-')

    plt.pause(0.1)

    while True:
        time.sleep(1)