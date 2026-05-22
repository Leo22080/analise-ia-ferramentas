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

#include <iostream>
#include <string>
#include <stack>
using namespace std;

class Solution {
public:
    bool isValid(string s) {
        stack<char> stack;
        for (char c : s) {
            if (c == '(' || c == '[' || c == '{') {
                stack.push(c);
            }
            else if (c == ')' || c == ']' || c == '}') {
                if (stack.empty()) {
                    return false;
                }
                char top = stack.top();
                stack.pop();
                if (c == ')' && top != '(') return false;
                else if (c == ']' && top != '[') return false;
                else if (c == '}' && top != '{') return false;
            }
        }
        return stack.empty();
    }
};  

int main() {
    Solution solution;
    string s = "()";
    bool result = solution.isValid(s);
    cout << result << endl;
    return 0;
}