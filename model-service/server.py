#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys

import Ice
import networkx as nx
from commodity import path
from shapely.geometry import Point

from IndoorGMLreader import IndoorGMLreader

Ice.loadSlice(path.get_project_dir('.') + '/model-service/UrbanService.ice')
import UrbanService


class IgmlLayerI(UrbanService.IgmlLayer):
    def __init__(self, model):
        self.model = model

    def isConnectedCell(self, referenceCellID, cellToCheqID, current=None):
        spaceLayerID = self.model.getLayerOfaCell(referenceCellID)
        referenceCellSpace = self.model.getCellreference(referenceCellID)
        cellSpaceToCheq = self.model.getCellreference(cellToCheqID)

        referenceCellSpace_duality = referenceCellSpace.duality
        cellSpaceToCheq_duality = cellSpaceToCheq.duality

        return cellSpaceToCheq_duality in self.model.spaceLayers[spaceLayerID].neighbors(referenceCellSpace_duality)

    def isAdjacentCell(self, referenceCellID, cellToCheqID, current=None):
        referenceCellSpace = self.model.getCellreference(referenceCellID)
        cellSpaceToCheq = self.model.getCellreference(cellToCheqID)

        referenceCellSpaceBoundaries = referenceCellSpace.cellSpaceBoundaries
        cellSpaceToCheqBoundaries = cellSpaceToCheq.cellSpaceBoundaries

        return any(cellSpaceToCheqBoundary in referenceCellSpaceBoundaries for cellSpaceToCheqBoundary in cellSpaceToCheqBoundaries)

    def getConnectedCells(self, referenceCellID, current=None):
        connectedCells = []
        spaceLayerID = self.model.getLayerOfaCell(referenceCellID)
        referenceCellSpace = self.model.getCellreference(referenceCellID)
        referenceCellSpace_duality = referenceCellSpace.duality

        for neighbor in self.model.spaceLayers[spaceLayerID].neighbors(referenceCellSpace_duality):
            connectedCells.append(
                self.model.spaceLayers[spaceLayerID].nodes[neighbor]['obj'].duality)

        return connectedCells

    def getAdjacentCells(self, referenceCellID, current=None):
        adjacentCells = []

        for cellToCheqID in self.model.CellSpaces:
            if self.isAdjacentCell(referenceCellID, cellToCheqID) and cellToCheqID != referenceCellID:
                adjacentCells.append(cellToCheqID)

        return adjacentCells

    def getBoundariesBetweenCells(self, referenceCellID1, referenceCellID2, current=None):
        cellSpaceBoundariesID = []
        cellSpace1 = self.model.getCellreference(referenceCellID1)
        cellSpace2 = self.model.getCellreference(referenceCellID2)

        cellSpace1Boundaries = cellSpace1.cellSpaceBoundaries
        cellSpace2Boundaries = cellSpace2.cellSpaceBoundaries

        for cellSpace1Boundary in cellSpace1Boundaries:
            if(cellSpace1Boundary in cellSpace2Boundaries):
                cellSpaceBoundariesID.append(cellSpace1Boundary)

        return cellSpaceBoundariesID

    def getCells(self, spaceLayerID, current=None):
        cells = []

        for cellToCheq in self.model.CellSpaces.values():
            if(self.model.getLayerOfaCell(cellToCheq.id) == spaceLayerID):
                cells.append(cellToCheq)

        return cells

    def getCellSpaceBoundaries(self, spaceLayerID, current=None):
        cellSpaceBoundaries = []

        for cellSpaceBoundary in self.model.cellSpaceBoundaries.values():
            if(self.model.getLayerOfaBoundary(cellSpaceBoundary.id) == spaceLayerID):
                cellSpaceBoundaries.append(cellSpaceBoundary)

        return cellSpaceBoundaries

    def getStates(self, spaceLayerID, current=None):
        return(list(nx.get_node_attributes(self.model.spaceLayers[spaceLayerID], 'obj').values()))

    def getTransitions(self, spaceLayerID, current=None):
        return(list(data['obj'] for node1, node2,
                    data in self.model.spaceLayers[spaceLayerID].edges(data=True)))

    def getUsage(self, referenceCellID, current=None):
        referenceCellSpace = self.model.getCellreference(referenceCellID)
        return referenceCellSpace.usage

    def getName(self, referenceCellID, current=None):
        referenceCellSpace = self.model.getCellreference(referenceCellID)
        return referenceCellSpace.name

    def getHeight(self, referenceCellID, current=None):
        referenceCellSpace = self.model.getCellreference(referenceCellID)
        surfaces = referenceCellSpace.geometry.surfaces

        z_base_coord = surfaces[len(surfaces) - 1].linearRing[0].z
        z_roof_coord = surfaces[0].linearRing[0].z

        return z_roof_coord - z_base_coord
    
    def getBoundary(self, boundary_id, current=None):
        boundaries = self.model.cellSpaceBoundaries.values()

        for boundary in boundaries:
            if boundary.id == boundary_id:
                return boundary
        return None

    def getExits(self, referenceCellID, current=None):
        exits = []
        referenceCellSpace = self.model.getCellreference(referenceCellID)
        for cellSpaceBoundary in referenceCellSpace.cellSpaceBoundaries:
            if(self.model.cellSpaceBoundaries[cellSpaceBoundary].usage == 'Door'):
                exits.append(cellSpaceBoundary)

        return exits

    def getEntrances(self, spaceLayerID, current=None):
        entrances = []
        for cellSpace_id, cellSpace in self.model.CellSpaces.items():
            if(cellSpace.usage == 'Entrance' and self.model.getLayerOfaCell(cellSpace_id) == spaceLayerID):
                entrances.append(cellSpace_id)
        return entrances

    def getSpaceLayersID(self, current=None):
        return self.model.get_SpaceLayers_id()

    def getCellofPosition(self, spaceLayerID, position, current=None):
        return self.model.findCellIDofPointInKDTree(spaceLayerID, position)

    def isPositionInCell(self, position, cell, current=None):
        z_coord_of_position_ground = self.model.calculateGroundOfPosition(
            position.z)
        point = [position.x, position.y, z_coord_of_position_ground]
        for value in self.model.shapePoligons.values():
            if(value[0] == cell):
                return(value[1].contains(Point(point)))

    def getPathCellToCell(self, spaceLayerID, CellIDfrom, CellIDto, current=None):
        cellSpaceFrom = self.model.getCellreference(CellIDfrom).duality
        cellSpaceTo = self.model.getCellreference(CellIDto).duality

        nodes = nx.dijkstra_path(
            self.model.spaceLayers[spaceLayerID], cellSpaceFrom, cellSpaceTo)

        result = []
        for n in nodes:
            result.append(
                self.model.spaceLayers[spaceLayerID].nodes[n]['obj'].duality)

        return result

    def getPathPositionToPosition(self, spaceLayerID, positionFrom, positionTo, current=None):
        cellIDfrom = self.getCellofPosition(spaceLayerID, positionFrom)
        cellIDTo = self.getCellofPosition(spaceLayerID, positionTo)
        return self.getPathCellToCell(spaceLayerID, cellIDfrom, cellIDTo)


class Server(Ice.Application):
    def __init__(self):
        self.model = IndoorGMLreader(sys.argv[1])

    def run(self, argv):
        broker = self.communicator()
        servant = IgmlLayerI(self.model)

        adapter = broker.createObjectAdapter("IgmlLayerAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("IgmlLayer1"))

        print(proxy)
        sys.stdout.flush()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))
