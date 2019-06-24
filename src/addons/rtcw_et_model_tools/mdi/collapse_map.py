
# this code was ported to python from:
# https://github.com/melax/sandbox/blob/master/bunnylod/progmesh.cpp
# the algorithm was slightly modified to prioritize certain vertices in
# non-sealed surfaces
# complete algorithm is explained, search "A simple, Fast, and Effective
# Polygon Reduction Algorithm"

# TODO use set and switch from camelCase

import mathutils

import logging

vertices = []
triangles = []

# checks for object identity
# this only works if the listItems are not preallocated by
# python, e.g. it wont work if list items are small integers
def contains(list, listItem):
    for item in list:
        if item is listItem:
            return True
    return False

# only adds an item to a list if not already present
def addUnique(list, listItem):
    isPresent = contains(list, listItem)
    if isPresent == False:
        list.append(listItem)

# remove an item from a list
def remove(list, listItem):
    for i in range(0, len(list)):
        item = list[i]
        if item is listItem:
            list.pop(i)
            break
    isPresent = contains(list, listItem)
    if isPresent == True:
        logging.warning("item is still present")

# remove a triangle
# this acts like a destructor, it should remove all references from all arrays to this triangle
# python will then clean it up some time afterwards
def removeTriangle(triangle):
    remove(triangles, triangle)

    for vertex in triangle.vertices:
        remove(vertex.faces, triangle)

    for i1 in range(0, 3):
        i2 = (i1+1)%3
        if triangle.vertices[i1] == None or triangle.vertices[i2] == None:
            continue
        triangle.vertices[i1].removeIfNonNeighbor(triangle.vertices[i2])
        triangle.vertices[i2].removeIfNonNeighbor(triangle.vertices[i1])

# remove a vertex
# this acts like a destructor, it should remove all references from all arrays to this triangle
# python will then clean it up some time afterwards
def removeVertex(vertex):
    if len(vertex.faces) > 0:
        logging.warning("warning: this vertex is still part of some triangles ", len(vertex.faces))
        return

    neighborsToRemove = []
    for neighbor in vertex.neighbors:
        neighborsToRemove.append(neighbor)

    for neighbor in neighborsToRemove:
        remove(neighbor.neighbors, vertex)
        remove(vertex.neighbors, neighbor)

    '''
    while i > 0:
        remove(vertex.neighbors[0].neighbors, vertex)
        vertex.neighbors[0] = None
        remove(vertex.neighbors, vertex.neighbors[0])
        i = len(vertex.neighbors)
    '''

    remove(vertices, vertex)

class CMTriangle:

    def __init__(self, v0, v1, v2):

        if v0 is v1 or v1 is v2 or v2 is v0:
            logging.warning("warning: triangle not valid")
            return

        self.vertices = [v0, v1, v2] # the 3 points that make this tri
        self.computeNormal() # unit vector othogonal to this face
        triangles.append(self)
        for v in self.vertices:
            v.faces.append(self)
            for i in range(0, len(self.vertices)):
                if self.vertices[i] is v:
                    continue
                addUnique(v.neighbors, self.vertices[i])

    def computeNormal(self):

        a = self.vertices[0].position
        b = self.vertices[1].position
        c = self.vertices[2].position
        n = b - a
        m = c - a
        self.normal = n.cross(m).normalized()

    def replaceVertex(self, vOld, vNew):

        if vOld == None or vNew == None:
            logging.warning("warning: replaceVertex by None")
            return
        if (vOld is self.vertices[0] or vOld is self.vertices[1] or vOld is self.vertices[2]) == False:
            logging.warning("warning: trying to replace vertex which is not part of triangle")
            return
        if vNew is self.vertices[0] or vNew is self.vertices[1] or vNew is self.vertices[2]:
            logging.warning("warning: trying to replace to vertex which is already part of triangle")
            return

        if vOld is self.vertices[0]:
            self.vertices[0] = vNew
        elif vOld is self.vertices[1]:
            self.vertices[1] = vNew
        else:
            if vOld is self.vertices[2]:
                self.vertices[2] = vNew
            else:
                logging.warning("warning: did not find old vertex when replacing")
                return
        remove(vOld.faces, self)
        if contains(vOld.faces, self):
            logging.warning("warning: face still contains vertex")
            return
        vNew.faces.append(self)

        for i in range(0, 3):
            vOld.removeIfNonNeighbor(self.vertices[i])
            self.vertices[i].removeIfNonNeighbor(vOld)
        for i in range(0, 3):
            if contains(self.vertices[i].faces, self) == False:
                logging.warning("triangle contain failed")
                return
            for j in range(0, 3):
                if self.vertices[i].id != self.vertices[j].id:
                    addUnique(self.vertices[i].neighbors, self.vertices[j])
        self.computeNormal()

    def hasVertex(self, v):
        hasVertex = False
        if self.vertices[0] is v or self.vertices[1] is v or self.vertices[2] is v:
            hasVertex = True
        return hasVertex

class CMVertex:

    def __init__(self, v, id):

        self.position = mathutils.Vector((v[0], v[1], v[2])) # location of point in euclidean space
        self.id = id # place of vertex in original Array
        vertices.append(self)

        self.neighbors = [] # adjacent vertices
        self.faces = [] # adjacent triangles
        self.objdist = 1000000 # cached cost of collapsing edge
        self.collapse = None # candidate vertex for collapse

    def removeIfNonNeighbor(self, n):
        # removes n from neighbor Array if n isn't a neighbor
        if contains(self.neighbors, n) == True:
            return
        for face in self.faces:
            if face.hasVertex(n) == True:
                return
        remove(self.neighbors, n)


def countFacesOnEdge(u, v):

    count = 0
    for faceU in u.faces:
        for faceV in v.faces:
            if faceU.hasVertex(v) and faceV.hasVertex(u):
                count += 1

    return count

def hasSilhouetteEdge(u):

    hasSilhouetteEdge = False
    for neighbor in u.neighbors:
        if countFacesOnEdge(u, neighbor) <= 1:
            hasSilhouetteEdge = True
            break

    return hasSilhouetteEdge

def computeEdgeCollapseCost(u, v):
	# if we collapse edge uv by moving u to v then how
	# much different will the model change, i.e. how much "error".
	# Texture, vertex normal, and border vertex code was removed
	# to keep this demo as simple as possible.
	# The method of determining cost was designed in order
	# to exploit small and coplanar regions for
	# effective polygon reduction.
	# Is is possible to add some checks here to see if "folds"
	# would be generated.  i.e. normal of a remaining face gets
	# flipped.  I never seemed to run into this problem and
	# therefore never added code to detect this case.
    edgeLength = (u.position - v.position).length
    curvature = 0.0

    # find the "sides" triangles that are on the edge uv
    sides = []
    for face in u.faces:
        if face.hasVertex(v):
            sides.append(face)

    # use the triangle facing most away from the sides
    # to determine our curvature term
    for face in u.faces:
        minCurv = 1.0 # curve for face i and closer side to it
        for side in sides:
            dotProd = face.normal.dot(side.normal) #  use dot product of face normals.
            minCurv = min(minCurv, (1 - dotProd) / 2.0)
        curvature = max(curvature, minCurv)

    # the more coplanar the lower the curvature term
    return edgeLength * curvature

def computeEdgeCostAtVertex(v):
	# compute the edge collapse cost for all edges that start
	# from vertex v.  Since we are only interested in reducing
	# the object by selecting the min cost edge at each step, we
	# only cache the cost of the least cost edge at this vertex
	# (in member variable collapse) as well as the value of the
	# cost (in member variable objdist).
    if len(v.neighbors) == 0:
        # v doesn't have neighbors so it costs nothing to collapse
        v.collapse = None
        v.objDist = -0.01
        return

    v.collapse = None
    v.objDist = 10000000
    # search all neighboring edges for "least cost" edge
    for neighbor in v.neighbors:
        dist = computeEdgeCollapseCost(v, neighbor)
        if dist < v.objDist:
            v.collapse = neighbor
            v.objDist = dist

    if hasSilhouetteEdge(v) == True:
        v.objDist += 10000

def computeAllEdgeCollapseCosts():

    for vertex in vertices:
        computeEdgeCostAtVertex(vertex)

def collapse(u, v):

	# Collapse the edge uv by moving vertex u onto v
	# Actually remove tris on uv, then update tris that
	# have u to have v, and then remove u.
    if v == None:
        # u is a vertex all by itself so just delete it
        removeVertex(u)
        return

    # make tmp a Array of all the neighbors of u
    tmp = []
    for neighbor in u.neighbors:
        tmp.append(neighbor)

    facesToDelete = []
    facesToUpdate = []
    for face in u.faces:
        if face.hasVertex(v) == True:
            facesToDelete.append(face)
        else:
            facesToUpdate.append(face)

    # delete triangles on edge uv:
    for face in facesToDelete:
        removeTriangle(face)

    # update remaining triangles to have v instead of u
    for face in facesToUpdate:
        face.replaceVertex(u, v)

    removeVertex(u)

    # recompute the edge collapse costs for neighboring vertices
    for neighbor in tmp:
        computeEdgeCostAtVertex(neighbor)

def addVertices(verts):

    for i in range(0, len(verts)):
        vertex = CMVertex(verts[i], i)

def addFaces(faces):

    for i in range(0, len(faces)):
        face = faces[i]
        triangle = CMTriangle(vertices[face[0]], vertices[face[1]], vertices[face[2]])

def minimumCostEdge():
	# Find the edge that when collapsed will affect model the least.
	# This funtion actually returns a Vertex, the second vertex
	# of the edge (collapse candidate) is stored in the vertex data.
	# Serious optimization opportunity here: this function currently
	# does a sequential search through an unsorted Array :-(
	# Our algorithm could be O(n*lg(n)) instead of O(n*n)
    mn = vertices[0]
    for vertex in vertices:
        if vertex.objDist < mn.objDist:
            mn = vertex
    return mn

def progressiveMesh(vertexData, triangleData):

    addVertices(vertexData) # put input data into our data structures
    addFaces(triangleData)

    minLod = None

    computeAllEdgeCollapseCosts() # cache all edge collapse costs

    permutation = [] # allocate space
    for i in range(0, len(vertices)):
        permutation.append(None)

    map = [] # allocate space
    for i in range(0, len(vertices)):
        map.append(None)

    # reduce the object down to nothing
    while (len(vertices) > 0):

        # get the next vertex to collapse
        mn = minimumCostEdge()
        # keep track of this vertex, i.e. the collapse ordering
        permutation[mn.id] = len(vertices) - 1
        # keep track of vertex to which we collapse to
        if mn.collapse != None:
            map[len(vertices) - 1] = mn.collapse.id
        else:
            map[len(vertices) - 1] = -1

        if mn.objDist >= 10000 and minLod == None:
            minLod = len(vertices)

        # collapse this edge
        collapse(mn, mn.collapse)

    # reorder the map Array based on the collapse ordering
    for i in range(0, len(map)):
        if map[i] != -1:
            map[i] = permutation[map[i]]
        else:
            map[i] = 0

    if minLod == None:
        minLod = 0

	# The caller of this function should reorder their vertices
	# according to the returned "permutation".

    return map, permutation, minLod

def calculate(vertexData, triangleData):

    (map, permutation, minLod) = progressiveMesh(vertexData, triangleData)
    return map, permutation, minLod
