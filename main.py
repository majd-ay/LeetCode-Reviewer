from pathlib import Path

from dotenv import load_dotenv
from google import genai


def read_text_file(path: str) -> str:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return file_path.read_text(encoding="utf-8")


def write_text_file(path: str, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8")


def build_input(prompt: str, solution_text: str) -> str:
    return f"""
{prompt}

Here is the user's problem and solution:

{solution_text}
""".strip()


def main() -> None:
    load_dotenv()

    prompt = read_text_file("reviewer_prompt.txt")
    solution_text = read_text_file("input.md")

    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=build_input(prompt, solution_text),
    )

    review = response.text or ""

    write_text_file("review.md", review)

    print("Review saved to review.md")
    print()
    print(review)


if __name__ == "__main__":
    main()
