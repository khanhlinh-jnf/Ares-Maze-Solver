import API.algorithms
import API.gui

if __name__ == "__main__":
	print("1. Get output of level you want to solve")
	print("2. Play game and solve if you want")
 
	choice = input("Enter your choice: ")
	if choice == "2": API.gui.main()
	elif choice == "1": API.algorithms.write_result_to_output()
	else: print("Invalid choice")
