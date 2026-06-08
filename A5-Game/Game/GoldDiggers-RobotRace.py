from game_utils import Direction as D
from game_utils import TileStatus
from game_utils import Map
from player_base import Player
import numpy as np
from shortestpaths import AllShortestPaths


class BasicBot(Player):

        def __init__(self,*,random=False):
                self.random=random

        def reset(self, player_id, max_players, width, height):
                self.player_name = "Team_1_GoldDigger"
                self.ourMap = Map(width, height)
                self.mine_memory = {}
                self.last_junction = None
                self.repositioning_target = None

        def round_begin(self, r):
                 #map memory
                #store status of fields that you see from the current position
                status = self.status

                #delete expired mines from map and mine memory
                for pos, expiry_round in list(self.mine_memory.items()):
                        if r >= expiry_round:
                                del self.mine_memory[pos]
                                if self.ourMap[pos].status == TileStatus.Mine:
                                        self.ourMap[pos].status = TileStatus.Empty

                for dx in range(-status.params.visibility, status.params.visibility +1):
                        for dy in range(-status.params.visibility, status.params.visibility +1):
                                x = status.x + dx 
                                y = status.y + dy

                                #map boundary
                                if not self.is_inside_map((x, y)):
                                        continue

                                tile_status = status.map[x,y].status

                                if  tile_status != TileStatus.Unknown:
                                        self.ourMap[x,y].status = tile_status

                                        if tile_status == TileStatus.Mine:
                                                if (x,y) not in self.mine_memory:
                                                        self.mine_memory[(x,y)] = r + status.params.mineExpiryTime
                                        elif tile_status == TileStatus.Empty:
                                                self.mine_memory.pop((x,y), None)

        def is_inside_map(self, position):
                x, y = position
                if x < 0 or y < 0:
                                return False
                elif x >= self.ourMap.width or y >= self.ourMap.height:
                                return False
                else:
                        return True

        def _as_direction(self,curpos,nextpos):
                for d in D:
                        diff = d.as_xy()
                        if (curpos[0] + diff[0], curpos[1] + diff[1]) ==  nextpos:
                                return d
                return None

        def _as_directions(self,curpos,path):
                return [self._as_direction(x,y) for x,y in zip([curpos]+path,path)]

        def move(self, status):
                ourMap = self.ourMap

                curpos = (status.x,status.y)

                assert len(status.goldPots) > 0
                goldLocation = next(iter(status.goldPots))

                # remember last junction
                neighbours = self.ourMap.nonWallNeighbours(curpos)
                if len(neighbours) >= 3:
                        self.last_junction = curpos

                print(status)
                print("status"*20)
                ## move towards gold pot
                numMoves = 4
                
                paths_to_gold = AllShortestPaths(goldLocation,ourMap)
                bestpath = paths_to_gold.shortestPathFrom(curpos)
                bestpath = self.check_path(status, bestpath, numMoves)
                bestpath = bestpath[1:]
                bestpath.append( goldLocation )

                low_gold_mode = True if status.gold < 20 else False
                max_rounds_to_pot = 4 if not low_gold_mode else 1

                distance=len(bestpath)
                #numMoves = distance
                #TODO: also check for total remaining rounds in the game
                if numMoves>0 and distance/numMoves > min(status.goldPotRemainingRounds, max_rounds_to_pot):
                        # waiting mode
                        # numMoves = 0
                        # repositioning mode: move towards last junction to increase likelihood of finding next gold pot
                        numMoves = 1
                        if self.repositioning_target is not None:
                                if curpos == self.repositioning_target:
                                        self.repositioning_target = None
                                        numMoves = 0

                        # find all free neighbors to find out if stuck in a dead end
                        elif len(self.ourMap.nonWallNeighbours(curpos)) <= 1 and self.last_junction is not None:
                                paths_to_junction = AllShortestPaths(self.last_junction, self.ourMap)
                                bestpath = paths_to_junction.shortestPathFrom(curpos)
                                bestpath = bestpath[1:]
                                bestpath.append(self.last_junction)
                                self.repositioning_target = self.last_junction

                        else:
                        # otherwise wait
                                numMoves = 0

                return self._as_directions(curpos,bestpath[:numMoves])
        
        def check_path(self, status, path, numMoves):
                i = 0
                for tile in path:
                        if self.check_for_obstacles(status, tile[0], tile[1]):
                                print("collision detected", tile)
                                path = path[:i]
                                break 
                        if self.is_enemy_on_tile(status, tile):
                                print("Enemy detected", tile)
                                path = path[:i]
                                break
                        i+=1
                return path

        def check_for_obstacles(self, status, x, y):
                '''
                checks a given tile for obstacles (walls & mines)
                Input: current status and x, y coordinates of tile to check
                Output: True -> obstacle on tile, False -> tile is clear, None if we cannot see the tile
                '''
                tileStatus = self.ourMap[x, y].status
                # new version: if tile is empty we go, otherwise we don't. This should hopefully detect players too
                if tileStatus != TileStatus.Empty:
                        return True
                return False
                
                # old version: check specifically for walls and mines
                """ if  tileStatus == TileStatus.Wall or tileStatus == TileStatus.Mine:
                        print("Found an obstacle")
                        return True
                elif tileStatus == TileStatus.Unknown: return None
                return False"""

        def is_enemy_on_tile(self, status, pos):
                for other in status.others:
                        if other is not None and (other.x, other.y) == pos:
                                return True
                return False

players = [ BasicBot()]
