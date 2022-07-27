import time


class Node:
    def __init__(self, name):
        self.name = name
        self.neighbours = []
        self.edges = 0

    def add(self, neighbours):
        for neighbour in neighbours:
            self.neighbours.append(neighbour)
        
    
            
    
    


class Graph:
    def __init__(self, movies_filename, actors_filename):
        self._create_graph(movies_filename, actors_filename)
        #self._create_graph()

    # def _create_graph(self):
    #     self._graph = {}
    #     self.nodes = len(self._actors)
    #     self.edges = 0
    #     for _, (actor, movies) in enumerate(self._actors.items()):
    #         self._graph[actor] = []
    #         for movie in movies:
    #             for ngbr_actor in self._movies_and_actors[movie]:
    #                 if ngbr_actor not in self._graph:
    #                     self.edges += 1
    #                 self._graph[actor].append(ngbr_actor)

    def _create_graph(self, movies_filename, actors_filename):
        graph = {}

        movies = {}
        movies_and_actors = {}
        actors = {}

        edges = 0
        nodes = 0

        with open(movies_filename, "r") as f:
            for line in f:
                word_list = line.split()

                movie_id = word_list[0]
                movie_name = ""

                for word in word_list[1:-3]:
                    movie_name += word + " "
                movie_name += word_list[-3]

                rating = word_list[-2]
                movies[movie_id] = [movie_name, rating]
                movies_and_actors[movie_id] = []

        
    
        

        with open(actors_filename, "r") as f:
            for line in f:
                word_list = line.split()

                movie_id_list = []
                name_id = word_list[0]
                nodes += 1

                for movie in word_list[1:]:
                    if movie[:2] == "tt":
                        if movie in movies:
                            movie_id_list.append(movie)
                            movies_and_actors[movie].append(name_id)

                actors[name_id] = movie_id_list
                graph[name_id] = Node(name_id)

        with open(actors_filename, "r") as f:
            for line in f:
                word_list = line.split()

                name_id = word_list[0]
                kuk = 0
                for movie in word_list[1:]:
                    if movie[:2] == "tt":
                        if movie in movies:
                            neighbours = movies_and_actors[movie]
                            neighbours.remove(name_id)
                            edges += len(neighbours)
                                    
                            graph[name_id].add(neighbours)
        
        
        
                                
        self._edges = edges
        self._nodes = nodes

        self._movies = movies
        self._actors = actors
        self._graph = graph
        

    def shortest_path(self, from_actor, to_actor):
        pass

    def chillest_path(self, from_actor, to_actor):
        pass


if __name__ == "__main__":
    movies_filename = "movies.tsv"
    actors_filename = "actors.tsv"

    start = time.time()
    graph = Graph(movies_filename, actors_filename)
    end = time.time()

    runtime = end -start

    print(f"{runtime = :.4f}s")

    print(f"{graph._edges = } {graph._nodes = }")
