from math import sqrt
from numpy import *


def get_block(level, x, y, z):
    return level.blockAt(x, y, z)


def set_block(level, (block, data), x, y, z):
    level.setBlockAt(int(x), int(y), int(z), block)
    level.setBlockDataAt(int(x), int(y), int(z), data)


class Map:
    def __init__(self, level, box, impassable_blocks, wood_blocks, leaf_blocks, decorative_blocks):
        self.grid = None
        self.altitudes = None
        self.blocks = None
        self.positions = None
        self.level = level
        self.box = box

        self.x, self.y = box.minx, box.minz
        self.w, self.h = box.maxx - box.minx, box.maxz - box.minz

        self.impassable_blocks = impassable_blocks
        self.wood_blocks = wood_blocks
        self.leaf_blocks = leaf_blocks
        self.decorative_blocks = decorative_blocks

        self.setup()

    def setup(self):
        print("  Generating heightmap...")

        self.blocks = zeros((self.w, self.h)).astype(int)
        self.altitudes = zeros((self.w, self.h)).astype(int)

        box = self.box
        level = self.level

        for x in xrange(box.minx, box.maxx):
            for z in xrange(box.minz, box.maxz):
                for y in xrange(box.maxy, box.miny, -1):

                    block = get_block(level, x, y, z)
                    if block != 0:
                        if block not in self.decorative_blocks:
                            self.altitudes[x - self.x, z - self.y] = int(y)
                            self.blocks[x - self.x, z - self.y] = int(block)
                            break

        # Collecting positions
        self.positions = set()
        for x in xrange(self.w):
            for y in xrange(self.h):
                if not self.blocks[x, y] in self.impassable_blocks:
                    self.positions.add((x, y))

        # Setting up grid
        self.grid = zeros((self.w, self.h)).astype(int)

    def update_grid_for_structure(self, width, length, structure_x, structure_y, road_distance, door_locations):
        x1 = structure_x - self.x
        x2 = (structure_x - self.x) + width
        y1 = structure_y - self.y
        y2 = (structure_y - self.y) + length

        for x in xrange(max(0, x1 - road_distance), min(self.w, x2 + road_distance)):
            for y in xrange(max(0, y1 - road_distance), min(self.h, y2 + road_distance)):
                self.grid[x, y] = 1

        for (door_x, door_y, direction, distance_x, distance_z) in door_locations:
            door_x = door_x - self.x
            door_y = door_y - self.y
            entry_path = self.get_entry_path_default(direction, door_y, door_x, distance_x, distance_z)

            for x, y in entry_path:
                try:
                    self.grid[x, y] = 0
                except IndexError:
                    break

    def fits_inside(self, x1, y1, x2, y2):
        if x1 >= 0 and x2 <= self.w and y1 >= 0 and y2 <= self.h:
            return True
        return False

    def collides(self, x1, y1, x2, y2, collider_blocks):
        for x in range(x1, x2):
            for y in range(y1, y2):
                if self.blocks[x, y] in collider_blocks:
                    return True
        return False

    def complete_path(self, points, road_material):
        for x, y in points:
            self.fill_block_relative_to_surface(x, y, 0, road_material)

    def fill_block_relative_to_surface(self, x, y, z, material):
        set_block(self.level, material, self.x + x, self.altitudes[x, y] + z, self.y + y)
        self.blocks[x, y] = material[0]  # only if it's the same or higher than altitude?
        if material[0] == 0:
            self.positions.discard((x, y))

    def fill_block(self, x, y, z, material):
        set_block(self.level, material, self.x + x, z, self.y + y)
        if material[0] != 0:
            self.blocks[x, y] = material[0]
            self.positions.discard((x, y))

    def fill(self, x1, y1, z1, x2, y2, z2, material):
        for x in range(x1, x2):
            for y in range(y1, y2):
                for z in range(z1, z2):
                    set_block(self.level, material, self.x + x, z, self.y + y)
                    if material[0] != 0:
                        self.blocks[x, y] = material[0]
                        self.positions.discard((x, y))

    def get_entry_path_default(self, direction, door_y, door_x, distance_x, distance_y):
        pathway = []
        if direction == 's':
            for y in xrange(door_y, door_y + distance_y + 1):
                pathway.append((door_x, y))
        elif direction == 'n':
            for y in xrange(door_y, door_y - distance_y - 1, -1):
                pathway.append((door_x, y))
        elif direction == 'e':
            for x in xrange(door_x, door_x + distance_x + 1):
                pathway.append((x, door_y))
        elif direction == 'w':
            for x in xrange(door_x, door_x - distance_x - 1, -1):
                pathway.append((x, door_y))
        return pathway

    def get_distance(self, x1, y1, x2, y2):
        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def box_collision(self, a_x1, a_y1, a_x2, a_y2, b_x1, b_y1, b_x2, b_y2):
        return not (b_x1 > a_x2 or b_x2 < a_x1 or b_y1 > a_y2 or b_y2 < a_y1)