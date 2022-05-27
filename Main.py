from random import *
from Generator import Generator
from Map import Map
import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
from numpy import *
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *
import utilityFunctions as uf
from operator import itemgetter
import glob
from PIL import Image

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
    doors = [64, 71, 193, 194, 195, 196, 197, 324, 330, 427, 428, 429, 430, 431]
    front_doors = [(44, 0), (44, 1), (44, 2), (44, 3), (44, 4), (44, 5), (44, 6), (44, 7), (126, 0), (126, 1), (126, 2), (126, 3), (126, 4), (126, 5)]

    print("\nStep 1: generate heightmap")
    heightMap = Map(level, box, impassable_blocks, wood_blocks, leaf_blocks, decorative_blocks)

    ####################### SAVING IMAGE OF HEIGHTMAP ##################################################################

    img = Image.new('1', (len(heightMap.grid), len(heightMap.grid[0])))
    pixels = img.load()

    for i in range(img.size[0]):
        for j in range(img.size[1]):
            pixels[i, j] = heightMap.grid[i][j]

    img.show()
    img.save('F:\OneDrive - um.edu.mt\Documents\MCEdit\Filters\FYP_Settlement_Generator-master\initialHeightmap.bmp')

    ####################################################################################################################

    print("\nStep 2: generate structures")
    generator = Generator(level, box, options, heightMap, doors, front_doors)
    generator.generate_buildings()

    print("\nStep 3: postprocessing")
    # Expanding roads to be 3 blocks wide
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
                            heightMap.blocks[x2, y2] = blocks_copy[x2, y2]
                            blocks_updated[x2, y2] = (98, 0)[0]

    # Replace unused front door slabs to dirt block
    for x in range(box.minx, box.maxx):
        for z in range(box.minz, box.maxz):
            if level.blockAt(x, 4, z) in doors:
                for front_door in front_doors:
                    # NORTH
                    if level.blockAt(x, 3, z - 1) in front_door:
                        uf.setBlock(level, (2, 0), x, 3, z - 1)
                    # EAST
                    elif level.blockAt(x + 1, 3, z) in front_door:
                        uf.setBlock(level, (2, 0), x + 1, 3, z)
                    # SOUTH
                    elif level.blockAt(x, 3, z + 1) in front_door:
                        uf.setBlock(level, (2, 0), x, 3, z + 1)
                    # WEST
                    elif level.blockAt(x - 1, 3, z) in front_door:
                        uf.setBlock(level, (2, 0), x - 1, 3, z)

    treeCounter = 0
    SchematicFileNames = glob.glob(
        "F:\OneDrive - um.edu.mt\Documents\MCEdit\Filters\FYP_Settlement_Generator-master\Exsilit's_tree_repository\*.schematic")

    total_number_of_trees = 0
    avg_width_of_trees = 0
    avg_height_of_trees = 0
    avg_length_of_trees = 0

    while True:
        generator.treeCandidates = []
        randomChoice = random.choice(SchematicFileNames)
        sourceSchematic = MCSchematic(filename=randomChoice)

        start_x, start_y = generator.heightMap.w / 2, generator.heightMap.h / 2
        sorted_positions = sorted(generator.heightMap.positions, key=lambda position: generator.heightMap.get_distance(position[0], position[1], start_x, start_y))

        distance_data = None
        for x, y in sorted_positions:
            width = sourceSchematic.Width
            height = sourceSchematic.Height
            length = sourceSchematic.Length

            if generator.acceptable(x, y, x + width, y + length):
                if len(generator.treeBBList) > 0:
                    for candidate in generator.treeCandidates:
                        distance = generator.get_distance_data(x, y, candidate[0], candidate[1])

                        if distance_data is None:
                            distance_data = distance
                        elif distance < distance_data:
                            distance_data = distance

                    generator.treeCandidates.append([x, y, x + width, y + length, width, height, length, sourceSchematic, distance_data])
                else:
                    generator.treeCandidates.append([x, y, x + width, y + length, width, height, length, sourceSchematic, distance_data])

            if len(generator.treeCandidates) >= generator.max_candidate_attempts:
                break

        if generator.treeCandidates:
            total_number_of_trees += 0
            print("   Generating tree: " + str(len(generator.treeBBList) + 1))
            print("     Found %i candidates..." % len(generator.treeCandidates))
            shuffle(generator.treeCandidates)

            generator.treeCandidates = sorted(generator.treeCandidates, key=itemgetter(-1), reverse=True)
            top_candidate = generator.treeCandidates[0]
            x1, y1, x2, y2, width, height, length, sourceSchematic, _ = top_candidate

            avg_width_of_trees += width
            avg_length_of_trees += length
            avg_height_of_trees += height

            box_location_x = x1 + generator.box.minx
            box_location_z = y1 + generator.box.minz

            generator.heightMap.fill(x1, y1, 3, x2, y2, 3 + 1, (3, 0))
            newBox = BoundingBox((0, 0, 0), (width, height, length))
            generator.treeBBList.append((newBox, (x1, y1, x2, y2)))
            b = range(4096)
            b.remove(0)  # @CodeWarrior0 and @Wout12345 explained how to merge schematics
            generator.level.copyBlocksFrom(sourceSchematic, newBox, (box_location_x, generator.box.miny, box_location_z), b)
            generator.level.markDirtyBox(generator.box)
        else:
            treeCounter += 1
            if treeCounter > 500:
                print("No more suitable areas to generate trees found.")
                break

    # Convert dirt plots back to grass
    for x in range(box.minx, box.maxx):
        for z in range(box.minz, box.maxz):
            if level.blockAt(x, 3, z) == 3:
                uf.setBlock(level, (2, 0), x, 3, z)

    print("---------------------------- RESULTS ---------------------------------")
    print("Total number of houses: ", str(generator.total_number_of_houses))
    print("Total number of houses in clay district: ", str(generator.houses_clay_district))
    print("Total number of houses in brick district: ", str(generator.houses_brick_district))
    print("Total number of houses in wood district: ", str(generator.houses_wood_district))
    print("Total number of houses in wool district: ", str(generator.houses_wool_district))
    print("Total number of houses in inner region: ", str(generator.houses_inner_region))
    print("Total number of houses in middle region: ", str(generator.houses_middle_region))
    print("Total number of houses in outer region: ", str(generator.houses_outer_region))
    print("Average house size of inner region: ", str(generator.avg_house_sizes_inner_region / generator.houses_inner_region))
    print("Average house size of middle region: ", str(generator.avg_house_sizes_middle_region / generator.houses_middle_region))
    print("Average house size of outer region: ", str(generator.avg_house_sizes_outer_region / generator.houses_outer_region))
    print("Total number of paths: ", str(generator.total_number_of_paths))
    print("Average path length: ", str(generator.avg_path_length / generator.total_number_of_paths))
    print("Total number of connected houses: ", str(generator.total_number_of_connected_houses))
