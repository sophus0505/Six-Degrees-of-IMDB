import csv
from collections import defaultdict, deque, OrderedDict
from heapq import heappush, heappop
from os import kill
import time

import cProfile, pstats, io
import requests
from bs4 import BeautifulSoup
import re
import dateutil

def readfile(movies_filename, actors_filename):
    movies_and_rating = {}
    actors_in_movie = {}
    actor_names = {}
    actor_and_movies = {}
    nodes = 0

    with open(movies_filename) as file:
        tsv_file = csv.reader(file, delimiter="\t")
        for line in tsv_file:
            movie_id = line[0]
            movie_name = ""

            for word in line[1:-3]:
                movie_name += word + " "
            movie_name += line[-3]

            rating = float(line[-2])
            movies_and_rating[movie_id] = [movie_name, rating]

            actors_in_movie[movie_id] = []
    
    with open(actors_filename) as file:
        tsv_file = csv.reader(file, delimiter="\t")
        for line in tsv_file:
            name_id = line[0]
            nodes += 1
            
            movie_id_list = []

            name = ""
            i = 1
            while line[i][:2] != "tt":
                name += line[i] + " "
                i += 1
            for movie in line[i:]:
                if movie in movies_and_rating:
                    actors_in_movie[movie].append(name_id)
                    movie_id_list.append(movie)

            actor_names[name_id] = name

            actor_and_movies[name_id] = movie_id_list

    return nodes, actors_in_movie, actor_names, movies_and_rating, actor_and_movies

def buildgraph(actors_in_movie, movies_and_rating, actor_and_movies):
    
    V = set() # Set with all the actors
    E = defaultdict(set) # All the actors with the connected actors
    w = dict()
   
    edges = 0
    for actor, movies in actor_and_movies.items():
        V.add(actor)
        for movie in movies:
            rating = movies_and_rating[movie][1]
            weight = 10 - rating

            for ngbr_actor in actors_in_movie[movie]:
                if ngbr_actor == actor:
                    continue
                if ngbr_actor not in E:
                    edges += 1

                E[actor].add(ngbr_actor)

                w[(actor, ngbr_actor)] = weight
            
    nodes = len(E)
    
    print("Oppgave 1\n")
    print(f"Nodes: {nodes}")
    print(f"Edges: {edges}")

    return V, E, w, edges

def women_weights(actor_and_movies, actors_in_movie, actresses_in_movie, total_dict):
    w_w = dict()
   
    for actor, movies in actor_and_movies.items():
        for movie in movies:
            women = int(actresses_in_movie[movie])
            total_actors = total_dict[movie]
        
            for ngbr_actor in actors_in_movie[movie]:
                w_w[(actor, ngbr_actor)] = total_actors - women
    
    return w_w

def bfs_shortest_paths_from(G, s):
    _, E, _, _ = G
    parents = {s : None}
    queue = deque([s])
    result = []

    while queue:
        v = deque.popleft(queue)
        result.append(v)
        for u in E[v]:
            if u not in parents:
                parents[u] = v
                queue.append(u)
    return parents

def bfs_shortest_path_between(G, s, t):
    parents = bfs_shortest_paths_from(G, s)
    v = t
    path = []

    if t not in parents:
        return path

    while v:
        path.append(v)
        v = parents[v]
    path.reverse()
    return path

def print_shortest_path(shortest_path):
    print("\nOppgave 2\n")
    print(actor_names[shortest_path[0]])

    for i in range(1, len(shortest_path)):
        actor1, actor2 = shortest_path[i-1], shortest_path[i]
        for (movie, actors) in actors_in_movie.items():
            if actor1 in actors and actor2 in actors:
                movie_name = movies_and_rating[movie][0]
                movie_rating = float(movies_and_rating[movie][1])
        print(f"===[ {movie_name} {movie_rating} ] ===> {actor_names[shortest_path[i]]}")

def dijkstra(G, s):
    _, E, w, _ = G
    Q = [(0, s)]
    
    D = defaultdict(lambda: float('inf'))
    parents = {s : None}
    D[s] = 0
    while Q:
        cost, v = heappop(Q)
        for u in E[v]:
            c = cost + w[(v, u)]
            if c < D[u]:
                D[u] = c
                heappush(Q, (c, u))
                parents[u] = v
                
    return parents, D

def chillest_path_between(G, s, e):
    parents, D = dijkstra(G, s)

    weight = D[e]
    chillest_path = [e]
    while parents[e]:
        e = parents[e]
        chillest_path.append(e)
    chillest_path.reverse()

    return chillest_path, weight

def print_chillest_path(chillest_path, weight):
    print("\nOppgave 3\n")
    print(actor_names[chillest_path[0]])
    for i in range(1, len(chillest_path)):
        actor1, actor2 = chillest_path[i-1], chillest_path[i]
        max_movie_rating = 0
        for (movie, actors) in actors_in_movie.items():
            if actor1 in actors and actor2 in actors:
                movie_name = movies_and_rating[movie][0]
                movie_rating = float(movies_and_rating[movie][1])

                if movie_rating > max_movie_rating:
                    max_movie_name = movie_name
                    max_movie_rating = movie_rating

        print(f"===[ {max_movie_name} {max_movie_rating} ] ===> {actor_names[chillest_path[i]]}")
    print(f"Total weight: {weight:.1f}")

def components(G):
    V, E, _, _ = G
    sizes = dict()
    visited = set()

    for actor in V:
        if actor in visited:
            continue
        
        else:
            queue = deque([actor])
            parents = {actor : None}

            while queue:
                v = deque.popleft(queue)
                for u in E[v]:
                    if u not in parents:
                        visited.add(u)
                        parents[u] = v
                        queue.append(u)
            
            size = len(parents)
            if size in sizes:
                sizes[size] += 1
            else:
                sizes[size] = 1
    
    o_sizes = OrderedDict(sorted(sizes.items(), reverse=True))
    return o_sizes
    
def print_components(sizes):
    print("\nOppgave 4\n")
    for (size, n) in sizes.items():
        print(f"There are {n} components of size {size}")

def create_txt(G, outfile):
    nm_id1_list = ["nm2255973", "nm0424060", "nm4689420", "nm0000288", "nm0031483"]
    nm_id2_list = ["nm0000460", "nm0000243", "nm0000365", "nm0001401", "nm0931324"]

    with open(outfile, "w") as f:
        f.write("Oppgave 1\n\n")
        V, E, w, edges = G
        f.write(f"Nodes: {len(V)}\n")
        f.write(f"Edges: {edges}\n\n")

        f.write("Oppgave 2\n\n")
        for nm_id1, nm_id2 in zip(nm_id1_list, nm_id2_list):
            shortest_path = bfs_shortest_path_between(G, nm_id1, nm_id2)
            f.write(f"{actor_names[shortest_path[0]]}\n")

            for i in range(1, len(shortest_path)):
                actor1, actor2 = shortest_path[i-1], shortest_path[i]
                for (movie, actors) in actors_in_movie.items():
                    if actor1 in actors and actor2 in actors:
                        movie_name = movies_and_rating[movie][0]
                        movie_rating = float(movies_and_rating[movie][1])
                f.write(f"===[ {movie_name} {movie_rating} ] ===> {actor_names[shortest_path[i]]}\n")

            f.write("\n")

        f.write("Oppgave 3\n\n")
        for nm_id1, nm_id2 in zip(nm_id1_list, nm_id2_list):
            chillest_path, weight = chillest_path_between(G, nm_id1, nm_id2)
            
            f.write(f"{actor_names[chillest_path[0]]}\n")

            for i in range(1, len(chillest_path)):
                actor1, actor2 = chillest_path[i-1], chillest_path[i]
                max_movie_rating = 0
                for (movie, actors) in actors_in_movie.items():
                    if actor1 in actors and actor2 in actors:
                        movie_name = movies_and_rating[movie][0]
                        movie_rating = float(movies_and_rating[movie][1])

                        if movie_rating > max_movie_rating:
                            max_movie_name = movie_name
                            max_movie_rating = movie_rating

                f.write(f"===[ {max_movie_name} {max_movie_rating} ] ===> {actor_names[chillest_path[i]]}\n")
            f.write(f"Total weight: {weight:.1f}\n\n")

        f.write("Oppgave 4\n\n")
        sizes = components(G)
        for (size, n) in sizes.items():
            f.write(f"There are {n} components of size {size}\n")

def getMovieQuote(movie_id, movie_name):
    """Scrapes imdb.com for a movie quote from the given movie if it exists
    on the imdb page. If it exists it prints the quote to the terminal. 

    Args:
        movie_id (str): The imdb movie id for the movie given in movies.tsv
        movie_name (str): The name of the movie, for printing
    """
    url = 'https://www.imdb.com/title/' + movie_id
    result = requests.get(url)

    assert result.status_code == 200

    src = result.content
    document = BeautifulSoup(src, 'lxml')
    classy="ipc-html-content ipc-html-content--base Quotes__StyledHTMLContent-ff1m6h-1 dAalVs"

    kuk = document.find('div', class_=classy)
    try:
        cocks = kuk.find_all('p')
    except AttributeError:
        print(f"{movie_name} has no quote 🙁 ")
        return 

    quote = []
    for i in cocks:
        quote.append(list(i.stripped_strings))

    print(f"Quote from {movie_name}:")
    underline = '='*(len(movie_name) + 12)
    print(underline)
    for line in quote:
        # print(line)
        if len(line) == 1: 
            print(f"{line[0][1:-1]}")
        elif len(line) == 2:
            character = line[0]
            saying = line[1]
            print(f"{character}: {saying[2:]}")
            # print(f"\t")
        else:
            print(f"{line[0]}: ", end='')
            for elem in line[1:]:
                if elem == ':':
                    pass
                elif elem[0] == '[':
                    print(f"{elem} ", end='')
                else:
                    print(f"{elem}", end='')
            print('')
    print(underline)

def create_actress_dict(in_file):
    """Creates two dictionaries: actresses_in_movie and total_dict.
    Actresses_in_movie have keys 'movie' and items 'the actors in the movie'. 

    Args:
        in_file ([type]): [description]

    Returns:
        [type]: [description]
    """
    actresses_in_movie = defaultdict(lambda: 0)
    total_dict = defaultdict(lambda: 0)

    with open(in_file) as file: #, open(out_file, "wt") as out_file:
        tsv_file = csv.reader(file, delimiter="\t")
        # tsv_writer = csv.writer(out_file, delimiter='\t')
        for line in tsv_file:
            
            sex = line[4]
            if sex[:4] == "actr":
                for movie in line:
                    if movie[:2] == "tt":
                        actresses_in_movie[movie] += 1
            for movie in line:
                if movie[:2] == "tt":
                    total_dict[movie] += 1
                # tsv_writer.writerow([line[0]])
    
    return actresses_in_movie, total_dict

def createActressList(actress_file):
    actresses = []
    with open(actress_file) as file:
        tsv_file = csv.reader(file, delimiter="\t")
        for line in tsv_file:
            actresses.append(line[0])

    return actresses

def dijkstra_women(G, w_w, s):
    _, E, _, _ = G
    Q = [(0, s)]
    
    D = defaultdict(lambda: float('inf'))
    parents = {s : None}
    D[s] = 0
    while Q:
        cost, v = heappop(Q)
        for u in E[v]:
            c = cost + w_w[(v, u)]
            if c < D[u]:
                D[u] = c
                heappush(Q, (c, u))
                parents[u] = v
                
    return parents, D

def least_sexistic_path(G, w_w, s, e):
    parents, D = dijkstra_women(G, w_w, s)

    weight = D[e]
    least_sexistic_path = [e]
    while parents[e]:
        e = parents[e]
        least_sexistic_path.append(e)
    least_sexistic_path.reverse()

    return least_sexistic_path, weight

def print_least_sexistic_path(least_sexistic_path, weight):
    print("\nOppgave 5\n")
    print(actor_names[least_sexistic_path[0]])
    for i in range(1, len(least_sexistic_path)):
        actor1, actor2 = least_sexistic_path[i-1], least_sexistic_path[i]
        max_movie_rating = 0
        for (movie, actors) in actors_in_movie.items():
            if actor1 in actors and actor2 in actors:
                movie_name = movies_and_rating[movie][0]
                movie_rating = float(movies_and_rating[movie][1])

                if movie_rating > max_movie_rating:
                    max_movie_name = movie_name
                    max_movie_rating = movie_rating

        print(f"===[ {max_movie_name} {max_movie_rating} ] ===> {actor_names[least_sexistic_path[i]]}")
    print(f"Total weight: {weight:.1f}")

if __name__ == "__main__":
    start1 = time.time()
    start2 = time.time()
    
    movies_filename, actors_filename = "movies.tsv", "actors.tsv"
    nodes, actors_in_movie, actor_names, movies_and_rating, actor_and_movies = readfile(movies_filename, actors_filename)
    

    # Oppgave 1
    G = buildgraph(actors_in_movie, movies_and_rating, actor_and_movies)

    # Oppgave 2
    path = bfs_shortest_path_between(G, "nm0000255", "nm0095013")
    # print_shortest_path(path)

    # Oppgave 3

    # chillest_path, weight = chillest_path_between(G, "nm0377336", "nm2640105")
    # print_chillest_path(chillest_path, weight)

    # chillest_path, weight = chillest_path_between(G, "nm0031483", "nm2640105")
    # print_chillest_path(chillest_path, weight)

    # Oppgave 4
    # sizes = components(G)
    # print_components(sizes)

    create_txt(G, "oblig2.txt")

    end2 = time.time()

    # Oppgave 5 Quote
    movie_id = "tt0076759"; movie_name = "Star Wars: Episode IV – A New Hope"
    getMovieQuote(movie_id, movie_name)

    # Oppgave 5 Ladies

    actresses_in_movie, total_dict = create_actress_dict("data.tsv")
    w_w = women_weights(actor_and_movies, actors_in_movie, actresses_in_movie, total_dict)
    path, weight = least_sexistic_path(G, w_w, "nm0031483", "nm0000138")
    print_least_sexistic_path(path, weight)
    end1 = time.time()


    print(f"total runtime: {end1 - start1}s")
    print(f"1-4 runtime: {end2 - start2}")


    


    




    
  
