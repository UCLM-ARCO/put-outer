#!/usr/bin/python3
# -*- coding: utf-8; mode: python -*-

import sys

import re
import Ice
from commodity import path

Ice.loadSlice(
    '-I /usr/share/slice /usr/share/slice/dharma/scone-wrapper.ice --all')
from Semantic import SconeServicePrx
Ice.loadSlice(path.get_project_dir('.') + '/UrbanService.ice')
from UrbanService import position3D, IgmlLayerPrx


class Lighter(Ice.Application):
    def run(self, argv):
        self.IgmlLayer = self.get_service(argv[1], IgmlLayerPrx)
        self.scone = self.get_service(argv[2], SconeServicePrx)

        self.target_location = position3D(float(argv[3]),
                                          float(argv[4]),
                                          float(argv[5]))

        self.target_cell = self.IgmlLayer.getCellofPosition('topology', self.target_location)

        print('The target point to illuminate is: {}\n'.format(self.target_location,))
        print('And that point is located in {}\n'.format(self.target_cell))

        cells_to_check = [self.target_cell] + self.get_adjacent_cells(self.target_cell)

        print('Cells to check:\n{}'.format(cells_to_check))
        print("------------------------------\n")
        print('Looking for valid lamps in %s and adjacents...\n' % self.target_cell)

        valid_lamps = self.get_valid_lamps(cells_to_check)

        print("Valid lamps:\n%s\n" % valid_lamps)

    def get_valid_lamps(self, cells):
        valid_lamps = []

        for cell in cells:
            lamps = self.get_cell_lamps(cell)
            print("Lamps in %s:" % cell)

            for lamp in lamps:
                if not self.valid_lamp(lamp):
                    print("\t- %s is not a valid lamp" % lamp)
                    print("\t  (target not in range or inoperative lamp)")
                    break

                navigable_boundaries = self.navigables_between_cells(cell, self.target_cell)

                if not navigable_boundaries:
                    print("\t- %s is not a valid lamp" % lamp)
                    print("\t  (no navigables between %s and %s)" % (cell, self.target_cell))
                    break
                
                if not self.navigables_in_range(navigable_boundaries, lamp):
                    print("\t- %s is not a valid lamp" % lamp)
                    print("\t  (no navigables in the lamp range)")
                    break

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

        adjacency_boundaries = self.adjacency_boundaries(cell_1, cell_2)
        navigable_boundaries = []

        for boundary in adjacency_boundaries:
            request = "(statement-true? {%s} {is navigable by} {light})" % boundary
            scone_reply = self.scone.request(request)

            if scone_reply.lower() == 't':
                navigable_boundaries.append(boundary)

        return navigable_boundaries
    
    def navigables_in_range(self, navigables, lamp):
        valid_navigables = []

        if navigables[0] == "space":
            return True
        # HEREEEEEEEEEEEE
        # for navigable in navigables:
        #     navigable_centroid = self.boundary_centroid(navigable)
        #     if self.isPointInLampRange(lamp, navigable_centroid):
        #         valid_navigables.append(navigable)

        return True if valid_navigables else False
    
    # def boundary_centroid(self, boundary):
    #     geometry = self.scone.request("(list-all-x-of-y {geometric part} " +
    #                                         "{%s})" % boundary)[2:-2]
    #     scone_response = self.scone.request("(list-rel-inverse {is an " +
    #                                         "ordered element of} {%s})" %
    #                                         geometry)
    #     boundary_points = re.findall(r'{(.*?)}', scone_response)
    #     point_1, point_2 = self.getTwoPointsWithSameCoordinate(boundary_points,
    #                                                            'z')
    #     point_1_x = self.scone.request("(the-x-of-y {x-coordinate} {%s})" %
    #                                    point_1)[1:-1]
    #     point_1_y = self.scone.request("(the-x-of-y {y-coordinate} {%s})" %
    #                                    point_1)[1:-1]
    #     point_2_x = self.scone.request("(the-x-of-y {x-coordinate} {%s})" %
    #                                    point_2)[1:-1]
    #     point_2_y = self.scone.request("(the-x-of-y {y-coordinate} {%s})" %
    #                                    point_2)[1:-1]
    #     centroid_x = (float(point_1_x) + float(point_2_x)) / 2
    #     centroid_y = (float(point_1_y) + float(point_2_y)) / 2

    #     return UrbanService.position3D(centroid_x, centroid_y, float(0))
    
    def adjacency_boundaries(self, cell_1, cell_2):
        relations = self.relations_between_cells(cell_1, cell_2, "is adjacent to")
        boundaries = []
        
        for relation in relations:
            # In the Scone parser two relations for the same are parsed:
            # R1 is adjacent to R2 and viceversa. It's necessary to know
            # if already exists that relation in any direction. Two next
            # lines will be innecesary when this problem has been fixed.
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
        if self.is_point_in_range(lamp) and self.can_be_turned_on(lamp):
            return True
        return False
    
    def is_point_in_range(self, lamp):
        request = "(the-x-of-y {action range} {%s})" % lamp
        scone_reply = self.scone.request(request)
        lamp_range = scone_reply[1:-1]
        return self.IgmlLayer.isPositionInCell(self.target_location, lamp_range)

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