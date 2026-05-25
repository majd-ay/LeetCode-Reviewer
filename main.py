import re
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors

REVIEW_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
]
QA_MODELS = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
]
TEST_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
]
MAX_RETRIES = 3
FEEDBACK_ERROR_MESSAGE = "Could not generate feedback due to a temporary API error."
CLARIFICATION_ERROR_MESSAGE = (
    "Could not generate a clarification answer due to a temporary API error."
)
QA_ERROR_MESSAGE = "Q&A could not be generated due to a temporary API error."
DEFAULT_QUESTION_COUNT = 3
DEFAULT_TEST_COUNT = 5
MAX_TEST_COUNT = 10
GENERATED_TEST_NOTE = (
    "These tests were generated automatically and should be reviewed if they fail."
)
YES_ANSWERS = {"y", "yes"}
NO_ANSWERS = {"n", "no"}


def read_text_file(path: str | Path) -> str:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return file_path.read_text(encoding="utf-8")


def write_text_file(path: str | Path, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8")


def generate_text(
    client: genai.Client,
    models: list[str],
    contents: str,
    purpose: str,
) -> str:
    errors_by_model = []
    for index, model in enumerate(models):
        print(f"Calling Gemini model: {model} for {purpose}...")

        try:
            return generate_text_with_retries(client, model, contents)
        except Exception as e:
            error_message = f"{model}: {type(e).__name__}: {e}"
            errors_by_model.append(error_message)

            if index < len(models) - 1:
                print(f"Model {model} failed. Trying fallback: {models[index + 1]}...")
            else:
                print(f"Model {model} failed. No fallback left.")

    raise RuntimeError(
        f"All models failed for {purpose}:\n" + "\n\n".join(errors_by_model)
    )


def generate_text_with_retries(
    client: genai.Client,
    model: str,
    contents: str,
) -> str:
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(model=model, contents=contents)
            return (response.text or "").strip()
        except errors.ServerError:
            if attempt == MAX_RETRIES:
                raise

            wait_seconds = 2**attempt
            print(f"Temporary API error. Retrying in {wait_seconds} seconds...")
            time.sleep(wait_seconds)


def build_review_input(prompt: str, solution_text: str) -> str:
    return f"""
{prompt}

Here is the user's problem and solution:

{solution_text}
""".strip()


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "problem"


def extract_problem_name(solution_text: str) -> str | None:
    generic_titles = {"problem", "my solution", "solution"}

    for line in solution_text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if not match:
            continue

        title = match.group(1).strip()
        if title.lower() not in generic_titles:
            return title

        return None

    return None


def fallback_slug() -> str:
    return datetime.now().strftime("leetcode-review-%Y%m%d-%H%M%S")


def create_review_folder(slug: str) -> Path:
    folder = Path("reviews") / slug
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def extract_cpp_solution_code(solution_text: str) -> str | None:
    fenced_match = re.search(
        r"```(?:cpp|c\+\+)\s*\n(.*?)```",
        solution_text,
        re.DOTALL | re.IGNORECASE,
    )
    if fenced_match:
        return fenced_match.group(1).strip()

    heading_match = re.search(
        r"^#\s+My Solution\s*$",
        solution_text,
        re.MULTILINE | re.IGNORECASE,
    )
    if not heading_match:
        return None

    fallback_code = solution_text[heading_match.end() :].strip()
    return fallback_code or None


def build_compile_main(cpp_code: str) -> str:
    return f"""#include <bits/stdc++.h>
using namespace std;

{cpp_code}

int main() {{
    return 0;
}}
"""


def format_compile_result(stdout: str, stderr: str, exit_code: int | str) -> str:
    return f"""Command: g++ -std=c++17 -Wall -Wextra -pedantic -fsyntax-only main.cpp
Exit code: {exit_code}

STDOUT:
{stdout}

STDERR:
{stderr}
"""


def strip_code_fence(text: str) -> str:
    match = re.search(
        r"^\s*```(?:cpp|c\+\+|C\+\+)?\s*\n(.*?)\n```\s*$",
        text,
        re.DOTALL,
    )
    if match:
        return match.group(1).strip()

    return text.strip()


def build_test_generation_input(solution_text: str, test_count: int) -> str:
    return f"""
Generate a complete self-contained C++17 test harness for this LeetCode problem and solution.

Rules:
- Return only C++ code, with no Markdown fences or explanation.
- Include #include <bits/stdc++.h> and using namespace std;.
- Include any required LeetCode helper structs/classes, such as ListNode or TreeNode, if needed.
- Include the user's Solution class/code from the input below.
- Include helper functions for building/comparing linked lists or trees if needed.
- Include int main().
- Include exactly {test_count} meaningful tests.
- Print clear cout output for passed/failed tests.
- Exit with code 0 only if every generated test passes.
- Do not review or critique the solution.

Problem and solution:
{solution_text}
""".strip()


def parse_test_count(test_count_input: str) -> int:
    try:
        test_count = int(test_count_input) if test_count_input else DEFAULT_TEST_COUNT
    except ValueError:
        test_count = DEFAULT_TEST_COUNT

    return max(1, min(MAX_TEST_COUNT, test_count))


def format_test_result(
    compile_stdout: str,
    compile_stderr: str,
    compile_exit_code: int | str,
    run_stdout: str = "",
    run_stderr: str = "",
    run_exit_code: int | str = "not run",
) -> str:
    return f"""{GENERATED_TEST_NOTE}

Compile command: g++ -std=c++17 -Wall -Wextra -pedantic test_main.cpp -o test_runner.exe
Compile exit code: {compile_exit_code}

Compile STDOUT:
{compile_stdout}

Compile STDERR:
{compile_stderr}

Run command: test_runner.exe
Run exit code: {run_exit_code}

Run STDOUT:
{run_stdout}

Run STDERR:
{run_stderr}
"""


def run_cpp_compile_check(solution_text: str, review_folder: Path) -> bool:
    compile_folder = review_folder / "compile"
    compile_folder.mkdir(parents=True, exist_ok=True)
    result_path = compile_folder / "compile_result.txt"

    cpp_code = extract_cpp_solution_code(solution_text)
    if cpp_code is None:
        message = "No C++ solution code found in input.md, so the compile check was skipped."
        write_text_file(result_path, message + "\n")
        print(message)
        return False

    write_text_file(compile_folder / "main.cpp", build_compile_main(cpp_code))

    if shutil.which("g++") is None:
        message = "C++ compile check skipped because g++ was not found on this system."
        write_text_file(result_path, message + "\n")
        print(message)
        return False

    command = [
        "g++",
        "-std=c++17",
        "-Wall",
        "-Wextra",
        "-pedantic",
        "-fsyntax-only",
        "main.cpp",
    ]
    try:
        result = subprocess.run(
            command,
            cwd=compile_folder,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        message = "C++ compile check skipped because g++ was not found on this system."
        write_text_file(result_path, message + "\n")
        print(message)
        return False
    write_text_file(
        result_path,
        format_compile_result(result.stdout, result.stderr, result.returncode),
    )

    if result.returncode == 0:
        print(f"C++ compile check passed. Results saved to {result_path}")
        return True
    else:
        print(f"C++ compile check found syntax issues. Results saved to {result_path}")
        return False


def run_generated_cpp_tests(
    client: genai.Client,
    solution_text: str,
    review_folder: Path,
    test_count: int,
) -> None:
    tests_folder = review_folder / "tests"
    tests_folder.mkdir(parents=True, exist_ok=True)
    test_main_path = tests_folder / "test_main.cpp"
    result_path = tests_folder / "test_result.txt"

    try:
        test_harness = generate_text(
            client,
            TEST_MODELS,
            build_test_generation_input(solution_text, test_count),
            "Generating C++ tests",
        )
    except Exception as e:
        message = "Could not generate C++ tests because the model is unavailable."
        write_text_file(result_path, f"{GENERATED_TEST_NOTE}\n\n{message}\nReason: {e}\n")
        print(message)
        print(f"Reason: {e}")
        return

    write_text_file(test_main_path, strip_code_fence(test_harness))

    if shutil.which("g++") is None:
        message = "Generated C++ tests could not run because g++ was not found."
        write_text_file(result_path, f"{GENERATED_TEST_NOTE}\n\n{message}\n")
        print(message)
        return

    compile_command = [
        "g++",
        "-std=c++17",
        "-Wall",
        "-Wextra",
        "-pedantic",
        "test_main.cpp",
        "-o",
        "test_runner.exe",
    ]
    try:
        compile_result = subprocess.run(
            compile_command,
            cwd=tests_folder,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        message = "Generated C++ tests could not run because g++ was not found."
        write_text_file(result_path, f"{GENERATED_TEST_NOTE}\n\n{message}\n")
        print(message)
        return

    if compile_result.returncode != 0:
        write_text_file(
            result_path,
            format_test_result(
                compile_result.stdout,
                compile_result.stderr,
                compile_result.returncode,
            ),
        )
        print(f"Generated C++ tests failed to compile. Results saved to {result_path}")
        return

    runner_path = (tests_folder / "test_runner.exe").resolve()
    run_result = subprocess.run(
        [str(runner_path)],
        cwd=tests_folder,
        capture_output=True,
        text=True,
        check=False,
    )
    write_text_file(
        result_path,
        format_test_result(
            compile_result.stdout,
            compile_result.stderr,
            compile_result.returncode,
            run_result.stdout,
            run_result.stderr,
            run_result.returncode,
        ),
    )

    if run_result.returncode == 0:
        print(f"Generated C++ tests passed. Results saved to {result_path}")
    else:
        print(f"Generated C++ tests failed. Results saved to {result_path}")


def build_questions_input(solution_text: str, question_count: int) -> str:
    return f"""
You are a software engineering interviewer.
Write exactly {question_count} concise interview follow-up questions based on this problem and solution.
Return one question per line with no numbering or extra text.

{solution_text}
""".strip()


def parse_questions(text: str, question_count: int) -> list[str]:
    questions = []

    for line in text.splitlines():
        question = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", line).strip()
        if question:
            questions.append(question)

    return questions[:question_count]

def build_feedback_input(solution_text: str, question: str, answer: str) -> str:
    return f"""
You are a software engineering interviewer giving feedback directly to the person who answered.

Evaluate the answer to the follow-up question below.

Style rules:
- Write directly to the person using "you" and "your answer".
- Do not say "the candidate", "the user", "they", or "their answer".
- Do not write as if the answer is yours.
- Keep the tone direct, professional, and consistent.
- Give concise feedback in 2 to 4 sentences.

Content rules:
- Mention what the answer got right.
- Mention what was missing or inaccurate.
- Mention one improvement if useful.

Problem and solution:
{solution_text}

Follow-up question:
{question}

Answer to evaluate:
{answer}

Feedback:
""".strip()


def build_clarification_input(
    solution_text: str,
    question: str,
    answer: str,
    feedback: str,
    clarification: str,
) -> str:
    return f"""
You are a software engineering interviewer answering a clarification directly.

Style rules:
- Use "you" and "your answer".
- Do not say "the candidate", "the user", or "they".
- Keep the answer practical and focused.
- Use 2 to 5 sentences.

Problem and solution:
{solution_text}

Follow-up question:
{question}

User answer:
{answer}

Feedback already given:
{feedback}

Clarification question:
{clarification}

Clarification answer:
""".strip()


def format_qa_entry(index: int, question: str, answer: str, feedback: str) -> str:
    return f"""
## Question {index}

{question}

### User Answer

{answer}

### Feedback

{feedback}
""".strip()


def format_clarification_entry(index: int, question: str, answer: str) -> str:
    return f"""
### Clarification {index}

{question}

#### Answer

{answer}
""".strip()


def write_qa_file(qa_path: Path, entries: list[str]) -> None:
    write_text_file(qa_path, "# Interview Q&A\n\n" + "\n\n".join(entries) + "\n")


def run_qa_session(client: genai.Client, solution_text: str, qa_path: Path, question_count: int) -> None:
    try:
        questions = parse_questions(
            generate_text(
                client,
                QA_MODELS,
                build_questions_input(solution_text, question_count),
                "Q&A session: questions generation",
            ),
            question_count,
        )
    except Exception as e:
        print("Could not start Q&A because the model is temporarily unavailable.")
        print(f"Reason: {e}")
        write_qa_file(qa_path, [QA_ERROR_MESSAGE])
        return

    entries = []

    print()
    print("Interview follow-up Q&A")

    for index, question in enumerate(questions, start=1):
        print()
        print(f"Question {index}: {question}")
        answer = input("Your answer: ").strip()

        try:
            feedback = generate_text(
                client,
                QA_MODELS,
                build_feedback_input(solution_text, question, answer),
                "Q&A session: reviewing follow-up question",
            )
        except Exception as e:
            print("Could not start Q&A because the model is temporarily unavailable.")
            print(f"Reason: {e}")
            feedback = FEEDBACK_ERROR_MESSAGE

        print()
        print("Feedback:")
        print(feedback)

        entries.append(format_qa_entry(index, question, answer, feedback))
        write_qa_file(qa_path, entries)
        run_clarification_rounds(
            client,
            solution_text,
            question,
            answer,
            feedback,
            entries,
            qa_path,
        )

    write_qa_file(qa_path, entries)


def run_clarification_rounds(
    client: genai.Client,
    solution_text: str,
    question: str,
    answer: str,
    feedback: str,
    entries: list[str],
    qa_path: Path,
) -> None:
    for clarification_index in range(1, 3):
        clarification = input(
            "Do you have a follow-up question or clarification? "
            "Press Enter to continue. "
        ).strip()
        if not clarification:
            return

        try:
            clarification_answer = generate_text(
                client,
                QA_MODELS,
                build_clarification_input(
                    solution_text,
                    question,
                    answer,
                    feedback,
                    clarification,
                ),
                "Q&A session: answering clarification",
            )
        except Exception as e:
            print("Could not answer the clarification because the model is unavailable.")
            print(f"Reason: {e}")
            clarification_answer = CLARIFICATION_ERROR_MESSAGE

        print()
        print("Clarification answer:")
        print(clarification_answer)

        entries[-1] += "\n\n" + format_clarification_entry(
            clarification_index,
            clarification,
            clarification_answer,
        )
        write_qa_file(qa_path, entries)


def main() -> None:
    load_dotenv()

    prompt = read_text_file("reviewer_prompt.txt")
    solution_text = read_text_file("input.md")

    client = genai.Client()
    problem_name = extract_problem_name(solution_text)
    review_slug = slugify(problem_name) if problem_name else fallback_slug()
    review_folder = create_review_folder(review_slug)

    write_text_file(review_folder / "problem.md", solution_text)

    generate_review = input("Generate Gemini review? [Y/n]: ").strip().lower()

    if generate_review in NO_ANSWERS:
        print("Skipping Gemini review.")
    else:
        try:
            review = generate_text(
                client,
                REVIEW_MODELS,
                build_review_input(prompt, solution_text),
                "Reviewing solution",
            )
        except Exception as e:
            print("Could not generate the review because the model is unavailable.")
            print(f"Reason: {e}")
            return

        write_text_file(review_folder / "review.md", review)

        print(f"Review saved to {review_folder / 'review.md'}")
        print()
        print(review)

    run_compile_check = input("Run C++ compile check? [y/N]: ").strip().lower()

    if run_compile_check in YES_ANSWERS:
        compile_passed = run_cpp_compile_check(solution_text, review_folder)
    else:
        compile_passed = False
        print("Skipping C++ compile check.")

    if compile_passed:
        run_generated_tests = input("Run generated C++ tests? [y/N]: ").strip().lower()
        if run_generated_tests in YES_ANSWERS:
            test_count_input = input(
                f"How many tests? [default {DEFAULT_TEST_COUNT}, max {MAX_TEST_COUNT}]: "
            ).strip()
            test_count = parse_test_count(test_count_input)
            run_generated_cpp_tests(client, solution_text, review_folder, test_count)
        else:
            print("Skipping generated C++ tests.")

    start_interactive_qa = input("Start interactive Q&A? [y/N]: ").strip().lower()

    if start_interactive_qa not in YES_ANSWERS:
        print("Skipping interactive Q&A.")
        return
    question_count_input = input(
        f"How many questions? [default {DEFAULT_QUESTION_COUNT}]: "
    ).strip()

    if question_count_input:
        try:
            question_count = int(question_count_input)
        except ValueError:
            print(f"Invalid number. Using default: {DEFAULT_QUESTION_COUNT}")
            question_count = DEFAULT_QUESTION_COUNT
    else:
        question_count = DEFAULT_QUESTION_COUNT
    run_qa_session(client, solution_text, review_folder / "qa.md", question_count)
    print()
    print(f"Q&A saved to {review_folder / 'qa.md'}")


if __name__ == "__main__":
    main()
