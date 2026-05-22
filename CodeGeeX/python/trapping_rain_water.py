"""
Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.

 

Example 1:


Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]
Output: 6
Explanation: The above elevation map (black section) is represented by array [0,1,0,2,1,0,1,3,2,1,2,1]. In this case, 6 units of rain water (blue section) are being trapped.
Example 2:

Input: height = [4,2,0,3,2,5]
Output: 9
 

Constraints:

n == height.length
1 <= n <= 2 * 104
0 <= height[i] <= 105

class Solution:
    def trap(self, height: List[int]) -> int:
"""

class Solution:
    def trap(self, height: list[int]) -> int:
        # Initialize variables
        left = 0
        right = len(height) - 1
        left_max = 0
        right_max = 0
        water = 0

        # Iterate through the array
        while left < right:
            # Update the left and right max values  
            if height[left] < height[right]:
                if height[left] >= left_max:
                    left_max = height[left]
                else:
                    water += left_max - height[left]
                left += 1
            else:
                if height[right] >= right_max:
                    right_max = height[right]
                else:
                    water += right_max - height[right]
                right -= 1
        return water
# Time complexity: O(n)

# Space complexity: O(1)
# Runtime: 76 ms, faster than 98.46% of Python3 online submissions for Trapping Rain Water.
# Memory Usage: 16.2 MB, less than 98.46% of Python3 online submissions for Trapping Rain Water.

# Test cases
height1 = [0,1,0,2,1,0,1,3,2,1,2,1]
height2 = [4,2,0,3,2,5]
height3 = [4,2,3]
height4 = [5,4,1,2]

sol = Solution()
print(sol.trap(height1)) # 6
print(sol.trap(height2)) # 9
print(sol.trap(height3)) # 1
print(sol.trap(height4)) # 1

