````markdown
# LeetCode Reviewer Agent

A Python-based tool that automates the review of LeetCode-style programming solutions using Google's Generative AI (Gemini) and C++ compilation/testing utilities.

## Features

*   **Automated Code Review:** Generates detailed feedback on correctness, edge cases, time/space complexity, and code quality.
*   **AI-Powered Interview Feedback:** Provides direct feedback as if in a real interview.
*   **Improved Solution Generation:** Offers cleaner C++ code suggestions when beneficial.
*   **C++ Compilation Check:** Verifies the syntax of C++ solutions.
*   **Automated C++ Test Generation:** Creates and runs test cases for C++ solutions using AI.
*   **Structured Output:** Saves all review artifacts (reviews, test results, logs) into organized directories.

## Tech Stack

*   **Languages:** Python, C++
*   **Libraries:** `google-generativeai`, `python-dotenv`
*   **Tools:** `g++` (for C++ compilation/testing), `ruff` (linter, inferred)

## Project Structure

```
.
├── .env                  # Environment variables (e.g., API key)
├── .gitignore            # Git ignore rules
├── input.md              # Problem statement and user's solution
├── main.py               # Core review script
├── reviewer_prompt.txt   # Prompt for the AI review model
├── reviews/              # Directory for all review outputs
│   ├── leetcode-review-.../ # Specific review sessions
│   │   ├── problem.md
│   │   ├── qa.md
│   │   └── review.md
│   └── swap-nodes-in-pairs/ # Example review for a specific problem
│       ├── compile/
│       ├── problem.md
│       ├── qa.md
│       ├── review.md
│       └── tests/
└── .ruff_cache/          # Ruff linter cache
```

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd leet-code-reviewer-agent
    ```
2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    # Or manually:
    pip install google-generativeai python-dotenv
    ```
3.  **Obtain Google Generative AI API Key:** Get an API key from the Google AI Studio or Google Cloud Platform.
4.  **Configure API Key:** Create a `.env` file in the root directory and add your API key:
    ```env
    GOOGLE_API_KEY=YOUR_API_KEY_HERE
    ```
5.  **Install C++ Compiler:** Ensure `g++` is installed and accessible in your system's PATH.
    *   **Linux (Debian/Ubuntu):** `sudo apt update && sudo apt install build-essential`
    *   **macOS (with Homebrew):** `brew install gcc`
    *   **Windows:** Install MinGW-w64 or a similar C++ compiler.

## How to Run

1.  **Prepare Input:** Place your LeetCode problem statement and solution into `input.md`. For C++ solutions, ensure they are enclosed in fenced code blocks (e.g., ` ```cpp ... ``` `).
2.  **Execute the main script:**
    ```bash
    python main.py
    ```
3.  **View Results:** The script will process the input and generate detailed review reports, compilation checks, and test results in the `reviews/` directory. Each review session will be stored in a timestamped subfolder.

## Environment Variables

*   `GOOGLE_API_KEY`: Your API key for accessing Google's Generative AI models. **Required.**

## Usage Notes

*   The script primarily targets C++ solutions for compilation and testing. While the core review functionality might work for other languages, the C++ specific tooling will only apply to C++ code.
*   Ensure your `input.md` correctly formats the problem and solution for the best results.
*   The quality of AI-generated reviews and tests depends on the prompt and the capabilities of the chosen Gemini models.

## Limitations & TODOs

*   **Language Support:** Currently optimized for C++ for automated compilation and testing. Broader language support would require additional tooling and prompt adjustments.
*   **Interactive Q&A:** The interactive Q&A and feedback features are implied by model configurations but may require manual invocation or further development.
*   **Configuration:** Key parameters like API models and retry counts are hardcoded; command-line arguments or a config file could improve flexibility.
````
