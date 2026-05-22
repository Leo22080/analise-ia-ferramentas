"""
Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.
An input string is valid if:
Open brackets must be closed by the same type of brackets.
Open brackets must be closed in the correct order.
Every close bracket has a corresponding open bracket of the same type.
 

Example 1:

Input: s = "()"
Output: true
Example 2:

Input: s = "()[]{}"
Output: true
Example 3:

Input: s = "(]"
Output: false
 

Constraints:

1 <= s.length <= 104
s consists of parentheses only '()[]{}'.
class Solution:
    def isValid(self, s: str) -> bool:
"""

class Solution:
    def isValid(self, s: str) -> bool:
        # Create a dictionary to store the matching pairs of parentheses
        matching_pairs = {')': '(', '}': '{', ']': '['}
        
        # Create a stack to store the opening parentheses
        stack = []
        
        # Iterate through each character in the string
        for char in s:
            # If the character is an opening parenthesis, push it onto the stack
            if char in matching_pairs.values():
                stack.append(char)
            # If the character is a closing parenthesis, check if the stack is empty
            # or if the top of the stack does not match the matching pair
            elif not stack or stack.pop() != matching_pairs[char]:
                return False

        # If the stack is empty, all parentheses have been matched
        return not stack
# Time complexity: O(n), where n is the length of the string