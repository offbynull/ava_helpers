def get_edges_connecting_vertex(face, vertex):
    return [
        edge for edge in face.Edges
        if any(v.isSame(vertex) for v in edge.Vertexes)
    ]