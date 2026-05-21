# Interview Q&A

## Question 1

Can you explain the time and space complexity of your solution?

### User Answer

Time: The solution iterates over each element in the array at most once and does at most two hash map look-ups, so O(n) on average and O(n^2) in the worst case. Space: Each element of the array is inserted to the hash map at most once, so O(n).

### Feedback

Your explanation of the time complexity is mostly correct, with the correct average case of O(n) due to the hash map operations. However, the worst-case time complexity for an `unordered_map` is indeed O(n) for lookups and insertions, making the overall worst-case time complexity O(n^2). For space complexity, O(n) is accurate as you store each element in the hash map. An improvement would be to clarify that the worst-case for `unordered_map` arises from hash collisions, which are rare in practice.

## Question 2

What would happen if there were duplicate numbers in the input array?

### User Answer

the unordered_map will overwrite previous indexes (map values) of the previously inserted element values (map keys) with the most recent indexes of duplicate values, but this won't happen as we're returning the first pair found.

### Feedback

The candidate correctly identifies that the `unordered_map` would overwrite previous indices with more recent ones for duplicate numbers. They also correctly observe that this overwrite behavior doesn't impact the current solution's correctness because it returns the first valid pair found. However, they could further clarify that if the problem required finding *all* pairs, or a specific pair (e.g., with the smallest indices), the current overwrite behavior would be problematic.

## Question 3

How would you adapt this solution if you needed to find three numbers that sum to the target?

### User Answer

to add an inner loop for each element being examined to check for each element in the map their sum and then look for need = target - theirSum in the map

### Feedback

Your approach of adding an inner loop to check sums is a good starting point. However, this would lead to a cubic time complexity, which is less efficient. To improve, consider iterating through the array and for each element, solving the "two sum" problem for the remaining part of the array with an adjusted target. This would reduce the complexity to quadratic.
