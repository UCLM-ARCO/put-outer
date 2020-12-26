#!/usr/bin/python3
# -*- coding: utf-8; mode: python -*-

import sys

import re
import Ice

from commodity import path

Ice.loadSlice(path.get_project_dir('.') + '/UrbanService.ice')
import UrbanService

boundary_types = ['virtual boundary', 'door', 'window', 'wall']
cell_types = ['space', 'room', 'stairs', 'elevator']


class Parser(Ice.Application):
    def run(self, argv):
        self.ic = self.communicator()
        proxy = self.ic.stringToProxy(argv[1])

        self.igml_model = UrbanService.IgmlLayerPrx.checkedCast(proxy)

        if not self.igml_model:
            raise RuntimeError('Invalid igml_model proxy')

        with open('model.lisp', 'w') as self.file:
            self.parse_topology()
            self.parse_lamps()
        
    def parse_topology(self):
        self.parse_boundaries()
        self.parse_cells()
        self.parse_nrg()

    def parse_lamps(self):
        lamps = self.igml_model.getStates('lights')

        for lamp in lamps:
            self.new_indv(lamp.id, 'lamp')
            self.new_indv(lamp.duality, 'action range')
            self.x_is_a_y_of_z(lamp.duality, 'action range', lamp.id)
    
    def parse_boundaries(self):
        boundaries = self.igml_model.getCellSpaceBoundaries('topology')

        for boundary in boundaries:
            entity_type = 'boundary'

            if boundary.usage.lower() in boundary_types:
                entity_type = boundary.usage.lower()
            
            self.new_indv(boundary.id, entity_type)

            if boundary.material:
                material_element = '%s element' % boundary.material.lower()
                self.new_is_a(boundary.id, material_element)
    
    def parse_cells(self):
        def parse_adjacency(cell):
            adj_cells_ids = self.igml_model.getAdjacentCells(cell.id)

            # FIXME: two statements for every adjacency relation.
            # R1 is adjacent to R2 and viceversa. It's necessary to know if
            # already exists a relation in any direction
            for adj_cell_id in adj_cells_ids:
                boundary_ids = self.igml_model.getCellSpaceBoundariesBetweenCells(adj_cell_id, cell.id)

                for boundary_id in boundary_ids:
                    self.new_statement(cell.id, 'is adjacent to', adj_cell_id, boundary_id)

        cells = self.igml_model.getCells('topology')

        for cell in cells:
            entity_type = 'cell'
            usage = None

            if cell.usage.lower() in cell_types:
                entity_type = cell.usage.lower()
            else:
                usage = cell.usage.lower()
            
            self.new_indv(cell.id, entity_type)

            if usage:
                self.x_is_a_y_of_z(usage, 'room usage', cell.id)

        for cell in cells:
            parse_adjacency(cell)
    
    def parse_nrg(self):
        def find_dual_entity(dual_entity, entities):
            for entity in entities:
                if entity.id == dual_entity:
                    return entity.duality

        transitions = self.igml_model.getTransitions('topology')
        states = self.igml_model.getStates('topology')

        for t in transitions:
            cell_from = find_dual_entity(t.connectsFrom, states)
            cell_to = find_dual_entity(t.connectsTo, states)

            self.new_statement(cell_from, "is connected to", cell_to, t.duality)
    
    def new_indv(self, id, entity_type):
        self.file.write('(new-indv {%s} {%s})\n' % (id, entity_type))
    
    def new_is_a(self, id, entity_type):
        self.file.write('(new-is-a {%s} {%s})\n' % (id, entity_type))

    def x_is_a_y_of_z(self, x, y, z):
        self.file.write('(x-is-a-y-of-z {%s} {%s} {%s})\n' % (x, y, z))
    
    def new_statement(self, a, relation, b, c):
        statement = ('(new-statement {%s} {%s} {%s}' % (a, relation, b))
        statement += (' :c {%s})\n' % c) if c else (')\n')
        self.file.write(statement)


sys.exit(Parser().main(sys.argv))