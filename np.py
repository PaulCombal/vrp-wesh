#!/bin/env python

import random, numpy, math, copy, sys, argparse, matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("-d", help="dataset file", default=False)
parser.add_argument("-n", help="noninteractive", default=False)
args = parser.parse_args()

# Déclaration de fonctions
def generate_cities(howmany = 15, max_coordinates = 100):
    return [random.sample(range(max_coordinates), 2) for _ in range(howmany)]


def generate_random_tour(cities):
    city_count = len(cities)
    return random.sample(range(city_count), city_count)

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

def distance(tour, cities):
    city_count = len(cities)
    return sum([math.sqrt(sum([(cities[tour[(k+1) % city_count]][d] - cities[tour[k % city_count]][d])**2 for d in [0,1] ])) for k in range(city_count)])


def temperature_noninteractive():
    return numpy.logspace(0,5,num=100000)[::-1]

def temperature_interactive():
    alpha = 0.99
    temp = 10 ** 5
    while True:
        temp = alpha * temp
        yield temp
        


def SA(cities, temperatures):
    iteration = 0
    tour = generate_random_tour(cities)
    city_count = len(cities)
    lowest_tour = None
    lowest_distance = 10000
    try:
        for temperature in temperatures():
            iteration = iteration + 1
            [i,j] = sorted(random.sample(range(city_count),2))
            newTour = tour[:i] + tour[j:j+1] +  tour[i+1:j] + tour[i:i+1] + tour[j+1:]

            oldDistances = distance_between(tour, cities, i, j)
            newDistances = distance_between(newTour, cities, i, j)
            oldTotalDist = distance(tour, cities)
            newTotalDist = distance(newTour, cities)

            if math.exp( (oldDistances - newDistances) / temperature) > random.random():
                tour = copy.copy(newTour)
            
            if newTotalDist < lowest_distance:
                lowest_distance = newTotalDist
                lowest_tour = copy.copy(tour)

            if(iteration % 5000 == 0):
                print("Iteration: " + str(iteration))
                print("New distance: " + str(newTotalDist))
                print("Old distance: " + str(oldTotalDist))
                print("Best distance: " + str(lowest_distance))
                print("======")
    
    except KeyboardInterrupt:
        print("Interrupted")


    if lowest_tour == None:
        print("retiurn tour")
        return tour
    else:
        print("return lwoeshy")
        return lowest_tour


# Initialisation des données
external_dataset = dataset_name()
if external_dataset:
    cities = import_dataset(external_dataset)
else:
    cities = generate_cities()

city_count = len(cities)

print(distance([0, 1, 2, 3], [[1, 1], [2, 1], [2, 2], [1, 2]]))
sys.exit()

# Application de la métaheuristique
if args.n:
    # Non interactif: On est dans une range de solutions relativement petite
    print("Run non interactif, fin dans 30s")
    tour = SA(cities, temperature_noninteractive)
else:
    # Interactif: tourne à l'infini jusqu'à l'arrêt
    print("Run interactif, Ctrl+c quand fini")
    tour = SA(cities, temperature_interactive)

# Affichage graphique
plt.plot([cities[tour[i % city_count]][0] for i in range(city_count + 1)], [cities[tour[i % city_count]][1] for i in range(city_count + 1)], 'xb-')
plt.show()