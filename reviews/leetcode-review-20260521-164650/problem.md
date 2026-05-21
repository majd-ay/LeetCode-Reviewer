# Problem

Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

# My Solution

```cpp
class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        unordered_map<int, int> mp;

        for (int i = 0; i < nums.size(); i++) {
            int need = target - nums[i];

            if (mp.count(need)) {
                return {mp[need], i};
            }

            mp[nums[i]] = i;
        }

        return {};
    }
};
