import numpy as np 
import matplotlib.pyplot as plt
import networkx as nx

N = 5
NUM_ANTS = 200

def solve_tsp(G, ants, N, num_max_iterations=100, evaporation_rate=0.7):
	# do iterations for tsp
	path_dict = {}
	for iters in range(num_max_iterations):
		path_dict = {}
		for ant in ants:
			ant.reset(N)
		for i in range(0, N):
			# since there are N cities, each ant will take exactly N iterations 
			# to complete it's tour
			for ant in ants:
				ant.choose_next(G, N)

		# Each ant should've completed it's tour by now, else we don't care
		# Evaporate some pheromone
		for edge in G.edges():
			G.edges()[edge]['pheromone'] = (1-evaporation_rate) * G.edges()[edge]['pheromone']

		# Add new pheromone
		for ant in ants:
			p = ant.get_path()
			if p in path_dict:
				path_dict[p] += 1
			else:
				path_dict[p] = 0
			ant.update_pheromone(G)
	# print(path_dict)
	return path_dict

class Ant(object):
	def __init__(self, num_start_points, PH=100, eps=0.1):
		# Places the ant at any of the given starting points randomly
		self.path = []
		self.path_length = 0
		self.PHEROMONE = PH # this is the pheromone that this ant will deposit over the length of its path
		k = np.random.randint(0, num_start_points)
		self.path.append(k) # this ant starts at node k
		self.eps = eps 		# epsilon value to help discriminate between choosing randomly

	def reset(self, num_start_points):
		self.path = []
		k = np.random.randint(0, num_start_points)
		self.path.append(k)
		self.path_length = 0

	def completed_tour(self, N):
		if len(self.path) == N:
			return True
		return False

	def choose_next(self, graph, N):
		last_visited = self.path[-1]
		to_consider = []
		for neigbour in graph.neighbors(last_visited):
			if neigbour not in self.path:
				cost = graph.edges()[last_visited, neigbour]['pheromone']
				to_consider.append((cost, neigbour))

		if to_consider:
			to_eps = np.random.uniform(0,1)
			if to_eps < self.eps:
				# Choose randomly
				k = np.random.randint(0, len(to_consider))
				self.path.append(to_consider[k][1])
			else:
				to_consider.sort()
				self.path.append(to_consider[0][1])
		elif not self.completed_tour(N):
			# am stuck since all current neibours are visited
			# move out randomly
			x = list(graph.neighbors(last_visited))
			if len(x) == 0:
				print('Bad Luck')
				return
			t = np.random.randint(0, len(x))
			self.path.append(x[t])
		else:
			self.path.append(self.path[0])

		# update path length
		if last_visited != self.path[-1]:
			try:
				self.path_length = self.path_length + graph.edges()[(last_visited, self.path[-1])]['weight']
			except:
				pass
		else:
			# The code
			print('Shucks, Not an issue. But for better results try a more dense graph.')
			self.path_length += 0

	def update_pheromone(self, graph):
		for i in range(1, len(self.path)):
			u = self.path[i-1]
			v = self.path[i]
			try:
				graph.edges()[(u, v)]['pheromone'] += self.PHEROMONE / self.path_length 
			except Exception as e:
				print(u, v)

	def get_path(self):
		x = ""
		for i in self.path:
			x = x + str(i) + ", "
		return x

def main(num=0, evaporation_rate=0.7, graph_type=None, num_iters=100, show=True, save=True):
	print('For Experiment {}'.format(num))

	# Initialize ants
	ants = []
	for i in range(0, NUM_ANTS):
		ants.append(Ant(N))

	# Initalize graph
	if not graph_type:
		G = nx.complete_graph(N)
	else:
		G = graph_type
	pos = nx.spring_layout(G)

	for edge in G.edges():
		G.edges()[edge]['weight'] = np.random.randint(5, 20)
		G.edges()[edge]['pheromone'] = 1

	# Perform ACO
	paths = solve_tsp(G, ants, N, num_max_iterations=num_iters, evaporation_rate=evaporation_rate)

	# print(paths)
	converted = []
	for path in paths:
		p = tuple(map(lambda x: int(x.strip()), path.split(',')[:-1]))
		converted.append((paths[path], p))
	converted.sort()
	top_path = converted[-1]
	print('Top Path = ', top_path[1], 'Confidence = ', top_path[0]/NUM_ANTS)

	edge_list = []
	for k in range(1, len(top_path[1])):
		edge_list.append((top_path[1][k-1], top_path[1][k]))

	for edge in G.edges():
		print(edge, G.edges()[edge]['weight'], G.edges()[edge]['pheromone'])

	labels = {}
	for node in G.nodes():
		labels[node] = node

	print(nx.to_numpy_matrix(G))
	plt.figure()

	nx.draw_networkx_nodes(G, pos)
	nx.draw_networkx_edges(G, pos, edge_color='r')
	nx.draw_networkx_edges(G, pos, edgelist=edge_list, edge_color='b')
	nx.draw_networkx_labels(G, pos, labels, font_size=16)

	if show:
		plt.show()
	if save:
		plt.savefig('Figure_{}'.format(num))
	return top_path[0]

if __name__ == '__main__':
	# global NUM_ANTS, N
	expt = 0

	# Variation with number of ants:
	X = []
	Y = []
	for i in range(100, 200, 10):
		NUM_ANTS = i
		q = main(expt, show=False, save=False)
		plt.close()
		expt+=1
		X.append(i)
		Y.append(q)
	plt.figure()
	plt.plot(X, Y)
	plt.show()

	# Variation with evaporation rate:
	NUM_ANTS = 100
	X = []
	Y = []
	for i in np.linspace(0.1, 0.9, 9):
		q = main(expt, evaporation_rate=i, show=False, save=False)
		plt.close()
		expt+=1
		X.append(i)
		Y.append(q)
	plt.figure()
	plt.plot(X, Y)
	plt.show()

	# Variation with number of cities:
	X = []
	Y = []
	for i in range(5, 10):
		N = i
		q = main(expt, show=False, save=False)
		plt.close()
		expt+=1
		X.append(i)
		Y.append(q)
	plt.figure()
	plt.plot(X, Y)
	plt.show()

	# variation with sparsity
	N = 7
	X = []
	Y = []
	for i in range(N+1, N+9):
		G = nx.gnm_random_graph(N, i)
		q = main(expt, graph_type=G, show=False, save=False)
		plt.close()
		expt+=1
		X.append(i)
		Y.append(q)
	plt.figure()
	plt.plot(X, Y)
	plt.show()

	# variation with number of iterations
	N = 5
	X = []
	Y = []
	for i in range(50, 200, 15):
		q = main(expt, num_iters=i, show=False, save=False)
		plt.close()
		expt+=1
		X.append(i)
		Y.append(q)
	plt.figure()
	plt.plot(X, Y)
	plt.show()