from random import *
from mcplatform import *
from Generator import Generator
from Map import Map
import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
from numpy import *
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *
import utilityFunctions as uf

# MINIMUM HOUSE: 17W x 10H x 17L
# MAXIMUM HOUSE: 45W X 90H X 45L
# siteOptions = {'Operation': 'House', 'Seed:': randint(0, 99999999999)}
# house_perform(level, box, siteOptions)



# lots of spaces to align checkboxes
inputs = (
    ("Settlement Generator", "label"),
    ("Creator: Nathan Camilleri", "label"),
    ("Note: Selection area should start from underground", "label"),
)


def perform(level, box, options):
    wood_blocks = {17, 162, 99, 100}
    leaf_blocks = {18, 161, 106}
    decorative_blocks = {6, 30, 31, 32, 37, 38, 39, 40, 50, 51, 55, 59, 63, 78, 81, 104, 105, 111, 141, 142, 175, 207}
    impassable_blocks = {8, 9, 10, 11, 79}

    print("\nStep 1: generate heightmap")
    heightMap = Map(level, box, impassable_blocks, wood_blocks, leaf_blocks, decorative_blocks, clear_decorations=False, clear_trees=False, roads_can_cross_corners=False, start_time=0)

    # with open("F:\OneDrive - um.edu.mt\Documents\MCEdit\Filters\FYPGenerator\\file1.txt", 'a') as f:
    #     for item in heightMap.grid:
    #         print >> f, item

    print("\nStep 2: generate structures")
    generator = Generator(level, box, options, heightMap)
    generator.generate_buildings()

    # sequence = []
    # for _ in xrange(number_of_structures):
    #     sequence.append((choice(sizes_w), choice(sizes_h), 5, entry_distance, reserved_space, road_distance, 'house'))

    # generator.generate_buildings()

    print("\nStep 3: postprocessing")
    # expand roads
    blocks_copy = copy(heightMap.blocks)
    blocks_updated = copy(heightMap.blocks)
    reserved_materials = {(98, 0)[0]}

    for x in xrange(1, heightMap.w):
        for y in xrange(1, heightMap.h):
            if heightMap.blocks[x, y] == (98, 0)[0]:
                for x2 in xrange(x - 1, x + 2):
                    for y2 in xrange(y - 1, y + 2):
                        if heightMap.altitudes[x2, y2] == heightMap.altitudes[x, y] and not heightMap.blocks[x2, y2] in reserved_materials:
                            heightMap.fill_block(x2, y2, heightMap.altitudes[x, y], (98, 0))
                            #heightMap.clear_space(x2, y2, heightMap.altitudes[x, y] + 1)
                            heightMap.blocks[x2, y2] = blocks_copy[x2, y2]
                            blocks_updated[x2, y2] = (98, 0)[0]

    # Convert dirt plots back to grass
    for x in range(box.minx, box.maxx):
        for z in range(box.minz, box.maxz):
            if level.blockAt(x, 3, z) == 3:
                uf.setBlock(level, (2, 0), x, 3, z)

################################################################################################################################################################


    # determine materials
    # wood_source = (5, 0)
    # print("")
    # print("Tree area: %f" % map.tree_area)
    # print("")
    # for k, v in map.tree_probabilities.items():
    #     print("  %-20s %f" % (k, v))
    #
    # tree_keys = sorted(map.tree_probabilities.keys(), key=lambda k: map.tree_probabilities[k], reverse=True)
    # if len(tree_keys) > 0:
    #     wood_source = tree_keys[0]
    # else:
    #     wood_source = (5, 0)
    #
    # print("\nTree keys: %s" % (tree_keys,))


    # everything associated with clearing trees starts here
    # print("  Clearing trees...")
    #
    # tree_points = []
    # for x in xrange(0, map.w):
    #     for y in xrange(0, map.h):
    #         if map.trees[x, y] is not None:
    #             tree_points.append((x, y))
    #
    # # get a table of nearest tree coordinates for every point
    # # this is used to approximate which tree the surrounding leaves belong to, though the approach isn't perfectly accurate)
    # # it also doesn't extend beyond selection box, meaning that trees around it may get cut in half, etc.
    #
    # nearest_tree_table = empty((map.w, map.h), object)
    # if len(tree_points) > 0:
    #     for x in xrange(0, map.w):
    #         for y in xrange(0, map.h):
    #             nearest_tree_table[x, y] = (x, y)
    #             if map.trees[x, y] is None:
    #                 for d in xrange(1, max(map.w, map.h)):
    #                     points = []
    #
    #                     for i in xrange(0, d + 1):
    #                         x1 = x - d + i
    #                         y1 = y - i
    #                         if 0 <= x1 < map.w and 0 <= y1 < map.h and map.trees[x1, y1] is not None:
    #                             points.append((x1, y1))
    #                         x2 = x + d - i
    #                         y2 = y + i
    #                         if 0 <= x2 < map.w and 0 <= y2 < map.h and map.trees[x2, y2] is not None:
    #                             points.append((x2, y2))
    #
    #                     for i in xrange(1, d):
    #                         x1 = x - i
    #                         y1 = y + d - i
    #                         if 0 <= x1 < map.w and 0 <= y1 < map.h and map.trees[x1, y1] is not None:
    #                             points.append((x1, y1))
    #                         x2 = x + d - i
    #                         y2 = y - i
    #                         if 0 <= x2 < map.w and 0 <= y2 < map.h and map.trees[x2, y2] is not None:
    #                             points.append((x2, y2))
    #
    #                     if points:
    #                         ordered_points = sorted(points,
    #                                                 key=lambda position: map.get_distance(position[0], position[1], x,
    #                                                                                       y))
    #                         nearest_tree_table[x, y] = ordered_points[0]
    #                         break
    #
    # # actually clear trees
    # for x in xrange(0, map.w):
    #     for y in xrange(0, map.h):
    #         if map.trees[x, y] is not None:
    #             tree_near_settlement = False
    #             distance = 8
    #
    #             for x2 in xrange(max(0, x - distance), min(map.w, x + distance)):
    #                 for y2 in xrange(max(0, y - distance), min(map.h, y + distance)):
    #
    #                     if map.blocks[x2, y2] in reserved_materials or map.blocks[x2, y2] == materials['road'][0]:
    #                         tree_near_settlement = True
    #
    #                 if tree_near_settlement:
    #                     break
    #
    #             if tree_near_settlement:
    #                 map.clear_tree(x, y, nearest_tree_table)
