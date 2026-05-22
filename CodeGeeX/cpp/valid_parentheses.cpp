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

class Solution {
public:
    bool isValid(string s) {
        
    }
};
*/

#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    bool isValid(string s) {
        stack<char> st;
        
        for (char c : s) {
            // 如果是左括号，将对应的右括号入栈
            if (c == '(') {
                st.push(')');
            } else if (c == '{') {
                st.push('}');
            } else if (c == '[') {
                st.push(']');
            } else {
                // 如果是右括号，检查栈是否为空，或者栈顶元素是否与当前右括号匹配
                if (st.empty() || st.top() != c) {
                    return false;
                }
                // 匹配成功，弹出栈顶元素
                st.pop();
            }
        }
        
        // 如果栈为空，说明所有括号都完全匹配
        return st.empty();
    }
};



/*  
Time Complexity: O(n) where n is the length of the string s. We traverse the string s once.

Space Complexity: O(n) where n is the length of the string s. In the worst case, we have to push all opening brackets onto the stack. The stack will have at most n elements.
*/
