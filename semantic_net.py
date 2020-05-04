

def get_dist_network(id_file='./data/clics/clics2-network-ids.txt',
                     edge_file='./data/clics/clics2-network-edges.txt',
                     max_dist=2):
    idsToNames = {}
    with open(id_file, encoding='utf8') as f:
        for line in f:
            cells = line.strip().split('\t')
            idsToNames[cells[0]] = cells[1]
    edges = {}
    with open(edge_file, encoding='utf8') as f:
        for line in f:
            cells = line.strip().split('\t')
            concept1 = idsToNames[cells[0]]
            concept2 = idsToNames[cells[1]]
            try:
                edges[concept1].add(concept2)
            except KeyError:
                edges[concept1] = {concept2}
            try:
                edges[concept2].add(concept1)
            except KeyError:
                edges[concept2] = {concept1}

    distances = {}
    for concept in edges.keys():
        put(distances, concept, concept, 0)
        calculate_dist(distances, edges, concept, concept, 1, max_dist)
    return distances


def put(distances, concept1, concept2, dist):
    try:
        if distances[(concept1, concept2)] <= dist:
            return
    except KeyError:
        pass
    distances[(concept1, concept2)] = dist


def calculate_dist(distances, edges, ref_concept, cur_concept, dist, max_dist):
    if dist > max_dist:
        return
    for neighbour in edges[cur_concept]:
        put(distances, ref_concept, neighbour, dist)
        calculate_dist(distances, edges, ref_concept, neighbour, dist + 1,
                       max_dist)
