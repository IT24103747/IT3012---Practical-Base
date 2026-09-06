import random
from collections import deque
import heapq
import math

from logic_engine import KnowledgeBase

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)

# week 03 
class SearchAgent:   
    def __init__(self):
        self.plan = []
        self.active_algo = 'AStar'

        # Practical 05: propositional Knowledge Base used to check logical feasibility.
        self.kb = KnowledgeBase()
        self.kb.tell_rule(['TargetVisible', 'HasDust'], 'SafeToEngage')
        self.kb.tell_rule(['SafeToEngage', 'BloodseekerMissing'], 'Retreat')

    def is_feasible(self, tile_facts):
        """Return False when the KB proves that this tile requires Retreat.

        tile_facts is an iterable of percept strings for one candidate tile.
        The rules remain stored in the KB, but the facts are cleared for every tile.
        """
        self.kb.clear_facts()

        for fact in tile_facts:
            self.kb.tell_fact(fact)

        self.kb.forward_chain()
        return 'Retreat' not in self.kb.facts

    def get_successors(self, state, grid_size, walls):
        x, y = state
        width, height = grid_size

        moves = [
            ('Up', (x, y + 1)),
            ('Down', (x, y - 1)),
            ('Left', (x - 1, y)),
            ('Right', (x + 1, y))
        ]    

        successors = []

        for action, new_state in moves:

            nx, ny = new_state

            if not (0 <= nx < width and 0 <= ny < height):
                continue  

            if new_state in walls:
                continue  
            successors.append((new_state, action))

        return successors


    def bfs_search(self, start, goal, grid_size, walls):

        frontier = deque()
        frontier.append((start, []))  
        reached = {start}

        while frontier:
            state,path = frontier.popleft()

            if state == goal:
                return path

            for next_state, action in self.get_successors(state, grid_size,walls):
                if next_state not in reached:
                    reached.add(next_state)
                    new_path = path + [action]
                    frontier.append((next_state, new_path ))

        return []

    def dfs_search(self, start, goal, grid_size, walls):
        frontier = []
        frontier.append((start, [])) 
        reached = {start}

        while frontier:
            state, path = frontier.pop()

            if state == goal:
                return path

            for next_state, action in self.get_successors(state, grid_size, walls):
                if next_state not in reached:
                    reached.add(next_state)
                    new_path = path + [action]
                    frontier.append((next_state, new_path))

        return []

    def ucs_search(self, start, goal, grid_size, walls):
        frontier = []

        heapq.heappush(frontier, (0, start, []))  
        reached = {}

        while frontier:
            cost, state, path = heapq.heappop(frontier)

            if state in reached and reached[state] <= cost:
                continue

            reached[state] = cost

            if state == goal:
                return path

            for next_state, action in self.get_successors(state, grid_size, walls):

                new_cost = cost + 1  

                new_path = path + [action]

                if(
                    next_state not in reached
                    or new_cost < reached[next_state]
                ):

                    heapq.heappush(
                        frontier, 
                        (new_cost, next_state, new_path)
                    )    

        return []

    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)

    def astar_search(self, start_pos, goal_pos, grid_size, walls, heuristic_type='manhattan', tile_facts=None):
        frontier = []
        reached_states = set()
        tile_facts = tile_facts or {}
        
        if heuristic_type == 'manhattan':
            h_cost = self.manhattan_distance(start_pos, goal_pos)
        else:
            h_cost = self.euclidean_distance(start_pos, goal_pos)
            
        heapq.heappush(frontier, (h_cost, 0, start_pos, []))
        
        while frontier:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(frontier)
            
            if current_pos == goal_pos:
                return path_taken
                
            if current_pos in reached_states:
                continue
                
            reached_states.add(current_pos)
            
            for next_state, action in self.get_successors(current_pos, grid_size, walls):
                if next_state not in reached_states:
                    # Reachability was already checked by get_successors() (bounds/walls).
                    # Practical 05 now checks logical feasibility before adding the node.
                    percepts_for_tile = tile_facts.get(next_state, [])
                    if not self.is_feasible(percepts_for_tile):
                        continue

                    g_new = g_cost + 1  
                    
                    if heuristic_type == 'manhattan':
                        h_new = self.manhattan_distance(next_state, goal_pos)
                    else:
                        h_new = self.euclidean_distance(next_state, goal_pos)
                        
                    f_new = g_new + h_new
                    new_path = path_taken + [action]
                    
                    heapq.heappush(frontier, (f_new, g_new, next_state, new_path))
                    
        return []    

    def find_closest_food(self, start, all_food):

        if not all_food:
            return None

        x, y = start

        return min(
            all_food,
            key=lambda food:
                abs(food[0] - x) + abs(food[1] - y)
        ) 

    def sense_and_act(self, percept: dict) -> str:

        if not self.plan:

            start = percept['agent_pos']
            grid_size = percept['grid_size']
            walls = set(percept['walls'])
            all_food = percept.get('all_food', percept.get('remaining_food',[]))
            # Optional mapping: {(x, y): ['TargetVisible', 'HasDust', ...]}
            tile_facts = percept.get('tile_facts', {})

            if not all_food:
                return 'Stay'

            goal = self.find_closest_food(
                start,
                all_food
            )

            if self.active_algo == 'BFS':

                self.plan = self.bfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == 'DFS':

                self.plan = self.dfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == 'UCS':

                self.plan = self.ucs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == 'AStar':

                self.plan = self.astar_search(
                    start,
                    goal,
                    grid_size,
                    walls,
                    heuristic_type='manhattan',
                    tile_facts=tile_facts
                )    

            else:
                print("Invalid search algorithm")
                return 'Stay'

        if self.plan:
            return self.plan.pop(0)

        return 'Stay'      

if __name__ == "__main__":
    agent = SearchAgent()
    start = (0, 0)
    goal = (3, 4)
    
    print("Manhattan Distance:", agent.manhattan_distance(start, goal))  
    print("Euclidean Distance:", agent.euclidean_distance(start, goal))  