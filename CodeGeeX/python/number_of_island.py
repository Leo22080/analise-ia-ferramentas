"""
Given an m x n 2D binary grid grid which represents a map of '1's (land) and '0's (water), return the number of islands.

An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are all surrounded by water.

 

Example 1:

Input: grid = [
  ["1","1","1","1","0"],
  ["1","1","0","1","0"],
  ["1","1","0","0","0"],
  ["0","0","0","0","0"]
]
Output: 1
Example 2:

Input: grid = [
  ["1","1","0","0","0"],
  ["1","1","0","0","0"],
  ["0","0","1","0","0"],
  ["0","0","0","1","1"]
]
Output: 3
 

Constraints:

m == grid.length
n == grid[i].length
1 <= m, n <= 300
grid[i][j] is '0' or '1'.

class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
"""

class Solution:
    def numIslands(self, grid: list[list[str]]) -> int:
        # Check if the grid is empty
        if not grid:
            return 0

        # Get the number of rows and columns in the grid
        rows, cols = len(grid), len(grid[0])

        # Initialize a set to keep track of visited cells
        visited = set()

        # Initialize a counter for the number of islands
        num_islands = 0

        # Iterate through each cell in the grid
        for i in range(rows):
            for j in range(cols):
                # Check if the current cell is land and not visited
                if grid[i][j] == '1' and (i, j) not in visited:


                    # Increment the island counter
                    num_islands += 1

                    # Perform a depth-first search to mark all connected land cells as visited
                    stack = [(i, j)]
                    while stack:
                        x, y = stack.pop()
                        if 0 <= x < rows and 0 <= y < cols and grid[x][y] == '1' and (x, y) not in visited:
                            visited.add((x, y))
                            stack.append((x + 1, y))
                            stack.append((x - 1, y))
                            stack.append((x, y + 1))
                            stack.append((x, y - 1))

        # Return the number of islands
        return num_islands


# Test the function with the given examples
grid1 = [
  ["1","1","1","1","0"],
  ["1","1","0","1","0"],
  ["1","1","0","0","0"],
  ["0","0","0","0","0"]
]
grid2 = [
  ["1","1","0","0","0"],
]

print(Solution().numIslands(grid1))  # Output: 1
print(Solution().numIslands(grid2))  # Output: 3
# Time complexity: O(m * n), where m is the number of rows and n is the number of columns in the grid.
  