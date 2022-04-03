import AStar as pathfinding
import utilityFunctions as uf
from pymclevel import BoundingBox
from random import *
from numpy import *
from operator import itemgetter
from AHouse_v5 import house_perform as house_perform
import numpy as np
from itertools import cycle


class Generator:
    # Initializing
    def __init__(self, level, box, options, heightMap):
        self.level = level
        self.box = box
        self.options = options
        self.heightMap = heightMap
        self.entry_distance = 3
        self.center_x = (box.minx + box.maxx) / 2
        self.center_y = (box.miny + box.maxy) / 2
        self.center_z = (box.minz + box.maxz) / 2
        self.surface_blocks = [2, 3]
        self.doors = [64, 71, 193, 194, 195, 196, 197, 324, 330, 427, 428, 429, 430, 431]
        self.front_doors = [(44, 0), (44, 1), (44, 2), (44, 3), (44, 4), (44, 5), (44, 6), (44, 7), (126, 0), (126, 1), (126, 2), (126, 3), (126, 4), (126, 5)]
        self.houseBBList = []
        self.connected_doors = []
        self.all_door_locations = []
        self.candidates = []
        self.all_start_positions = []
        self.max_candidate_attempts = 5000 	# Number of positions considered when placing each structure (higher value results in better layouts at the cost of slower generation)

        self.district_locations = ['NW', 'NE', 'SW', 'SE']
        self.district_type = ['BRICK', 'CLAY', 'WOOD', 'WOOL']
        self.districts = []
        self.assign_districts()

        self.ADRIAN_MATERIALS = [(35, 0), (35, 8), (172, 0), (45, 0), (82, 0), (43, 9), (5, 2), (5, 1), (5, 5), (5, 3),
                                 (17, 12), (17, 13), (17, 15), (162, 12), (162, 13), (160, 8), (160, 0), (160, 7),
                                 (95, 8), (95, 0), (5, 0), (5, 2), (193, 1), (193, 3), (1, 0), (1, 1), (1, 2), (1, 3),
                                 (1, 4), (1, 5), (1, 6), (80, 0), (95, 3), (22, 0), (24, 2), (19, 0), (18, 0), (3, 0),
                                 (1, 0), (125, 0), (125, 2), (125, 5), (53, 0), (134, 0), (135, 0), (126, 0), (126, 1),
                                 (126, 2), (44, 10), (126, 8), (126, 9), (126, 10), (126, 13), (17, 12), (17, 13),
                                 (17, 14), (17, 15), (162, 12), (162, 13), (171, 0), (171, 1), (171, 2), (171, 3),
                                 (171, 4), (171, 5), (171, 6), (171, 7), (171, 8), (171, 9), (171, 10), (171, 11),
                                 (171, 12), (171, 13), (171, 14), (171, 15), (89, 0), (44, 5), (145, 2), (98, 3),
                                 (98, 0), (4, 0), (85, 0), (95, 0), (35, 0), (63, 0), (1, 0)]

        # MAT_WALL_BEAM = [(5, 5), (5, 3), (17, 12), (17, 13), (17, 15), (162, 12), (162, 13)]
        # MAT_WINDOW = [(160, 8), (160, 0), (160, 7), (95, 8), (95, 0)]
        # MAT_FLOOR = [(5, 0), (5, 2), (5, 3)]
        # MAT_DOOR = [(193, 1), (193, 3)]
        # MAT_ROOF = [(125, 0), (125, 2), (125, 5)]
        # MAT_DOOR_PORCH = [(126, 0), (126, 1), (126, 2)]
        # MAT_WINDOW_PORCH = [(44, 10), (126, 8), (126, 9), (126, 10), (126, 13)]
        # MAT_STAIRS = [(53, 0), (134, 0), (135, 0)]  # (67,0), (108,0), (109, 0), (114,0), (128,0), (164,0)

        self.MAT_EXT_WOOD = [(5, 0), (5, 1), (5, 5)]
        self.MAT_EXT_BEAM_WOOD = [(17, 0), (17, 1), (162, 1)]
        self.MAT_EXT_WINDOW_WOOD = [(20, 0), (95, 0)]
        self.MAT_EXT_DOOR_WOOD = [(64, 0), (193, 0), (197, 0)]
        self.MAT_EXT_ROOF_WOOD = [(5, 0), (5, 1), (5, 5)]
        self.MAT_DOOR_PORCH_WOOD = [(126, 0), (126, 1), (126, 5)]
        self.MAT_WINDOW_PORCH_WOOD = [(126, 0), (126, 1), (126, 5)]
        self.MAT_STAIRS_WOOD = [(53, 0), (134, 0), (164, 0)]
        self.MAT_FLOOR_WOOD = [(5, 0), (5, 1), (5, 5)]
        self.MAT_FENCE_POST_WOOD = [(85, 0), (188, 0), (191, 0)]

        self.MAT_EXT_CLAY = [(82, 0)]
        self.MAT_EXT_BEAM_CLAY = [(172, 0), (159, 3), (159, 9)]
        self.MAT_EXT_WINDOW_CLAY = [(95, 0), (20, 0)]
        self.MAT_EXT_DOOR_CLAY = [(195, 0), (196, 0)]
        self.MAT_EXT_ROOF_CLAY = [(159, 0), (159, 1), (159, 8)]
        self.MAT_DOOR_PORCH_CLAY = [(126, 3), (126, 4)]
        self.MAT_WINDOW_PORCH_CLAY = [(126, 3), (126, 4)]
        self.MAT_STAIRS_CLAY = [(136, 0), (163, 0)]
        self.MAT_FLOOR_CLAY = [(5, 3), (5, 4)]
        self.MAT_FENCE_POST_CLAY = [(190, 0), (192, 0)]

        self.MAT_EXT_BRICK = [(45, 0)]
        self.MAT_EXT_BEAM_BRICK = [(45, 0)]
        self.MAT_EXT_WINDOW_BRICK = [(20, 0), (95, 0)]
        self.MAT_EXT_DOOR_BRICK = [(64, 0), (197, 0)]
        self.MAT_EXT_ROOF_BRICK = [(43, 5), (4, 0)]
        self.MAT_DOOR_PORCH_BRICK = [(44, 3), (44, 4), (44, 5)]
        self.MAT_WINDOW_PORCH_BRICK = [(44, 3), (44, 4), (44, 5)]
        self.MAT_STAIRS_BRICK = [(108, 0), (109, 0), (67, 0)]
        self.MAT_FLOOR_BRICK = [(5, 0), (5, 1), (5, 5)]
        self.MAT_FENCE_POST_BRICK = [(85, 0), (188, 0), (191, 0)]

        self.MAT_EXT_WOOL = [(35, 0), (35, 8)]
        self.MAT_EXT_BEAM_WOOL = [(35, 15), (155, 0)]
        self.MAT_EXT_WINDOW_WOOL = [(20, 0), (95, 0)]
        self.MAT_EXT_DOOR_WOOL = [(64, 0), (193, 0), (197, 0)]
        self.MAT_EXT_ROOF_WOOL = [(35, 15), (155, 0)]
        self.MAT_DOOR_PORCH_WOOL = [(44, 0), (44, 7)]
        self.MAT_WINDOW_PORCH_WOOL = [(44, 0), (44, 7)]
        self.MAT_STAIRS_WOOL = [(156, 0)]
        self.MAT_FLOOR_WOOL = [(5, 0), (5, 1), (5, 5)]
        self.MAT_FENCE_POST_WOOL = [(85, 0), (188, 0), (191, 0)]

    def assign_districts(self):
        while len(self.district_locations) > 0 and len(self.district_type) > 0:
            random_district_location = choice(self.district_locations)
            random_district_type = choice(self.district_type)
            self.district_locations.remove(random_district_location)
            self.district_type.remove(random_district_type)
            self.districts.append((random_district_location, random_district_type))

    def collides_road(self, x1, y1, x2, y2):
        collider_blocks = {98}
        return self.heightMap.collides(x1, y1, x2, y2, collider_blocks)

    def collides(self, x1, y1, x2, y2):
        # collider_blocks = {(8, (9, 0), (10, 0), (11, 0), (79, 0), (35, 0), (35, 8), (172, 0), (45, 0), (82, 0), (43, 9),
        #                     (5, 2), (5, 1), (5, 5), (5, 3), (17, 12), (17, 13), (17, 15), (162, 12), (162, 13),
        #                     (160, 8), (160, 0), (160, 7), (95, 8), (95, 0), (5, 0), (5, 2), (193, 1), (193, 3), (1, 0),
        #                     (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (80, 0),
        #                     (95, 3), (22, 0), (24, 2), (19, 0), (18, 0), (3, 0), (1, 0), (125, 0), (125, 2), (125, 5),
        #                     (53, 0), (134, 0), (135, 0), (126, 0), (126, 1), (126, 2),
        #                     (44, 10), (126, 8), (126, 9), (126, 10), (126, 13), (17, 12), (17, 13), (17, 14), (17, 15),
        #                     (162, 12), (162, 13), (171, 0), (171, 1), (171, 2), (171, 3), (171, 4), (171, 5), (171, 6),
        #                     (171, 7),
        #                     (171, 8), (171, 9), (171, 10), (171, 11), (171, 12), (171, 13), (171, 14), (171, 15),
        #                     (89, 0), (44, 5), (145, 2), (98, 3), (98, 0), (4, 0), (85, 0), (95, 0), (35, 0), (63, 0),
        #                     (1, 0)}

        collider_blocks = {8, 9, 10, 11, 79, 3, 35, 172, 45, 82, 43, 5, 17, 162, 160, 95, 193, 1, 80, 95, 22, 24, 19, 18, 3, 125, 53, 134, 135, 126, 44, 17, 171, 89, 145, 98, 4, 85, 95, 35, 63, 98}
        return self.heightMap.collides(x1, y1, x2, y2, collider_blocks)

    def collides_structures(self, x1, y1, x2, y2):
        for structure in self.houseBBList:
            structure_x1, structure_y1, structure_x2, structure_y2 = structure[1]
            if self.heightMap.box_collision(x1, y1, x2, y2, structure_x1, structure_y1, structure_x2, structure_y2):
                return True
        return False

    def fits_inside(self, x1, y1, x2, y2):
        if self.heightMap.fits_inside(x1 - 3, y1 - 3, x2 + 3, y2 + 3):
            if self.heightMap.fits_inside(x1, y1, x2, y2):
                return True
        return False

    def get_distance_data(self, x1, z1, x2, z2):
        difference_x = abs(x1 - x2)
        difference_z = abs(z1 - z2)

        return difference_x + difference_z

    def acceptable(self, x1, y1, x2, y2):
        reserved_space = 4
        outer_x1 = max(0, x1 - reserved_space)
        outer_y1 = max(0, y1 - reserved_space)
        outer_x2 = min(self.heightMap.w, x2 + reserved_space)
        outer_y2 = min(self.heightMap.h, y2 + reserved_space)

        return self.heightMap.fits_inside(x1, y1, x2, y2) \
               and not self.collides_structures(outer_x1, outer_y1, outer_x2, outer_y2) \
               and not self.collides(outer_x1, outer_y1, outer_x2, outer_y2) \
               and not self.collides_road(max(0, x1 - 1), max(0, y1 - 1), min(self.heightMap.w, x2 + 1), min(self.heightMap.h, y2 + 1))

    def generate_buildings(self):
        counter = 0
        while True:
            self.candidates = []

            if len(self.houseBBList) > 0:
                random_structure = choice(self.houseBBList)
                random_structure_x1, random_structure_y1, _, _ = random_structure[1]
                start_x, start_y = random_structure_x1, random_structure_y1
            else:
                start_x, start_y = self.heightMap.w / 2, self.heightMap.h / 2

            sorted_positions = sorted(self.heightMap.positions, key=lambda position: self.heightMap.get_distance(position[0], position[1], start_x, start_y))

            full_width = self.heightMap.w
            full_height = self.heightMap.h
            half_width = full_width / 2
            half_height = full_height / 2
            third_half_width = half_width / 3
            third_half_height = half_height / 3

            distance_data = None
            for x, y in sorted_positions:
                # FROM CENTRE TO INNER THIRD OF A HALF
                INNER_X = half_width - third_half_width < x < half_width + third_half_width
                INNER_Y = half_height - third_half_height < y < half_height + third_half_height

                # FROM INNER THIRD OF A HALF TO MIDDLE THIRD OF A HALF
                MIDDLE_X = half_width - (third_half_width * 2) < x < half_width + (third_half_width * 2)
                MIDDLE_Y = half_height - (third_half_height * 2) < y < half_height + (third_half_height * 2)

                # FROM MIDDLE THIRD OF A HALF TO OUTER THIRD OF A HALF
                OUTER_X = x < full_width
                OUTER_Y = y < full_height

                # INNER SQUARE
                if INNER_X and INNER_Y:
                    random_structure_value = randint(35, 40)
                # MIDDLE SQUARE
                elif MIDDLE_X and MIDDLE_Y:
                    random_structure_value = randint(25, 30)
                # OUTER SQUARE
                elif OUTER_X and OUTER_Y:
                    random_structure_value = randint(15, 20)
                else:
                    continue

                siteOptions = {'Operation': 'House', 'Seed:': randint(0, 99999999999)}

                width = random_structure_value
                height = random_structure_value
                length = random_structure_value

                if self.acceptable(x, y, x + width, y + length):
                    if len(self.houseBBList) > 0:

                        for candidate in self.candidates:
                            distance = self.get_distance_data(x, y, candidate[0], candidate[1])

                            if distance_data is None:
                                distance_data = distance
                            elif distance < distance_data:
                                distance_data = distance

                        self.candidates.append([x, y, x + width, y + length, width, height, length, siteOptions, distance_data])
                    else:
                        self.candidates.append([x, y, x + width, y + length, width, height, length, siteOptions, distance_data])
                    #self.candidates.append([x, y, x + width, y + length, width, height, length, siteOptions, 0])

                if len(self.candidates) >= self.max_candidate_attempts:
                    break

            if self.candidates:
                print("   Generating house: " + str(len(self.houseBBList) + 1))
                print("     Found %i candidates..." % len(self.candidates))
                shuffle(self.candidates)

                self.candidates = sorted(self.candidates, key=itemgetter(-1), reverse=True)
                top_candidate = self.candidates[0]
                print("     Top candidate: ", top_candidate)
                x1, y1, x2, y2, width, height, length, siteOptions, _ = top_candidate

                box_location_x = x1 + self.box.minx
                box_location_z = y1 + self.box.minz
                self.generate_building(width, height, length, siteOptions, box_location_x, box_location_z, x1, y1, x2, y2)
                self.connect_building(self.houseBBList[-1][0], width, length, box_location_x, box_location_z)
            else:
                counter += 1
                if counter > 50:
                    print("No more suitable areas to generate buildings found.")
                    break

    def generate_building(self, width, height, length, siteOptions, starting_x, starting_z, x1, y1, x2, y2):
        self.heightMap.fill(x1, y1, 3, x2, y2, 3 + 1, (3, 0))
        newBox = BoundingBox((starting_x, 3, starting_z), (width, height, length))
        self.houseBBList.append((newBox, (x1, y1, x2, y2)))

        if self.box.minx < starting_x < self.center_x and self.box.minz < starting_z < self.center_z:
            # NORTH WEST
            NW_tuple = [tup for tup in self.districts if tup[0] == 'NW'][0]
            NW_tuple_type = NW_tuple[1]

            if NW_tuple_type == 'CLAY':
                house_perform(self.level, newBox, siteOptions,
                              self.MAT_EXT_CLAY, self.MAT_EXT_BEAM_CLAY, self.MAT_EXT_WINDOW_CLAY, self.MAT_EXT_DOOR_CLAY,
                              self.MAT_EXT_ROOF_CLAY, self.MAT_DOOR_PORCH_CLAY, self.MAT_WINDOW_PORCH_CLAY, self.MAT_STAIRS_CLAY,
                              self.MAT_FLOOR_CLAY, self.MAT_FENCE_POST_CLAY)
            elif NW_tuple_type == 'WOOD':
                house_perform(self.level, newBox, siteOptions,
                              self.MAT_EXT_WOOD, self.MAT_EXT_BEAM_WOOD, self.MAT_EXT_WINDOW_WOOD, self.MAT_EXT_DOOR_WOOD,
                              self.MAT_EXT_ROOF_WOOD, self.MAT_DOOR_PORCH_WOOD, self.MAT_WINDOW_PORCH_WOOD, self.MAT_STAIRS_WOOD,
                              self.MAT_FLOOR_WOOD, self.MAT_FENCE_POST_WOOD)
            elif NW_tuple_type == 'BRICK':
                house_perform(self.level, newBox, siteOptions,
                              self.MAT_EXT_BRICK, self.MAT_EXT_BEAM_BRICK, self.MAT_EXT_WINDOW_BRICK, self.MAT_EXT_DOOR_BRICK,
                              self.MAT_EXT_ROOF_BRICK, self.MAT_DOOR_PORCH_BRICK, self.MAT_WINDOW_PORCH_BRICK, self.MAT_STAIRS_BRICK,
                              self.MAT_FLOOR_BRICK, self.MAT_FENCE_POST_BRICK)
            elif NW_tuple_type == 'WOOL':
                house_perform(self.level, newBox, siteOptions,
                              self.MAT_EXT_WOOL, self.MAT_EXT_BEAM_WOOL, self.MAT_EXT_WINDOW_WOOL, self.MAT_EXT_DOOR_WOOL,
                              self.MAT_EXT_ROOF_WOOL, self.MAT_DOOR_PORCH_WOOL, self.MAT_WINDOW_PORCH_WOOL,
                              self.MAT_STAIRS_WOOL, self.MAT_FLOOR_WOOL, self.MAT_FENCE_POST_WOOL)

        elif self.center_x < starting_x < self.box.maxx and self.center_z < starting_z < self.box.maxz:
            # NORTH EAST
            NE_tuple = [tup for tup in self.districts if tup[0] == 'NE'][0]
            NE_tuple_type = NE_tuple[1]

            if NE_tuple_type == 'CLAY':
                house_perform(self.level, newBox, siteOptions,
                              self.MAT_EXT_CLAY, self.MAT_EXT_BEAM_CLAY, self.MAT_EXT_WINDOW_CLAY,
                              self.MAT_EXT_DOOR_CLAY,
                              self.MAT_EXT_ROOF_CLAY, self.MAT_DOOR_PORCH_CLAY, self.MAT_WINDOW_PORCH_CLAY,
                              self.MAT_STAIRS_CLAY,
                              self.MAT_FLOOR_CLAY, self.MAT_FENCE_POST_CLAY)
            elif NE_tuple_type == 'WOOD':
                house_perform(self.level, newBox, siteOptions,
                              self.MAT_EXT_WOOD, self.MAT_EXT_BEAM_WOOD, self.MAT_EXT_WINDOW_WOOD,
                              self.MAT_EXT_DOOR_WOOD,
                              self.MAT_EXT_ROOF_WOOD, self.MAT_DOOR_PORCH_WOOD, self.MAT_WINDOW_PORCH_WOOD,
                              self.MAT_STAIRS_WOOD,
                              self.MAT_FLOOR_WOOD, self.MAT_FENCE_POST_WOOD)
            elif NE_tuple_type == 'BRICK':
                house_perform(self.level, newBox, siteOptions,
                              self.MAT_EXT_BRICK, self.MAT_EXT_BEAM_BRICK, self.MAT_EXT_WINDOW_BRICK,
                              self.MAT_EXT_DOOR_BRICK,
                              self.MAT_EXT_ROOF_BRICK, self.MAT_DOOR_PORCH_BRICK, self.MAT_WINDOW_PORCH_BRICK,
                              self.MAT_STAIRS_BRICK,
                              self.MAT_FLOOR_BRICK, self.MAT_FENCE_POST_BRICK)
            elif NE_tuple_type == 'WOOL':
                house_perform(self.level, newBox, siteOptions,
                              self.MAT_EXT_WOOL, self.MAT_EXT_BEAM_WOOL, self.MAT_EXT_WINDOW_WOOL,
                              self.MAT_EXT_DOOR_WOOL,
                              self.MAT_EXT_ROOF_WOOL, self.MAT_DOOR_PORCH_WOOL, self.MAT_WINDOW_PORCH_WOOL,
                              self.MAT_STAIRS_WOOL, self.MAT_FLOOR_WOOL, self.MAT_FENCE_POST_WOOL)

        elif self.box.minx < starting_x < self.center_x and self.center_z < starting_z < self.box.maxz:
            # SOUTH WEST
            SW_tuple = [tup for tup in self.districts if tup[0] == 'SW'][0]
            SW_tuple_type = SW_tuple[1]

            if SW_tuple_type == 'CLAY':
                house_perform(self.level, newBox, siteOptions,
                              self.MAT_EXT_CLAY, self.MAT_EXT_BEAM_CLAY, self.MAT_EXT_WINDOW_CLAY,
                              self.MAT_EXT_DOOR_CLAY,
                              self.MAT_EXT_ROOF_CLAY, self.MAT_DOOR_PORCH_CLAY, self.MAT_WINDOW_PORCH_CLAY,
                              self.MAT_STAIRS_CLAY,
                              self.MAT_FLOOR_CLAY, self.MAT_FENCE_POST_CLAY)
            elif SW_tuple_type == 'WOOD':
                house_perform(self.level, newBox, siteOptions,
                              self.MAT_EXT_WOOD, self.MAT_EXT_BEAM_WOOD, self.MAT_EXT_WINDOW_WOOD,
                              self.MAT_EXT_DOOR_WOOD,
                              self.MAT_EXT_ROOF_WOOD, self.MAT_DOOR_PORCH_WOOD, self.MAT_WINDOW_PORCH_WOOD,
                              self.MAT_STAIRS_WOOD,
                              self.MAT_FLOOR_WOOD, self.MAT_FENCE_POST_WOOD)
            elif SW_tuple_type == 'BRICK':
                house_perform(self.level, newBox, siteOptions,
                              self.MAT_EXT_BRICK, self.MAT_EXT_BEAM_BRICK, self.MAT_EXT_WINDOW_BRICK,
                              self.MAT_EXT_DOOR_BRICK,
                              self.MAT_EXT_ROOF_BRICK, self.MAT_DOOR_PORCH_BRICK, self.MAT_WINDOW_PORCH_BRICK,
                              self.MAT_STAIRS_BRICK,
                              self.MAT_FLOOR_BRICK, self.MAT_FENCE_POST_BRICK)
            elif SW_tuple_type == 'WOOL':
                house_perform(self.level, newBox, siteOptions,
                              self.MAT_EXT_WOOL, self.MAT_EXT_BEAM_WOOL, self.MAT_EXT_WINDOW_WOOL,
                              self.MAT_EXT_DOOR_WOOL,
                              self.MAT_EXT_ROOF_WOOL, self.MAT_DOOR_PORCH_WOOL, self.MAT_WINDOW_PORCH_WOOL,
                              self.MAT_STAIRS_WOOL, self.MAT_FLOOR_WOOL, self.MAT_FENCE_POST_WOOL)

        elif self.center_x < starting_x < self.box.maxx and self.box.minz < starting_z < self.center_z:
            # SOUTH EAST
            SE_tuple = [tup for tup in self.districts if tup[0] == 'SE'][0]
            SE_tuple_type = SE_tuple[1]

            if SE_tuple_type == 'CLAY':
                house_perform(self.level, newBox, siteOptions,
                              self.MAT_EXT_CLAY, self.MAT_EXT_BEAM_CLAY, self.MAT_EXT_WINDOW_CLAY,
                              self.MAT_EXT_DOOR_CLAY,
                              self.MAT_EXT_ROOF_CLAY, self.MAT_DOOR_PORCH_CLAY, self.MAT_WINDOW_PORCH_CLAY,
                              self.MAT_STAIRS_CLAY,
                              self.MAT_FLOOR_CLAY, self.MAT_FENCE_POST_CLAY)
            elif SE_tuple_type == 'WOOD':
                house_perform(self.level, newBox, siteOptions,
                              self.MAT_EXT_WOOD, self.MAT_EXT_BEAM_WOOD, self.MAT_EXT_WINDOW_WOOD,
                              self.MAT_EXT_DOOR_WOOD,
                              self.MAT_EXT_ROOF_WOOD, self.MAT_DOOR_PORCH_WOOD, self.MAT_WINDOW_PORCH_WOOD,
                              self.MAT_STAIRS_WOOD,
                              self.MAT_FLOOR_WOOD, self.MAT_FENCE_POST_WOOD)
            elif SE_tuple_type == 'BRICK':
                house_perform(self.level, newBox, siteOptions,
                              self.MAT_EXT_BRICK, self.MAT_EXT_BEAM_BRICK, self.MAT_EXT_WINDOW_BRICK,
                              self.MAT_EXT_DOOR_BRICK,
                              self.MAT_EXT_ROOF_BRICK, self.MAT_DOOR_PORCH_BRICK, self.MAT_WINDOW_PORCH_BRICK,
                              self.MAT_STAIRS_BRICK,
                              self.MAT_FLOOR_BRICK, self.MAT_FENCE_POST_BRICK)
            elif SE_tuple_type == 'WOOL':
                house_perform(self.level, newBox, siteOptions,
                              self.MAT_EXT_WOOL, self.MAT_EXT_BEAM_WOOL, self.MAT_EXT_WINDOW_WOOL,
                              self.MAT_EXT_DOOR_WOOL,
                              self.MAT_EXT_ROOF_WOOL, self.MAT_DOOR_PORCH_WOOL, self.MAT_WINDOW_PORCH_WOOL,
                              self.MAT_STAIRS_WOOL, self.MAT_FLOOR_WOOL, self.MAT_FENCE_POST_WOOL)

    def connect_building(self, houseBB, width, length, box_location_x, box_location_z):
        door_locations = self.get_front_door_locations(houseBB)

        shortest_path_length = None
        existing_new_closest_door = None
        shortest_path_found = None

        self.heightMap.update_grid_for_structure(width, length, box_location_x, box_location_z, 1, self.entry_distance, door_locations)

        # If first two houses
        if len(self.houseBBList) == 2:
            for door_location in door_locations:
                for all_door_location in self.all_door_locations[:-1]:
                    for old_door_location in all_door_location:
                        shortest_path_length, shortest_path_found, existing_new_closest_door = \
                            self.find_best_paths(door_location, old_door_location, existing_new_closest_door, shortest_path_length, shortest_path_found)
        # If remaining houses
        elif len(self.houseBBList) > 2:
            for door_location in door_locations:
                for connected_door in self.connected_doors:
                    shortest_path_length, shortest_path_found, existing_new_closest_door = \
                        self.find_best_paths(door_location, connected_door, existing_new_closest_door, shortest_path_length, shortest_path_found)

        # Connecting house using the shortest path found between doors of the new house and doors of already placed houses
        if existing_new_closest_door is not None and shortest_path_found is not None:
            self.connected_doors.append(existing_new_closest_door)

            print("     Shortest path found: " + str(len(shortest_path_found)))

            for x, y in shortest_path_found:
                self.heightMap.fill_block_relative_to_surface(x, y, 0, (98, 0))

    def find_best_paths(self, door_location, connected_door, existing_new_closest_door, shortest_path_length, shortest_path_found):
        door_x1, door_z1, _, _, _ = door_location
        door_x2, door_z2, _, _, _ = connected_door

        entry_source = (door_x1 - self.box.minx, door_z1 - self.box.minz)
        entry_target = (door_x2 - self.box.minx, door_z2 - self.box.minz)

        pathfinder = pathfinding.astar(self.heightMap.grid, entry_target, entry_source, self.heightMap)

        if pathfinder:
            pathLength = len(pathfinder)

            if existing_new_closest_door is None and shortest_path_length is None and shortest_path_found is None:
                shortest_path_length = pathLength
                shortest_path_found = pathfinder
                existing_new_closest_door = door_location
            else:
                if pathLength < shortest_path_length and self.heightMap.fits_inside(door_x1 - self.box.minx, door_z1 - self.box.minz, door_x2 - self.box.minx, door_z2 - self.box.minz):
                    shortest_path_length = pathLength
                    shortest_path_found = pathfinder
                    existing_new_closest_door = door_location

        return shortest_path_length, shortest_path_found, existing_new_closest_door

    def get_front_door_locations(self, houseBB):
        door_locations = []

        for x in range(houseBB.minx, houseBB.maxx):
            for z in range(houseBB.minz, houseBB.maxz):
                if self.level.blockAt(x, 4, z) in self.doors:
                    for front_door in self.front_doors:
                        # NORTH
                        if self.level.blockAt(x, 3, z - 1) in front_door and self.level.blockAt(x, 4, z - 1) == 0 and self.level.blockAt(x, 5, z - 1) == 0 \
                                and self.level.blockAt(x, 4, z - 2) == 0 and self.level.blockAt(x, 5, z - 2) == 0\
                                and self.level.blockAt(x, 4, z - 3) == 0 and self.level.blockAt(x, 5, z - 3) == 0:
                            if self.level.blockAt(x, 3, z - 2) in self.surface_blocks and self.level.blockAt(x, 3, z - 3) in self.surface_blocks:
                                distance_x = x - houseBB.minx + 1
                                distance_z = (z - 1) - houseBB.minz + 1

                                if (x, z - 1, 'n', distance_x, distance_z) not in door_locations:
                                    door_locations.append((x, z - 1, 'n', distance_x, distance_z))
                        # EAST
                        elif self.level.blockAt(x + 1, 3, z) in front_door and self.level.blockAt(x + 1, 4, z) == 0 and self.level.blockAt(x + 1, 5, z) == 0 \
                                and self.level.blockAt(x + 2, 4, z) == 0 and self.level.blockAt(x + 2, 5, z) == 0\
                                and self.level.blockAt(x + 3, 4, z) == 0 and self.level.blockAt(x + 3, 5, z) == 0:
                            if self.level.blockAt(x + 2, 3, z) in self.surface_blocks and self.level.blockAt(x + 2, 3, z) in self.surface_blocks:
                                distance_x = (x + 1) - houseBB.minx + 1
                                distance_z = z - houseBB.minz + 1

                                if (x + 1, z, 'e', distance_x, distance_z) not in door_locations:
                                    door_locations.append((x + 1, z, 'e', distance_x, distance_z))
                        # SOUTH
                        elif self.level.blockAt(x, 3, z + 1) in front_door and self.level.blockAt(x, 4, z + 1) == 0 and self.level.blockAt(x, 5, z + 1) == 0 \
                                and self.level.blockAt(x, 4, z + 2) == 0 and self.level.blockAt(x, 5, z + 2) == 0\
                                and self.level.blockAt(x, 4, z + 3) == 0 and self.level.blockAt(x, 5, z + 3) == 0:
                            if self.level.blockAt(x, 3, z + 2) in self.surface_blocks and self.level.blockAt(x, 3, z + 3) in self.surface_blocks:
                                distance_x = x - houseBB.minx + 1
                                distance_z = (z + 1) - houseBB.minz + 1

                                if (x, z + 1, 's', distance_x, distance_z) not in door_locations:
                                    door_locations.append((x, z + 1, 's', distance_x, distance_z))
                        # WEST
                        elif self.level.blockAt(x - 1, 3, z) in front_door and self.level.blockAt(x - 1, 4, z) == 0 and self.level.blockAt(x - 1, 5, z) == 0 \
                                and self.level.blockAt(x - 2, 4, z) == 0 and self.level.blockAt(x - 2, 5, z) == 0\
                                and self.level.blockAt(x - 3, 4, z) == 0 and self.level.blockAt(x - 3, 5, z) == 0:
                            if self.level.blockAt(x - 2, 3, z) in self.surface_blocks and self.level.blockAt(x - 3, 3, z) in self.surface_blocks:
                                distance_x = (x - 1) - houseBB.minx + 1
                                distance_z = z - houseBB.minz + 1

                                if (x - 1, z, 'w', distance_x, distance_z) not in door_locations:
                                    door_locations.append((x - 1, z, 'w', distance_x, distance_z))

        self.all_door_locations.append(door_locations)
        return door_locations
