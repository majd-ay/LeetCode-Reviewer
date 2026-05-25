#include <bits/stdc++.h>

using namespace std;

// Definition for singly-linked list.
struct ListNode {
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode *next) : val(x), next(next) {}
};

class Solution {
public:
    ListNode* swapPairs(ListNode* head) {
        ListNode* curr = head, *prev = nullptr;
        while (curr && curr->next) {
            auto* next = curr->next;
            curr->next = next->next;
            next->next = curr;
            if (!prev) {
                head = next;
            } else {
                prev->next = next;
            }
            prev = curr;
            curr = curr->next;
        }
        return head;
    }
};

// Helper function to build a linked list from a vector
ListNode* buildList(const vector<int>& vals) {
    if (vals.empty()) {
        return nullptr;
    }
    ListNode* head = new ListNode(vals[0]);
    ListNode* curr = head;
    for (size_t i = 1; i < vals.size(); ++i) {
        curr->next = new ListNode(vals[i]);
        curr = curr->next;
    }
    return head;
}

// Helper function to convert a linked list to a vector
vector<int> listToVector(ListNode* head) {
    vector<int> vals;
    ListNode* curr = head;
    while (curr) {
        vals.push_back(curr->val);
        curr = curr->next;
    }
    return vals;
}

// Helper function to delete a linked list
void deleteList(ListNode* head) {
    ListNode* curr = head;
    while (curr) {
        ListNode* temp = curr;
        curr = curr->next;
        delete temp;
    }
}

int main() {
    Solution sol;
    int test_count = 0;
    int passed_count = 0;

    // Test case 1: Standard case
    {
        test_count++;
        vector<int> input_vec = {1, 2, 3, 4};
        vector<int> expected_vec = {2, 1, 4, 3};
        ListNode* head = buildList(input_vec);
        ListNode* result_head = sol.swapPairs(head);
        vector<int> result_vec = listToVector(result_head);
        
        if (result_vec == expected_vec) {
            cout << "Test Case " << test_count << ": PASSED" << endl;
            passed_count++;
        } else {
            cout << "Test Case " << test_count << ": FAILED" << endl;
        }
        deleteList(result_head);
    }

    // Test case 2: Odd number of nodes
    {
        test_count++;
        vector<int> input_vec = {1, 2, 3};
        vector<int> expected_vec = {2, 1, 3};
        ListNode* head = buildList(input_vec);
        ListNode* result_head = sol.swapPairs(head);
        vector<int> result_vec = listToVector(result_head);

        if (result_vec == expected_vec) {
            cout << "Test Case " << test_count << ": PASSED" << endl;
            passed_count++;
        } else {
            cout << "Test Case " << test_count << ": FAILED" << endl;
        }
        deleteList(result_head);
    }

    // Test case 3: Empty list
    {
        test_count++;
        vector<int> input_vec = {};
        vector<int> expected_vec = {};
        ListNode* head = buildList(input_vec);
        ListNode* result_head = sol.swapPairs(head);
        vector<int> result_vec = listToVector(result_head);

        if (result_vec == expected_vec) {
            cout << "Test Case " << test_count << ": PASSED" << endl;
            passed_count++;
        } else {
            cout << "Test Case " << test_count << ": FAILED" << endl;
        }
        deleteList(result_head);
    }

    if (passed_count == test_count) {
        return 0;
    } else {
        return 1;
    }
}