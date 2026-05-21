# Interview Q&A

## Question 1

Can you explain the role of the `prev` pointer in your solution?

### User Answer

The role is to concatenate the newly inverted pair to the end of processed list

### Feedback

Your answer correctly identifies that the `prev` pointer is used for concatenation. It's crucial for linking the swapped pair back to the preceding portion of the list. To be more precise, it specifically connects the tail of the *previous* swapped pair (which becomes the new `prev` after each swap) to the head of the *current* swapped pair.

## Question 2

What would be the time and space complexity of this approach?

### User Answer

O(N) time because I process each node exactly once, more accurately each pair (0, 1), (2, 3), (4, 5), etc. is processed once. and O(1) space because I have only a constant number of temp nodes used.

### Feedback

Your answer correctly identifies the time complexity as O(N) and accurately explains why by stating that each node is processed once. You also correctly identify the space complexity as O(1). To further improve your explanation, you could explicitly mention that the constant number of temporary variables like `curr`, `prev`, and `next` contribute to the O(1) space complexity.

### Clarification 1

nope

#### Answer

That's a good explanation! For the space complexity, you're right that it's O(1) because you're only using a few extra variables. Explicitly mentioning `curr`, `prev`, and `next` as those constant temporary variables would make your reasoning even clearer.

## Question 3

How would you handle an odd number of nodes in the linked list with this code?

### User Answer

it's already handled, because the loop condition checks the existence of curr node and its following one, and if the list is of an odd number of nodes, I'll invert all pairs and the remaining last node will stay as is and connected to the inverted last pair.

### Feedback

Could not generate feedback due to a temporary API error.
