/*
Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.

Implement the LRUCache class:

LRUCache(int capacity) Initialize the LRU cache with positive size capacity.
int get(int key) Return the value of the key if the key exists, otherwise return -1.
void put(int key, int value) Update the value of the key if the key exists. Otherwise, add the key-value pair to the cache. If the number of keys exceeds the capacity from this operation, evict the least recently used key.
The functions get and put must each run in O(1) average time complexity.

 

Example 1:

Input
["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]
[[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]
Output
[null, null, null, 1, null, -1, null, -1, 3, 4]

Explanation
LRUCache lRUCache = new LRUCache(2);
lRUCache.put(1, 1); // cache is {1=1}
lRUCache.put(2, 2); // cache is {1=1, 2=2}
lRUCache.get(1);    // return 1
lRUCache.put(3, 3); // LRU key was 2, evicts key 2, cache is {1=1, 3=3}
lRUCache.get(2);    // returns -1 (not found)
lRUCache.put(4, 4); // LRU key was 1, evicts key 1, cache is {4=4, 3=3}
lRUCache.get(1);    // return -1 (not found)
lRUCache.get(3);    // return 3
lRUCache.get(4);    // return 4
 

Constraints:

1 <= capacity <= 3000
0 <= key <= 104
0 <= value <= 105
At most 2 * 105 calls will be made to get and put.

class LRUCache {
public:
    LRUCache(int capacity) {
        
    }
    
    int get(int key) {
        
    }
    
    void put(int key, int value) {
        
    }
};

/**
 * Your LRUCache object will be instantiated and called as such:
 * LRUCache* obj = new LRUCache(capacity);
 * int param_1 = obj->get(key);
 * obj->put(key,value);
*/


#include <unordered_map>
#include <list>

class LRUCache {
private:
    // 缓存的最大容量
    int cap;
    // 哈希表：key 映射到 list 中的迭代器（节点位置）
    std::unordered_map<int, std::list<std::pair<int, int>>::iterator> cache;
    // 双向链表：存储 {key, value} 对，头部是最近使用的，尾部是最久未使用的
    std::list<std::pair<int, int>> lru_list;

public:
    // 初始化 LRU 缓存
    LRUCache(int capacity) {
        this->cap = capacity;
    }
    
    // 获取键值
    int get(int key) {
        // 如果 key 不在哈希表中，返回 -1
        if (cache.find(key) == cache.end()) {
            return -1;
        }
        
        // key 存在，获取该节点在链表中的迭代器
        auto it = cache[key];
        int value = it->second;
        
        // 将该节点移到链表头部，表示最近被访问过
        lru_list.splice(lru_list.begin(), lru_list, it);
        
        // 更新哈希表中的迭代器（splice 操作不会改变迭代器本身指向的节点，但为了逻辑严谨和某些编译器的安全考量，可以重新赋值，实际上此处 it 依然有效）
        cache[key] = lru_list.begin();
        
        return value;
    }
    
    // 插入/更新键值对
    void put(int key, int value) {
        // 1. 如果 key 已经存在
        if (cache.find(key) != cache.end()) {
            // 获取迭代器，更新链表节点中的 value
            auto it = cache[key];
            it->second = value;
            // 移动到链表头部，表示最近被访问过
            lru_list.splice(lru_list.begin(), lru_list, it);
            cache[key] = lru_list.begin();
            return;
        }
        
        // 2. 如果 key 不存在，需要新增节点
        // 检查是否超出容量
        if (lru_list.size() == cap) {
            // 超出容量，删除链表尾部节点（最久未使用）
            auto last_it = lru_list.end();
            last_it--; // end() 指向尾后元素，需要减一才是最后一个元素
            int old_key = last_it->first;
            
            // 从哈希表中删除该 key
            cache.erase(old_key);
            // 从链表中删除该尾部节点
            lru_list.pop_back();
        }
        
        // 将新节点插入链表头部
        lru_list.push_front({key, value});
        // 在哈希表中记录 key 和新节点的迭代器
        cache[key] = lru_list.begin();
    }
};

/**
 * Your LRUCache object will be instantiated and called as such:
 * LRUCache* obj = new LRUCache(capacity);
 * int param_1 = obj->get(key);
 * obj->put(key,value);
 */
