import time 
import tracemalloc as trlloc
from collections import deque 

Player = '@' 
Switch = '.' 
Space = ' ' 
Stone = '$' 
Wall = '#' 


def bfs_move(file_path):

	ares_position = (0, 0)
	stone_positions = [] 
	switch_positions = []
	index_wall = []
	stones_value = {}
	correct_place = []

	with open(file_path, 'r') as file:
		value = file.readline().strip() 
		value_of_stones = list(map(int, value.split()))
		data = file.readlines()  
		index = 0
		for i in range(len(data)): 
			arr = []
			for j in range(len(data[i])): 
				if data[i][j] == Player: ares_position = (i, j) 
				if data[i][j] == Stone:
					stone_positions.append((i, j))
					stones_value[(i, j)] = value_of_stones[index] 
					index = index + 1 
				if data[i][j] == Switch: switch_positions.append((i, j)) 
				if data[i][j] == Wall: index_wall.append((i, j))
				if data[i][j] == '*': 
					correct_place.append((i, j)) 
					switch_positions.append((i, j)) 
					stone_positions.append((i, j))
					stones_value[(i, j)] = value_of_stones[index] 
					index = index + 1 
	
	
	start_time = time.time()
	trlloc.start()
	nodes_explored = 0
	queue = deque() 
	queue.append((ares_position, frozenset(stone_positions), "", 0, stones_value)) 
	explored = set() 
	
	while queue: 
		(ax, ay), stones, path, cost, value = queue.popleft()
		if stones == frozenset(switch_positions): 
			end_time = time.time() 
			_, memory = trlloc.get_traced_memory() 
			trlloc.stop() 
			return {
				'Step: ': len(path),
				'Weight: ': cost,
				'Node: ': nodes_explored, 
				'Path: ': path, 
				'Time (Ms): ': "{:.2f}".format(1000 * (end_time - start_time)), 
				'Memory (Mb): ': "{:.2f}".format(memory / (1024 * 1024))
			}
		
		if (ax, ay, stones) in explored : continue
		explored.add((ax, ay, stones)) 
		
		for next_x, next_y, move in [(-1, 0, 'u'), (0, -1, 'l'), (0, 1, 'r'), (1, 0, 'd')]:
			(new_x, new_y) = (ax + next_x, ay + next_y)
			if (new_x, new_y) in index_wall: continue 

			new_stones = set(stones) 
			new_stones_value = value.copy() 
			new_path = path 
			new_cost = cost 

			if (new_x, new_y) in stones: 
				(new_stone_x,new_stone_y) = (new_x + next_x, new_y + next_y) 
				if (new_stone_x, new_stone_y) in index_wall or (new_stone_x, new_stone_y) in stones: continue
				
				new_cost += new_stones_value[(new_x, new_y)] 
				new_stones_value[(new_stone_x, new_stone_y)] = new_stones_value.pop((new_x, new_y)) 
				new_stones.add((new_stone_x, new_stone_y))
				new_stones.remove((new_x, new_y)) 
				move = move.upper() 
			else: new_cost += 1 
			is_deadlock = False
			for stone in new_stones:
				if deadEnd(index_wall, stone, switch_positions, new_stones):
					is_deadlock = True 
					break 
			new_path = new_path + move 
			if not is_deadlock: 
				queue.append(((new_x, new_y), frozenset(new_stones), new_path, new_cost, new_stones_value))
			nodes_explored = nodes_explored + 1 

	return None 

def deadEnd(walls_index, index_stone, switches, stones):
	stone_x, stone_y = index_stone
	on_switches = (stone_x, stone_y) in switches
	up = (stone_x - 1, stone_y) in walls_index or (stone_x - 1, stone_y) in stones
	down = (stone_x + 1, stone_y) in walls_index or (stone_x + 1, stone_y) in stones
	right = (stone_x, stone_y + 1) in walls_index or (stone_x, stone_y + 1) in stones 
	left = (stone_x, stone_y - 1) in walls_index or (stone_x, stone_y - 1) in stones 
	if (up and left) and ((stone_x - 1, stone_y - 1) in walls_index or (stone_x - 1, stone_y - 1) in stones) and not on_switches: return True
	if (up and right) and ((stone_x - 1, stone_y + 1) in walls_index or (stone_x - 1, stone_y + 1) in stones) and not on_switches: return True
	if (down and left) and ((stone_x + 1, stone_y - 1) in walls_index or (stone_x + 1, stone_y - 1) in stones) and not on_switches: return True
	if (down and right) and ((stone_x + 1, stone_y + 1) in walls_index or (stone_x + 1, stone_y + 1) in stones) and not on_switches: return True

if __name__ == "__main__":
	# for i in range(10): 
	# 	print(f"test{i + 1}: ")
	# 	file_path = f"./test/input-0{i + 1}.txt" if i + 1 < 10 else f"./test/input-{i + 1}.txt"
	# 	print(bfs_move(file_path))

	file_path = f"../input/input1.txt"
	print(bfs_move(file_path))
	