#!/usr/bin/python3
# -*- coding: utf-8; mode: python -*-

import sys

import re
import Ice
from commodity import path

Ice.loadSlice(
    '-I /usr/share/slice /usr/share/slice/dharma/scone-wrapper.ice --all')
from Semantic import SconeServicePrx
Ice.loadSlice(path.get_project_dir('.') + '/model-service/UrbanService.ice')
from UrbanService import position3D, IgmlLayerPrx


class Lighter(Ice.Application):
    def run(self, argv):
        self.IgmlLayer = self.get_service(argv[1], IgmlLayerPrx)
        self.scone = self.get_service(argv[2], SconeServicePrx)

        self.target_location = position3D(float(argv[3]),
                                          float(argv[4]),
                                          float(argv[5]))

        self.target_cell = self.IgmlLayer.getCellofPosition('topology', self.target_location)
        cells_to_check = [self.target_cell] + self.get_adjacent_cells(self.target_cell)
        valid_lamps = self.get_valid_lamps(cells_to_check)

        print("Valid lamps:\n%s" % valid_lamps)

    def get_valid_lamps(self, cells):
        valid_lamps = []

        for cell in cells:
            lamps = self.get_cell_lamps(cell)

            for lamp in lamps:
                if not self.valid_lamp(lamp):
                    continue

                navigable_ids = self.navigables_between_cells(cell, self.target_cell)

                if not navigable_ids or not self.navigables_in_range(navigable_ids, lamp):
                    continue

                valid_lamps.append(lamp)

        return valid_lamps

    def get_cell_lamps(self, cell):
        request = "(list-all-x-inverse-of-y {logical location} {%s})" % cell
        scone_reply = self.scone.request(request)

        if scone_reply.lower() == "nil":
            print("There's no lamps in {}".format(cell))
            return []

        return self.parse_entity_list(scone_reply)
    
    def get_adjacent_cells(self, cell):
        request = '(list-rel {is adjacent to} {%s})' % cell
        scone_reply = self.scone.request(request)

        if scone_reply.lower() == "nil":
            print("There's no adjacent cells to {}".format(cell))
            return []

        return self.parse_entity_list(scone_reply)

    def navigables_between_cells(self, cell_1, cell_2):
        if cell_1 == cell_2:
            return ["space"]

        navigable_boundaries = []
        adjacency_boundaries = self.adjacency_boundaries(cell_1, cell_2)

        for boundary in adjacency_boundaries:
            request = "(statement-true? {%s} {is navigable by} {light})" % boundary
            scone_reply = self.scone.request(request)

            if scone_reply.lower() == 't':
                navigable_boundaries.append(boundary)

        return navigable_boundaries
    
    def navigables_in_range(self, navigable_ids, lamp):
        def surface_centroid(surface):
            point_1 = surface.linearRing[0]

            for i in range(1, len(surface.linearRing)):
                point_2 = surface.linearRing[i]

                if point_1.z == point_2.z:
                    break
            
            centroid_x = (float(point_1.x) + float(point_2.x)) / 2
            centroid_y = (float(point_1.y) + float(point_2.y)) / 2

            return position3D(centroid_x, centroid_y, float(0))

        if navigable_ids[0] == "space":
            return True

        for navigable_id in navigable_ids:
            navigable = self.IgmlLayer.getBoundary(navigable_id)

            for surface in navigable.geometry.surfaces:
                if self.is_point_in_range(lamp, surface_centroid(surface)):
                    return True

        return False
    
    def adjacency_boundaries(self, cell_1, cell_2):
        relations = self.relations_between_cells(cell_1, cell_2, "is adjacent to")
        relations += self.relations_between_cells(cell_1, cell_2, "is connected to")
        boundaries = []
        
        for relation in relations:
            # FIXME: In the parser, two statements to represent the same
            # relation are parsed: R1 is adjacent to R2 and viceversa.
            # It's necessary to consider if already exists a relation of
            # this type in any direction or parse this as a symmetric
            # relation.
            element = self.get_rel_element('c', relation)

            if element not in boundaries:
                boundaries.append(element)

        return boundaries

    def relations_between_cells(self, cell_1, cell_2, relation_type):
        cells = [cell_1, cell_2]
        relations = []

        for i, cell in enumerate(cells):
            cell_relations = self.entity_relation_instances(cell, relation_type)

            for relation, entity_related in cell_relations.items():
                if entity_related == cells[i-1] and relation not in relations:
                    relations.append(relation)

        return relations

    def entity_relation_instances(self, entity, relation_type):
        element_types = ['a', 'b']
        relations = {}

        for i, element_type in enumerate(element_types):
            request = "(incoming-%s-wires (lookup-element {%s}))" % (element_type, entity)
            scone_reply = self.scone.request(request)
            entity_relations = self.parse_entity_list(scone_reply)

            for relation in entity_relations:
                if relation_type in relation:
                    element = self.get_rel_element(element_types[i-1], relation)
                    relations[relation] = element

        return relations

    def get_rel_element(self, link_element, relation):
        request = '(%s-element {%s})' % (link_element, relation)
        scone_reply = self.scone.request(request)

        return self.parse_entity_list(scone_reply)[0]

    def valid_lamp(self, lamp):
        if self.is_point_in_range(lamp, self.target_location) and self.can_be_turned_on(lamp):
            return True
        return False 
    
    def is_point_in_range(self, lamp, point):
        request = "(the-x-of-y {action range} {%s})" % lamp
        scone_reply = self.scone.request(request)
        lamp_range = scone_reply[1:-1]
        return self.IgmlLayer.isPositionInCell(point, lamp_range)

    def can_be_turned_on(self, lamp):
        request = "(is-x-a-y? {%s} {inoperative})" % lamp
        scone_reply = self.scone.request(request)
        return False if scone_reply.lower() == "yes" else True

    def parse_entity_list(self, scone_reply):
        entity_list = re.findall(r'{(.*?)}', scone_reply)
        return entity_list if scone_reply.lower() != 'nil' else []

    def get_service(self, proxy_string, proxy_object_type):
        proxy = self.communicator().stringToProxy(proxy_string)
        proxy_object = proxy_object_type.checkedCast(proxy)

        if not proxy_object:
            raise RuntimeError('Invalid proxy: "{}"'.format(proxy_string))

        return proxy_object


sys.exit(Lighter().main(sys.argv))
