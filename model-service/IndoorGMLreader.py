#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import re
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import math

from commodity import path
from lxml import etree
from shapely.geometry import Polygon
from shapely.geometry import Point
from scipy.spatial import KDTree

import Ice
Ice.loadSlice(path.get_project_dir('.') + '/UrbanService.ice')
import UrbanService


ns = {'indoorgml': 'http://www.opengis.net/indoorgml/1.0/core',
      'gml': 'http://www.opengis.net/gml/3.2',
      'CellSpaceBoundary': '{http://www.opengis.net/indoorgml/1.0/core}CellSpaceBoundary',
      'CellSpace': '{http://www.opengis.net/indoorgml/1.0/core}CellSpace',
      'SpaceLayer': '{http://www.opengis.net/indoorgml/1.0/core}SpaceLayer',
      'id': '{http://www.opengis.net/gml/3.2}id',
      'href': '{http://www.w3.org/1999/xlink}href'}


class IndoorGMLreader:
    def __init__(self, _file):
        self.file = _file
        self.loadCellSpaceBoundaries()
        self.loadCellSpaces()
        self.createKDTree()
        self.loadSpaceLayers()

    def loadCellSpaceBoundaries(self):
        self.cellSpaceBoundaries = {}
        for (event, node) in etree.iterparse(self.file, events=['end'],
                                             tag=ns['CellSpaceBoundary'],
                                             huge_tree=True):

            cellSpaceBoundary_id = node.attrib[ns['id']]
            cellSpaceBoundary_name = node.find('gml:name', ns).text

            cellSpaceBoundary_usage = None
            cellSpaceBoundary_material = None
            if(node.find('gml:description', ns) is not None):
                description = node.find('gml:description', ns).text.split("/")

                for des in description:
                    des_type = des.split("=")[0]
                    des_value = des.split("=")[1]
                    if(des_type == "Usage"):
                        cellSpaceBoundary_usage = des_value
                    elif(des_type == "Material"):
                        cellSpaceBoundary_material = des_value

            surface_id = node.find('indoorgml:geometry3D', ns).find(
                'gml:Polygon', ns).attrib[ns['id']]

            cellSpaceBoundary_linearRing_node = node.find('indoorgml:geometry3D', ns).find(
                'gml:Polygon', ns).find('gml:exterior', ns).find('gml:LinearRing', ns)

            linearRing = []
            for pos in cellSpaceBoundary_linearRing_node.findall('gml:pos', ns):
                position = pos.text.split()
                linearRing.append(UrbanService.position3D(
                    float(position[0]),
                    float(position[1]),
                    float(position[2])))

            geometry = UrbanService.Geometry3D(
                'No id', [UrbanService.Surface(surface_id, linearRing)])
            self.cellSpaceBoundaries[cellSpaceBoundary_id] = UrbanService.cellSpaceBoundary(
                cellSpaceBoundary_id, cellSpaceBoundary_name,
                cellSpaceBoundary_usage, cellSpaceBoundary_material, geometry)

            node.clear()

    def loadCellSpaces(self):
        self.CellSpaces = {}
        self.shapePoligons = {}

        for (event, node) in etree.iterparse(self.file,
                                             tag=ns['CellSpace'],
                                             huge_tree=True):

            cellSpace_id = node.attrib[ns['id']]
            cellSpace_name = node.find('gml:name', ns).text

            cellSpace_usage = None
            if(node.find('gml:description', ns) is not None):
                dirty_cellSpace_usage = node.find(
                    'gml:description', ns).text
                cellSpace_usage = re.split(':|=', dirty_cellSpace_usage)[1]

            cellSpace_duality_node = node.find('indoorgml:duality', ns)
            cellSpace_duality = None
            if(cellSpace_duality_node is not None):
                cellSpace_duality = cellSpace_duality_node.attrib[ns['href']][1:]

            geometry_id = node.find('indoorgml:Geometry3D', ns).find(
                'gml:Solid', ns).attrib[ns['id']]

            surfaceMember_id = node.find('indoorgml:Geometry3D', ns).find(
                'gml:Solid', ns).attrib[ns['id']]

            shell_node = node.find('indoorgml:Geometry3D', ns).find(
                'gml:Solid', ns).find('gml:exterior', ns).find('gml:Shell', ns)

            surfaces = []
            for surfaceMember in shell_node.findall('gml:surfaceMember', ns):
                surface_id = surfaceMember.find(
                    'gml:Polygon', ns).attrib[ns['id']]
                linearRing_node = surfaceMember.find('gml:Polygon', ns).find(
                    'gml:exterior', ns).find('gml:LinearRing', ns)

                linearRing = []

                for pos in linearRing_node.findall('gml:pos', ns):
                    position = pos.text.split()
                    linearRing.append(UrbanService.position3D(
                        float(position[0]), float(position[1]), float(position[2])))

                surfaces.append(UrbanService.Surface(surface_id, linearRing))

            cellSpaceBoundaries = []
            for partialboundedByNode in node.findall('indoorgml:partialboundedBy', ns):
                cellSpaceBoundaries.append(
                    partialboundedByNode.attrib[ns['href']][1:])

            geometry = UrbanService.Geometry3D(geometry_id, surfaces)
            self.CellSpaces[cellSpace_id] = UrbanService.cellSpace(cellSpace_id, cellSpace_name,
                                                                   cellSpace_usage, cellSpace_duality, geometry, cellSpaceBoundaries)

            self.addBasePolygonOfCell(surfaces, cellSpace_id)
            node.clear()

    def addBasePolygonOfCell(self, surfaces, cellSpace_id):
        z_base_coords = math.inf
        base_surface = None

        for surface in surfaces:
            if(all(point.z == surface.linearRing[0].z for point in surface.linearRing)):
                if(surface.linearRing[0].z < z_base_coords):
                    z_base_coords = surface.linearRing[0].z
                    base_surface = surface

        points = []
        for point in base_surface.linearRing:
            points.append([point.x, point.y, z_base_coords])

        polygon_cell = Polygon(points)
        centroid_cell = polygon_cell.centroid
        self.shapePoligons[(centroid_cell.x, centroid_cell.y, z_base_coords)] = [
            cellSpace_id, polygon_cell]

    def createKDTree(self):
        points = []
        for key in self.shapePoligons.keys():
            points.append(key)

        self.kdtree = KDTree(points)

    def loadSpaceLayers(self):
        self.spaceLayers = {}

        for spaceLayer_id in self.get_SpaceLayers_id():
            self.loadSpaceLayer(spaceLayer_id)

    def loadSpaceLayer(self, spaceLayer_id):
        self.spaceLayers[spaceLayer_id] = nx.Graph()
        root = None
        for (event, node) in etree.iterparse(self.file,
                                             tag=ns['SpaceLayer'],
                                             huge_tree=True):

            if(node.attrib[ns['id']] == spaceLayer_id):
                root = node
                break

        nodes_node = root.find('indoorgml:nodes', ns)
        edges_node = root.find('indoorgml:edges', ns)

        self.loadNodes(nodes_node, self.spaceLayers[spaceLayer_id])
        self.loadEdges(edges_node, self.spaceLayers[spaceLayer_id])

    def loadNodes(self, root, graph):
        for stateMember in root.findall('indoorgml:stateMember', ns):
            state_node = stateMember.find('indoorgml:State', ns)
            state_id = state_node.attrib[ns['id']]
            state_name = state_node.find('gml:name', ns).text

            position_coords = state_node.find('indoorgml:geometry', ns).find(
                'gml:Point', ns).find('gml:pos', ns).text.split()

            position = UrbanService.position3D(
                float(position_coords[0]), float(position_coords[1]), float(position_coords[2]))

            state_duality_node = state_node.find('indoorgml:duality', ns)
            state_duality = None
            if(state_duality_node is not None):
                state_duality = state_duality_node.attrib[ns['href']][1:]

            state = UrbanService.state(
                state_id, position, state_name, state_duality)
            graph.add_node(state_id, obj=state)

    def loadEdges(self, root, graph):
        for transitionMember in root.findall('indoorgml:transitionMember', ns):
            transition_node = transitionMember.find('indoorgml:Transition', ns)
            transition_id = transition_node.attrib[ns['id']]
            transition_name = transition_node.find('gml:name', ns).text
            transition_weight = float(
                transition_node.find('indoorgml:weight', ns).text)

            transition_duality_node = transition_node.find(
                'indoorgml:duality', ns)
            transition_duality = None
            if(transition_duality_node is not None):
                transition_duality = transition_duality_node.attrib[ns['href']][1:]

            connects = transition_node.findall('indoorgml:connects', ns)
            state_ref_1 = connects[0].attrib[ns['href']][1:]
            state_ref_2 = connects[1].attrib[ns['href']][1:]

            lineString = []

            for pos in transition_node.find('indoorgml:geometry', ns).find('gml:LineString', ns).findall('gml:pos', ns):
                position = pos.text.split()
                lineString.append(UrbanService.position3D(
                    float(position[0]), float(position[1]), float(position[2])))

            transition = UrbanService.transition(
                transition_id, transition_name, transition_weight, transition_duality, state_ref_1, state_ref_2, lineString)
            graph.add_edge(state_ref_1, state_ref_2, obj=transition)

    def drawLayer(self, spaceLayer_id):
        nx.draw(self.spaceLayers[spaceLayer_id], with_labels=True)
        plt.show()

    def get_SpaceLayers_id(self):
        spaceLayers_id = []
        for (event, node) in etree.iterparse(self.file,
                                             tag=ns['SpaceLayer'],
                                             huge_tree=True):

            spaceLayers_id.append(node.attrib[ns['id']])

        return spaceLayers_id

    def findCellIDofPointInKDTree(self, spaceLayerID, position):
        z_coord_of_position_ground = self.calculateGroundOfPosition(position.z)
        point = [position.x, position.y, z_coord_of_position_ground]
        distances, ndx = self.kdtree.query(point, k=len(self.CellSpaces))

        for n in ndx:
            centroid_cell_coords = self.kdtree.data[n]
            cellSpace_id, polygon_cell = self.shapePoligons[(centroid_cell_coords[0],
                                                             centroid_cell_coords[1],
                                                             centroid_cell_coords[2])]

            polygon_z_coords = np.asarray(polygon_cell.exterior.coords)[0][2]
            if(spaceLayerID == self.getLayerOfaCell(cellSpace_id) and polygon_cell.contains(Point(point)) and
               polygon_z_coords == point[2]):
                return cellSpace_id
                break
        return None

    def calculateGroundOfPosition(self, z_coor):
        return int(z_coor / 3) * 3

    def getCellreference(self, cellID):
        if cellID in self.CellSpaces:
            return self.CellSpaces[cellID]
        else:
            raise Exception('Invalid cellID')

    def getLayerOfaCell(self, cellID):
        cellSpace = self.getCellreference(cellID)
        cellSpace_duality = cellSpace.duality

        for spaceLayerId in self.get_SpaceLayers_id():
            self.igmlLayer_graph = self.spaceLayers[spaceLayerId]

            if(cellSpace_duality in self.igmlLayer_graph.nodes):
                return spaceLayerId

    def getLayerOfaBoundary(self, cellSpaceBoundaryID):
        for cellToCheq in self.CellSpaces.values():
            if(cellSpaceBoundaryID in cellToCheq.cellSpaceBoundaries):
                return self.getLayerOfaCell(cellToCheq.id)
