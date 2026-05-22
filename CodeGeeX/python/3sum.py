"""
Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.

Notice that the solution set must not contain duplicate triplets.

 

Example 1:

Input: nums = [-1,0,1,2,-1,-4]
Output: [[-1,-1,2],[-1,0,1]]
Explanation: 
nums[0] + nums[1] + nums[2] = (-1) + 0 + 1 = 0.
nums[1] + nums[2] + nums[4] = 0 + 1 + (-1) = 0.
nums[0] + nums[3] + nums[4] = (-1) + 2 + (-1) = 0.
The distinct triplets are [-1,0,1] and [-1,-1,2].
Notice that the order of the output and the order of the triplets does not matter.
Example 2:

Input: nums = [0,1,1]
Output: []
Explanation: The only possible triplet does not sum up to 0.
Example 3:

Input: nums = [0,0,0]
Output: [[0,0,0]]
Explanation: The only possible triplet sums up to 0.
 

Constraints:

3 <= nums.length <= 3000
-105 <= nums[i] <= 105

class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
"""

class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        # Sort the array
        nums.sort()
        # Initialize an empty list to store the triplets
        triplets = []
        # Iterate through the array
        for i in range(len(nums) - 2):
            # Skip duplicate values
            if i > 0 and nums[i] == nums[i-1]:
                continue
            # Initialize two pointers
            left = i + 1
            right = len(nums) - 1
            # While the left pointer is less than the right pointer
            while left < right:
                # Calculate the sum of the current triplet
                current_sum = nums[i] + nums[left] + nums[right]
                # If the sum is equal to 0, add the triplet to the list
                if current_sum == 0:
                    triplets.append([nums[i], nums[left], nums[right]])
                    # Move the left pointer to the right
                    left += 1
                    # Move the right pointer to the left
                    right -= 1
                    # Skip duplicate values
                    while left < right and nums[left] == nums[left-1]:
                        left += 1
                    while left < right and nums[right] == nums[right+1]:
                        right -= 1
                # If the sum is less than 0, move the left pointer to the right
                elif current_sum < 0:
                    left += 1
                # If the sum is greater than 0, move the right pointer to the left
                else:
                    right -= 1
        return triplets
# Time complexity: O(n^2)