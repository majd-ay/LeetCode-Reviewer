import re
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors

MODEL = "gemini-2.5-flash"
MAX_RETRIES = 3
FEEDBACK_ERROR_MESSAGE = "Could not generate feedback due to a temporary API error."
QA_ERROR_MESSAGE = "Q&A could not be generated due to a temporary API error."


def read_text_file(path: str | Path) -> str:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return file_path.read_text(encoding="utf-8")


def write_text_file(path: str | Path, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8")


def generate_text(client: genai.Client, contents: str) -> str:
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(model=MODEL, contents=contents)
            return (response.text or "").strip()
        except errors.ServerError:
            if attempt == MAX_RETRIES:
                raise

            time.sleep(2**attempt)


def build_review_input(prompt: str, solution_text: str) -> str:
    return f"""
{prompt}

Here is the user's problem and solution:

{solution_text}
""".strip()


def build_problem_name_input(solution_text: str) -> str:
    return f"""
Extract the LeetCode problem name from the text below.
Return only the problem name.
If the name is not explicit, return a short likely name based on the problem statement.

{solution_text}
""".strip()


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "problem"


def create_review_folder(slug: str) -> Path:
    folder = Path("reviews") / slug
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def build_questions_input(solution_text: str) -> str:
    return f"""
You are a software engineering interviewer.
Write exactly 3 concise interview follow-up questions based on this problem and solution.
Return one question per line with no numbering or extra text.

{solution_text}
""".strip()


def parse_questions(text: str) -> list[str]:
    questions = []

    for line in text.splitlines():
        question = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", line).strip()
        if question:
            questions.append(question)

    return questions[:3]


def build_feedback_input(solution_text: str, question: str, answer: str) -> str:
    return f"""
You are a software engineering interviewer.
Evaluate the candidate's answer to the follow-up question below.
Give concise feedback in 2 to 4 sentences.
Mention what was correct, what was missing or inaccurate, and one improvement if useful.

Problem and solution:
{solution_text}

Question:
{question}

Candidate answer:
{answer}
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


def write_qa_file(qa_path: Path, entries: list[str]) -> None:
    write_text_file(qa_path, "# Interview Q&A\n\n" + "\n\n".join(entries) + "\n")


def run_qa_session(client: genai.Client, solution_text: str, qa_path: Path) -> None:
    try:
        questions = parse_questions(
            generate_text(client, build_questions_input(solution_text))
        )
    except errors.APIError:
        print("Could not start Q&A because the model is temporarily unavailable.")
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
                build_feedback_input(solution_text, question, answer),
            )
        except errors.APIError:
            feedback = FEEDBACK_ERROR_MESSAGE

        print()
        print("Feedback:")
        print(feedback)

        entries.append(format_qa_entry(index, question, answer, feedback))
        write_qa_file(qa_path, entries)

    write_qa_file(qa_path, entries)


def main() -> None:
    load_dotenv()

    prompt = read_text_file("reviewer_prompt.txt")
    solution_text = read_text_file("input.md")

    client = genai.Client()
    try:
        problem_name = generate_text(client, build_problem_name_input(solution_text))
    except errors.APIError:
        print("Could not determine the problem name because the model is unavailable.")
        return

    review_folder = create_review_folder(slugify(problem_name))

    write_text_file(review_folder / "problem.md", solution_text)

    try:
        review = generate_text(client, build_review_input(prompt, solution_text))
    except errors.APIError:
        print("Could not generate the review because the model is unavailable.")
        return

    write_text_file(review_folder / "review.md", review)

    print(f"Review saved to {review_folder / 'review.md'}")
    print()
    print(review)

    run_qa_session(client, solution_text, review_folder / "qa.md")
    print()
    print(f"Q&A saved to {review_folder / 'qa.md'}")


if __name__ == "__main__":
    main()
