/*
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

class Solution {
public:
    int numIslands(vector<vector<char>>& grid) {
        
    }
};
*/

#include <vector>
class Solution {
public:
    int numIslands(vector<vector<char>>& grid) {
        if (grid.empty() || grid[0].empty()) return 0;
        
        int m = grid.size();
        int n = grid[0].size();
        int count = 0;
        
        for (int i = 0; i < m; ++i) {
            for (int j = 0; j < n; ++j) {
                // 如果发现陆地，说明找到了一个新岛屿
                if (grid[i][j] == '1') {
                    count++;
                    // 使用 DFS 将整个岛屿淹没，避免重复计数
                    dfs(grid, i, j, m, n);
                }
            }
        }
        
        return count;
    }

private:
    void dfs(vector<vector<char>>& grid, int i, int j, int m, int n) {
        // 边界条件检查：越界或者遇到水，则停止搜索
        if (i < 0 || i >= m || j < 0 || j >= n || grid[i][j] == '0') {
            return;
        }
        
        // 将当前陆地淹没
        grid[i][j] = '0';
        
        // 递归淹没上下左右四个方向的相邻陆地
        dfs(grid, i - 1, j, m, n); // 上
        dfs(grid, i + 1, j, m, n); // 下
        dfs(grid, i, j - 1, m, n); // 左
        dfs(grid, i, j + 1, m, n); // 右
    }
};

/*  
作者：LeetCode-Solution
链接：https://leetcode-cn.com/problems/number-of-islands/solution/dao-yu-shu-liang-by-leetcode-solution/
来源：力扣（LeetCode）
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
*/