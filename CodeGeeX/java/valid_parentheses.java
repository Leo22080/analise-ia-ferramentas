/*Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.
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
*/

class Solution {
    public boolean isValid(String s) {
        // Create a dictionary to store the matching pairs of parentheses
        Map<Character, Character> parenthesesMap = new HashMap<>();
        parenthesesMap.put('(', ')');
        parenthesesMap.put('[', ']');
        parenthesesMap.put('{', '}');
        
        // Create a stack to store the opening parentheses
        Stack<Character> stack = new Stack<>();
        
        // Iterate through the string
        for (char c : s.toCharArray()) {
            // If the character is an opening parenthesis, push it onto the stack
            if (parenthesesMap.containsKey(c)) {
                stack.push(c);
            } else {
                // If the character is a closing parenthesis, check if it matches the top of the stack
                if (stack.isEmpty() || parenthesesMap.get(stack.pop()) != c) {
                    return false;
                }
            }
        }

        // If the stack is empty, all parentheses have been matched
        return stack.isEmpty();
    }
}