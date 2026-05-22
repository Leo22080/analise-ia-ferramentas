"""
A transformation sequence from word beginWord to word endWord using a dictionary wordList is a sequence of words beginWord -> s1 -> s2 -> ... -> sk such that:

Every adjacent pair of words differs by a single letter.
Every si for 1 <= i <= k is in wordList. Note that beginWord does not need to be in wordList.
sk == endWord
Given two words, beginWord and endWord, and a dictionary wordList, return the number of words in the shortest transformation sequence from beginWord to endWord, or 0 if no such sequence exists.

 

Example 1:

Input: beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log","cog"]
Output: 5
Explanation: One shortest transformation sequence is "hit" -> "hot" -> "dot" -> "dog" -> cog", which is 5 words long.
Example 2:

Input: beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log"]
Output: 0
Explanation: The endWord "cog" is not in wordList, therefore there is no valid transformation sequence.
 

Constraints:

1 <= beginWord.length <= 10
endWord.length == beginWord.length
1 <= wordList.length <= 5000
wordList[i].length == beginWord.length
beginWord, endWord, and wordList[i] consist of lowercase English letters.
beginWord != endWord
All the words in wordList are unique.

class Solution:
    def ladderLength(self, beginWord: str, endWord: str, wordList: List[str]) -> int:
"""

from typing import List
from collections import deque, defaultdict

class Solution:
    def ladderLength(self, beginWord: str, endWord: str, wordList: List[str]) -> int:
        # If the endWord is not in the wordList, no valid sequence exists
        if endWord not in wordList:
            return 0

        # Since beginWord might not be in wordList, we add it to process its patterns
        if beginWord not in wordList:
            wordList.append(beginWord)

        # 1. Preprocessing: Build an adjacency dictionary using wildcard patterns
        # e.g., "hot" -> "*ot", "h*t", "ho*"
        # This allows O(1) lookups for neighboring words instead of O(N) iterations
        pattern_map = defaultdict(list)
        for word in wordList:
            for i in range(len(word)):
                pattern = word[:i] + "*" + word[i+1:]
                pattern_map[pattern].append(word)

        # 2. Initialize Bidirectional BFS
        # Queue for forward search (from beginWord)
        queue_begin = deque([beginWord])
        visited_begin = {beginWord: 1} # word -> level (sequence length)
        
        # Queue for backward search (from endWord)
        queue_end = deque([endWord])
        visited_end = {endWord: 1}

        def visit_node(queue: deque, visited: dict, other_visited: dict) -> int:
            """Helper function to process one level of BFS from one direction."""
            level_size = len(queue)
            for _ in range(level_size):
                current_word = queue.popleft()
                current_level = visited[current_word]

                # Check all wildcard patterns of the current word
                for i in range(len(current_word)):
                    pattern = current_word[:i] + "*" + current_word[i+1:]

                    # Find all adjacent words sharing this pattern
                    for neighbor in pattern_map[pattern]:
                        # If the neighbor has been visited from the opposite direction, 
                        # we have found the shortest path!
                        if neighbor in other_visited:
                            return current_level + other_visited[neighbor]
                        
                        # If the neighbor hasn't been visited from this direction, process it
                        if neighbor not in visited:
                            visited[neighbor] = current_level + 1
                            queue.append(neighbor)
            return 0

        # 3. Execute Bidirectional BFS
        while queue_begin and queue_end:
            # Always expand the smaller queue to balance the search
            if len(queue_begin) <= len(queue_end):
                result = visit_node(queue_begin, visited_begin, visited_end)
            else:
                result = visit_node(queue_end, visited_end, visited_begin)
            
            # If a connection is found between the two searches, return the result
            if result > 0:
                return result

        # Return 0 if no such sequence exists
        return 0


