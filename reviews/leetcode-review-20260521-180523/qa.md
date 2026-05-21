# Interview Q&A

## Question 1

How would you handle duplicate numbers in the input array?

### User Answer

I'd use a hash-map from int to a vector of ints (indices) so recent indeces do not overridw previous one, and then I'd create pairs from the list of indeces I find associated with the needed number if found

### Feedback

Your answer correctly identifies the need to store multiple indices for a given number, suggesting a map where values are lists of indices. This is a good direction for handling duplicates. However, your proposed solution for pairing the indices after finding the complement is a bit vague and could lead to incorrect or inefficient results. Consider detailing how you would iterate through the list of indices for the complement to ensure you find valid pairs without returning duplicate index pairs or returning the same index twice.

## Question 2

What is the time and space complexity of your solution and why?

### User Answer

O(n)

### Feedback

Your answer correctly identified the time complexity as O(n). However, you missed mentioning the space complexity and the reasoning behind both. Your solution uses a hash map, which contributes to the space complexity. Consider explaining how the single pass through the array leads to O(n) time and how the hash map's potential to store all elements results in O(n) space complexity.

## Question 3

Can you explain the trade-offs of using `unordered_map` versus a sorted array and two pointers?

### User Answer

The solution iterates through the `nums` array once. Each hash map operation (`count` and `[]` access/insertion) takes average O(1) time. Therefore, the total time complexity is O(n), where n is the number of elements in `nums`.

### Feedback

Your explanation of the time complexity for the `unordered_map` approach is accurate, highlighting the O(n) performance due to average O(1) hash map operations. However, your answer does not address the trade-offs of using `unordered_map` compared to a sorted array and two pointers. To improve, you should discuss the time and space complexity differences between both approaches, as well as any other relevant considerations like mutability of the input array.
