# agent.py
import random
from collections import deque
import heapq

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
        self.active_algo = 'UCS'

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
                continue  # Out of bounds

            if new_state in walls:
                continue  # Hit a wall
            successors.append((new_state, action))

        return successors


    def bfs_search(self, start, goal, grid_size, walls):

        frontier = deque()
        frontier.append((start, []))  # (state, path)
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
        frontier.append((start, []))  # (state, path)
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

        heapq.heappush(frontier, (0, start, []))  # (cost, state, path)
        reached = {}

        while frontier:
            cost, state, path = heapq.heappop(frontier)

            if state in reached and reached[state] <= cost:
                continue

            reached[state] = cost

            if state == goal:
                return path

            for next_state, action in self.get_successors(state, grid_size, walls):

                new_cost = cost + 1  # Assuming uniform cost for each move

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


    def find_closest_food(self, start, all_food):

        if not all_food:
            return None

        x, y = start

        # Manhattan distance
        return min(
            all_food,
            key=lambda food:
                abs(food[0] - x) + abs(food[1] - y)
        ) 

    def sense_and_act(self, percept: dict) -> str:

        # Only search when the previous plan is finished
        if not self.plan:

            start = percept['agent_pos']
            grid_size = percept['grid_size']
            walls = set(percept['walls'])
            all_food = percept['all_food']

            # No food remaining
            if not all_food:
                return 'Stay'

            # Select the closest food pellet
            goal = self.find_closest_food(
                start,
                all_food
            )

            # Run selected search algorithm
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

            else:
                print("Invalid search algorithm")
                return 'Stay'

        # Execute the first action in the generated plan
        if self.plan:
            return self.plan.pop(0)

        return 'Stay'           