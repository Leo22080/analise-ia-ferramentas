"""
Given an array of strings strs, group the anagrams together. You can return the answer in any order.

 

Example 1:

Input: strs = ["eat","tea","tan","ate","nat","bat"]

Output: [["bat"],["nat","tan"],["ate","eat","tea"]]

Explanation:

There is no string in strs that can be rearranged to form "bat".
The strings "nat" and "tan" are anagrams as they can be rearranged to form each other.
The strings "ate", "eat", and "tea" are anagrams as they can be rearranged to form each other.
Example 2:

Input: strs = [""]

Output: [[""]]

Example 3:

Input: strs = ["a"]

Output: [["a"]]

 

Constraints:

1 <= strs.length <= 104
0 <= strs[i].length <= 100
strs[i] consists of lowercase English letters.

class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
"""

class Solution:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        # Sort the array
        strs.sort()

        # Create a dictionary to store the anagrams
        anagrams = {}

        # Iterate through the array
        for word in strs:
            # Sort the word
            sorted_word = "".join(sorted(word))

            # If the sorted word is not in the dictionary, add it with the word as the value
            if sorted_word not in anagrams:
                anagrams[sorted_word] = [word]
            # If the sorted word is in the dictionary, add the word to the list of values
            else:
                anagrams[sorted_word].append(word)
        # Return the values of the dictionary as a list of lists
        return list(anagrams.values())

# Test the function
print(Solution().groupAnagrams(["eat","tea","tan","ate","nat","bat"]))
print(Solution().groupAnagrams([""]))
print(Solution().groupAnagrams(["a"]))

# Time complexity: O(nlogn)
# Space complexity: O(n)
# Runtime: 128 ms, faster than 95.75% of Python3 online submissions for Group Anagrams.
# Memory Usage: 17.1 MB, less than 96.00% of Python3 online submissions for Group Anagrams.

