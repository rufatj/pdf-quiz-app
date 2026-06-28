# PDF Quiz App

#### Video Demo: <URL HERE>

#### Description:

This is my final project for CS50P. It is a command line program that takes a PDF file from the user, reads the text inside it, and then asks an AI model to create multiple choice questions based on what is in the PDF. The user can choose to be quizzed with 5, 10 or 20 questions. After every answer the program tells the user if they got it right or wrong, and at the end it shows a final score. Wrong answers cost half a point, so the user is not encouraged to just guess randomly.

The idea came from how I personally study. When I read long PDFs for my university classes, I sometimes wish I could just upload the file somewhere and immediately get tested on it to see if I actually understood it. So I built that.

#### Files in the project

**project.py** is the main file and contains all the logic. It has a `main` function which runs the program from start to end, plus four helper functions:

- `extract_text_from_pdf(path)` opens the PDF file using the `pypdf` library and returns all the text from every page as one big string. If the file does not exist, is not a PDF, or is broken in some way, it returns an empty string so the rest of the program can handle the error nicely instead of crashing.
- `validate_question_count(user_input)` takes whatever the user typed for the number of questions and makes sure it is either 5, 10 or 20. If they typed something invalid like "abc" or "100", the function quietly defaults to 5. I chose this approach instead of asking again in a loop because it makes the function easy to test with pytest.
- `generate_questions(text, count)` is the function that talks to the Groq API. It builds a prompt asking the model to write the requested number of multiple choice questions in a strict JSON format, then sends it and returns the raw response text. I am using Groq because it is free and very fast compared to other providers. The model I use is `llama-3.3-70b-versatile`. The PDF text is cut to 8000 characters before sending so I do not waste tokens on huge files.
- `parse_ai_response(raw_text)` takes the raw response from the AI and tries to extract a clean Python list of question dictionaries from it. Even though I told the model to return only JSON, sometimes it still wraps the answer in ```json``` code blocks or adds a sentence before and after. This function handles all those cases, and it also throws away any question that does not have all the required fields. This way the quiz never crashes if the model returns something slightly broken.
- `calculate_score(correct, wrong)` is the simplest function. It just returns `correct - (wrong * 0.5)`. I made it a separate function on purpose, even though the math is one line, because keeping it separate makes the rule easy to test and easy to change later if I want different scoring.

**test_project.py** contains pytest tests for the three required functions: `calculate_score`, `validate_question_count`, and `parse_ai_response`. I did not test `generate_questions` because it makes a real network call and the response is different every time, which would make tests unreliable. For `parse_ai_response` I included several tricky cases: clean JSON, JSON wrapped in markdown code blocks, JSON with extra text around it, completely broken input, and questions with missing or invalid fields.

**requirements.txt** lists the three pip packages the project depends on: `pypdf` for reading PDFs, `groq` for calling the Groq API, and `pytest` for running the tests.

#### Design choices

I thought about building a graphical interface with Tkinter, but I decided to keep it in the terminal. The CS50P course focuses on Python fundamentals, not GUI design, so I wanted the project to show off clean code and good function design instead of fancy widgets.

I also debated whether to support other AI providers (OpenAI, Anthropic, etc.) but in the end I picked just Groq to keep the code simple and the dependency list short. Adding more providers would not really teach me anything new, it would just make the code longer.

The penalty system (-0.5 for a wrong answer) was inspired by exams I take at my university, where guessing randomly is punished the same way. I think this makes the score feel more honest.

#### How to run it

1. Install the dependencies: `pip install -r requirements.txt`
2. Get a free API key from https://console.groq.com and set it as an environment variable: `export GROQ_API_KEY=your_key_here`
3. Run the program: `python project.py`
4. Run the tests with: `pytest test_project.py`
