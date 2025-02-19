import time 
import queue
import tracemalloc as trlloc

Player = '@' 
Switch = '.' 
Space = ' ' 
Stone = '$' 
Wall = '#' 

def Swarm_move(file_path):

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
	pr_queue = queue.PriorityQueue()	
	init_heuristic = heuristic(ares_position, stone_positions, switch_positions, stones_value) 
	pr_queue.put((init_heuristic, ares_position, frozenset(stone_positions), "", 0, stones_value)) 
	explored = set() 
	
	while not pr_queue.empty(): 
		curent, (ax, ay), stones, path, cost, value = pr_queue.get()
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
				if (new_stone_x, new_stone_y) in index_wall: continue
				
				new_cost += new_stones_value[(new_x, new_y)] 
				new_stones_value[(new_stone_x, new_stone_y)] = new_stones_value.pop((new_x, new_y)) 
				new_stones.add((new_stone_x, new_stone_y))
				new_stones.remove((new_x, new_y)) 
				move = move.upper() 
			else: new_cost += 1 

			g = curent + new_cost
			new_heuristic = heuristic((new_x, new_y), new_stones, switch_positions, new_stones_value)
			w = 1.5

			is_deadLock = False 
			for stone in new_stones:
				if deadEnd(index_wall, stone, switch_positions, new_stones): 
					is_deadLock = True
					break 
			
			new_path = new_path + move 
			if not is_deadLock: pr_queue.put((g + w * new_heuristic,(new_x, new_y), frozenset(new_stones), new_path, new_cost, new_stones_value))
			nodes_explored = nodes_explored + 1 

	return None 


def heuristic(ares_position, stones_position, switch_position, stones_value): 
	total_heuristic = 0
	distance_ares_to_stone_min = -1 

	for i, j in stones_position:
		distance_ares_to_stone = abs(ares_position[0] - i) + abs(ares_position[1] - j)  
		if distance_ares_to_stone_min > distance_ares_to_stone or distance_ares_to_stone_min == -1: 
			distance_ares_to_stone_min = distance_ares_to_stone 
		
		distance_stone_to_switches = -1 
		for switch in switch_position:
			temp_distance = abs(i - switch[0]) + abs(j - switch[1]) 
			if distance_stone_to_switches == -1 or temp_distance < distance_stone_to_switches: distance_stone_to_switches = temp_distance 

		total_heuristic += distance_stone_to_switches * (stones_value[(i, j)] + 1) 

	return total_heuristic + distance_ares_to_stone_min



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
	# 	print(Swarm_move(file_path))

	file_path = f"../input/input2.txt"
	print(Swarm_move(file_path))
	