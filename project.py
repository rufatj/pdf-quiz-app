import os
import json
from pypdf import PdfReader
from groq import Groq


def main():
    print("PDF Quiz App")
    print("------------")
    print("upload a pdf, get questions, see your score")
    print()

    start=input("ready to start? (y/n): ").strip().lower()
    if start!="y":
        print("ok, bye")
        return

    path=input("enter pdf file path: ").strip()
    text=extract_text_from_pdf(path)
    if not text:
        print("could not read this pdf, please check the path")
        return

    print(f"pdf loaded, {len(text)} characters of text found")
    choice=input("how many questions do you want? (5/10/20): ").strip()
    count=validate_question_count(choice)
    print(f"ok, preparing {count} questions for you...")

    raw=generate_questions(text, count)
    questions=parse_ai_response(raw)

    if not questions:
        print("something went wrong, could not generate questions")
        return

    correct=0
    wrong=0
    for i, q in enumerate(questions, start=1):
        print()
        print(f"Q{i}. {q['question']}")
        for letter in ["A", "B", "C", "D"]:
            if letter in q["options"]:
                print(f"  {letter}) {q['options'][letter]}")

        answer=input("your answer (A/B/C/D): ").strip().upper()
        if answer==q["answer"]:
            print("correct")
            correct+=1
        else:
            right=q["answer"]
            print(f"wrong, correct answer was {right}) {q['options'][right]}")
            wrong+=1

    score=calculate_score(correct, wrong)
    print()
    print("--- result ---")
    print(f"correct: {correct}")
    print(f"wrong: {wrong}")
    print(f"final score: {score}")

    again=input("try another pdf? (y/n): ").strip().lower()
    if again=="y":
        main()


def extract_text_from_pdf(path):
    if not os.path.exists(path):
        return ""
    if not path.lower().endswith(".pdf"):
        return ""
    try:
        reader=PdfReader(path)
        text=""
        for page in reader.pages:
            piece=page.extract_text()
            if piece:
                text+=piece+"\n"
        return text.strip()
    except Exception:
        return ""


def validate_question_count(user_input):
    allowed=[5, 10, 20]
    try:
        n=int(user_input)
    except (ValueError, TypeError):
        return 5
    if n in allowed:
        return n
    return 5


def generate_questions(text, count):
    api_key=os.environ.get("GROQ_API_KEY")
    if not api_key:
        return ""

    # if pdf is huge, cut it so we dont send too much to the api
    if len(text)>8000:
        text=text[:8000]

    prompt=(
        f"you are a teacher. read the text below and write exactly {count} "
        "multiple choice questions from it. each question must have 4 options "
        "labeled A, B, C, D and one correct answer. "
        "return only a json array, no extra words, no markdown. "
        "use this format:\n"
        '[{"question": "...", "options": {"A": "...", "B": "...", "C": "...", "D": "..."}, "answer": "A"}]\n\n'
        f"text:\n{text}"
    )

    try:
        client=Groq(api_key=api_key)
        response=client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return response.choices[0].message.content
    except Exception:
        return ""


def parse_ai_response(raw_text):
    if not raw_text:
        return []

    cleaned=raw_text.strip()

    # sometimes the model wraps it in ```json ... ``` even though we asked not to
    if cleaned.startswith("```"):
        lines=cleaned.split("\n")
        if len(lines)>2:
            cleaned="\n".join(lines[1:-1])

    # grab the first [ ... ] block
    start=cleaned.find("[")
    end=cleaned.rfind("]")
    if start==-1 or end==-1 or end<start:
        return []

    try:
        data=json.loads(cleaned[start:end+1])
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    result=[]
    for q in data:
        if not isinstance(q, dict):
            continue
        if "question" not in q or "options" not in q or "answer" not in q:
            continue
        if not isinstance(q["options"], dict):
            continue
        if q["answer"] not in q["options"]:
            continue
        result.append(q)
    return result


def calculate_score(correct, wrong):
    return correct-(wrong*0.5)


if __name__=="__main__":
    main()
