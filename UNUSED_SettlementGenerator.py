# from pymclevel import BoundingBox
#
# import SettlementAStar as pathfinding
# from random import *
# from numpy import *
#
# from AHouse_v5 import perform as house_perform
#
# class Generator:
#     # Initializing
#     def __init__(self, level, box, options, heightMap, materials, seed_number):
#         self.level = level
#         self.box = box
#         self.options = options
#         self.attempts = 0
#         self.heightMap = heightMap
#         self.structures = []
#         self.candidates = []
#         self.candidate_selected = 0
#         self.materials = materials
#         self.seed_number = seed_number
#         self.houseBBList = []
#         seed(self.seed_number)
#
#     # Generating structure data for all the required number of houses
#     def add_sequence(self, sequence):
#         seed(self.seed_number)
#
#         for i in xrange(0, len(sequence)):
#             structure_data = sequence[i]
#             self.add_structure(structure_data)
#
#     def add_structure(self, structure_data):
#         w, h, height, entry_distance, reserved_space, road_distance, category = structure_data
#
#         self.attempts += 1
#         print("\n  Trying to add a new structure (#%i) - %s..." % (self.attempts, category))
#
#         if len(self.structures) > 0:
#             random_structure = choice(self.structures)
#             start_x, start_y = random_structure.x1, random_structure.y1
#         else:
#             start_x, start_y = self.heightMap.w / 2, self.heightMap.h / 2
#
#         sorted_positions = sorted(self.heightMap.positions, key=lambda position: self.heightMap.get_distance(position[0], position[1], start_x, start_y))
#
#         for x, y in sorted_positions:
#             self.heightMap.buffer = []
#
#
#
#             new_structures = [
#                 Structure(self.heightMap, self.structures, x, y, x + w, y + h, height, entry_distance, reserved_space, 's',
#                           category, self.materials, modify_terrain, start_time),
#                 Structure(self.heightMap, self.structures, x, y, x + w, y + h, height, entry_distance, reserved_space, 'n',
#                           category, self.materials, modify_terrain, start_time),
#                 Structure(self.heightMap, self.structures, x, y, x + h, y + w, height, entry_distance, reserved_space, 'w',
#                           category, self.materials, modify_terrain, start_time),
#                 Structure(self.heightMap, self.structures, x, y, x + h, y + w, height, entry_distance, reserved_space, 'e',
#                           category, self.materials, modify_terrain, start_time),
#             ]
#             for structure in new_structures:
#                 if structure.acceptable():
#                     self.candidates.append({'structure': structure})
#             if len(self.candidates) >= max_attempts:
#                 break
#
#         if self.candidates:
#             print("  Found %i candidates..." % (len(self.candidates),))
#
#             shuffle(self.candidates)
#
#             if len(self.structures) < 1 or cat == 'farm':
#                 for candidate in self.candidates:
#                     candidate['score'] = self.get_candidate_score(candidate)
#             else:
#                 for candidate in self.candidates:
#                     candidate['distance_data'] = candidate['structure'].update_distance_data()
#                     candidate['score'] = self.get_candidate_score(candidate)
#
#             self.candidates.sort(key=lambda candidate: candidate['score'], reverse=True)
#
#             if not use_buffer or next_structure_data == None:
#                 top_candidate = self.candidates[0]
#                 self.generate_top_candidate(top_candidate, road_distance, modify_terrain, modify_terrain_roads)
#
#             else:
#                 # buffer = 'plan ahead' by doing one more round of generation for each candidate among the top N choices,
#                 # then select candidate which is predicted to produce best-scored structures in the future
#                 # in this version the buffer is disabled by default, so don't bother trying to understand it :)
#
#                 followup_scores = {}
#                 followup_top_candidates = {}
#
#                 max_buffer_options = 10
#                 max_buffer_attempts = max_attempts
#                 buffer_require_roads = False
#
#                 for i, considered_candidate in enumerate(self.candidates[:max_buffer_options]):
#
#                     self.map.buffer = [considered_candidate['structure']]
#                     followup_scores[i] = None
#
#                     followup_candidates = []
#
#                     w, h, height, entry_distance, reserved_space, road_distance, cat = next_structure_data
#
#                     for x2, y2 in sorted_positions:
#
#                         # buffer could be added at this stage instead of storing it in map.buffer? (assuming the way it works doesn't change)
#
#                         new_structures = [
#                             Structure(self.map, self.structures, x2, y2, x2 + w, y2 + h, height, entry_distance,
#                                       reserved_space, 's', cat, self.materials, modify_terrain, start_time),
#                             Structure(self.map, self.structures, x2, y2, x2 + w, y2 + h, height, entry_distance,
#                                       reserved_space, 'n', cat, self.materials, modify_terrain, start_time),
#                             Structure(self.map, self.structures, x2, y2, x2 + h, y2 + w, height, entry_distance,
#                                       reserved_space, 'w', cat, self.materials, modify_terrain, start_time),
#                             Structure(self.map, self.structures, x2, y2, x2 + h, y2 + w, height, entry_distance,
#                                       reserved_space, 'e', cat, self.materials, modify_terrain, start_time),
#                         ]
#                         for structure in new_structures:
#                             if structure.acceptable():
#                                 followup_candidates.append({'structure': structure})
#                         if len(followup_candidates) >= max_buffer_attempts:
#                             break
#
#                     if followup_candidates:
#                         if cat == 'farm':
#                             for candidate in followup_candidates:
#                                 candidate['score'] = self.get_candidate_score(candidate)
#                         else:
#                             for candidate in followup_candidates:
#                                 candidate['distance_data'] = candidate['structure'].update_distance_data()
#                                 candidate['score'] = self.get_candidate_score(candidate)
#
#                         followup_candidates.sort(key=lambda candidate: candidate['score'], reverse=True)
#
#                         top_followup_candidate = followup_candidates[0]
#                         top_followup_score = top_followup_candidate['score']
#                         followup_scores[i] = top_followup_score
#                         followup_top_candidates[i] = top_followup_candidate
#
#                     # print("    scenario %i (%i,%i / %i,%i - followup scores: %s)" % (i+1, considered_candidate['structure'].x1, considered_candidate['structure'].y1, top_followup_candidate['structure'].x1, top_followup_candidate['structure'].x2, top_followup_score[:10]))
#                     # print("    scenario %i scores: %s)" % (i+1, considered_candidate['score'][:6]))
#
#                 selected_scenario = 0
#                 top_candidate = None
#                 top_followup = None
#                 current_compared_score = None
#                 for i, considered_candidate in enumerate(self.candidates[:max_buffer_options]):
#
#                     # get rid of buffer_require_roads?
#                     if buffer_require_roads and considered_candidate['structure'].has_distance_data:
#                         shortest_point_distance, entry_target, entry_source, source = considered_candidate[
#                             'distance_data']
#                         path = self.get_path(considered_candidate, road_distance)
#
#                     if not buffer_require_roads or not considered_candidate['structure'].has_distance_data or (
#                             path and not entry_target == entry_source):
#
#                         if current_compared_score == None:
#                             top_candidate = considered_candidate
#                             top_followup = followup_top_candidates[i]
#                             current_compared_score = followup_scores[i]
#                             selected_scenario = i
#                         elif followup_scores[i] > current_compared_score:
#                             top_candidate = considered_candidate
#                             top_followup = followup_top_candidates[i]
#                             current_compared_score = followup_scores[i]
#                             selected_scenario = i
#
#                 if top_candidate != None:
#                     # print("\nSelected scenario: %i\n" % (selected_scenario+1,))
#                     self.generate_top_candidate(top_candidate, road_distance, modify_terrain, modify_terrain_roads)
#                 else:
#                     top_candidate = self.candidates[0]
#                     self.generate_top_candidate(top_candidate, road_distance, modify_terrain, modify_terrain_roads)
#
#         else:
#             print(" -No acceptable area to generate building found.")
#
#         print("  Done (time elapsed: %i s)." % (time.time() - start_time))
#
#     def adjust_road_block(self, x, y, z):
#         self.heightMap.fill_block(x, y, z, self.materials['road'])
#         self.heightMap.clear_space(x, y + 1, z)
#
#     def get_path(self, top_candidate):
#         # note:sometimes paths ascend up 2 or more squares when crossing hills/mountains
#         shortest_point_distance, entry_target, entry_source, _ = top_candidate['distance_data']
#         return pathfinding.astar(self.heightMap.grid, entry_target, entry_source, self.heightMap)
#
#     def generate_top_candidate(self, road_distance):
#         siteOptions = {'Seed:': randint(0, 99999999999)}
#         center_x = (self.box.minx + self.box.maxx) / 2
#         center_y = (self.box.miny + self.box.maxy) / 2
#         center_z = (self.box.minz + self.box.maxz) / 2
#         width, height, length = randint(17, 25), randint(15, 50), randint(17, 25)
#
#         newBox = BoundingBox((center_x, self.box.miny, center_z), (width, height, length))
#         self.houseBBList.append(newBox)
#         house_perform(self.level, newBox, siteOptions)
#
#         self.structures.append(newBox)
#         self.heightMap.update_entire_grid(self.structures, road_distance)
#
#         if len(self.houseBBList) > 1:
#             print("  Trying to generate road...")
#
#             target = self.houseBBList[-1]
#             shortest_point_distance, entry_target, entry_source, source = top_candidate['distance_data']
#
#             if self.get_path(self.houseBBList[-1]):
#                 print(" :Found path (length: %i)" % (len(self.get_path(self.houseBBList[-1]))))
#
#                 for x, y in self.get_path(self.houseBBList[-1]):
#                     self.heightMap.fill_block_relative_to_surface(x, y, 0, self.materials['road'])
#                     self.heightMap.clear_space_relative_to_surface(x, y, 1)
#
#                 target_entry_path = target.get_entry_path(entry_target)[:-1]
#                 source_entry_path = source.get_entry_path(entry_source)[:-1]
#
#                 self.heightMap.complete_path(target_entry_path, self.materials['road'])
#                 self.heightMap.complete_path(source_entry_path, self.materials['road'])
#
#             else:
#                 if entry_target == entry_source:
#                     print(" :Entry points align without a need for path.")
#
#                     target_entry_path = target.get_entry_path(entry_target)[:-1]
#                     source_entry_path = source.get_entry_path(entry_source)[:-1]
#
#                     self.heightMap.complete_path(target_entry_path, self.materials['road'])
#                     self.heightMap.complete_path(source_entry_path, self.materials['road'])
#
#                 else:
#                     print(" -No path found.")
