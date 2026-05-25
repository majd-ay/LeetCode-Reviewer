# Swap Nodes in Pairs

# Problem

Given a linked list, swap every two adjacent nodes and return its head. You must solve the problem without modifying the values in the list's nodes (i.e., only nodes themselves may be changed.)

Constraints:

The number of nodes in the list is in the range [0, 100].
0 <= Node.val <= 100

# My Solution


//  Definition for singly-linked list.
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