from project import calculate_score, validate_question_count, parse_ai_response


def test_calculate_score():
    assert calculate_score(5, 0)==5.0
    assert calculate_score(4, 2)==3.0
    assert calculate_score(0, 4)==-2.0
    assert calculate_score(10, 10)==5.0
    assert calculate_score(0, 0)==0
    assert calculate_score(1, 1)==0.5


def test_validate_question_count():
    assert validate_question_count("5")==5
    assert validate_question_count("10")==10
    assert validate_question_count("20")==20
    # not in the allowed list, should fall back to 5
    assert validate_question_count("7")==5
    assert validate_question_count("100")==5
    # not a number at all
    assert validate_question_count("abc")==5
    assert validate_question_count("")==5
    assert validate_question_count("ten")==5


def test_parse_ai_response():
    # normal clean json
    clean='[{"question": "what is 2+2?", "options": {"A": "3", "B": "4", "C": "5", "D": "6"}, "answer": "B"}]'
    result=parse_ai_response(clean)
    assert len(result)==1
    assert result[0]["answer"]=="B"
    assert result[0]["question"]=="what is 2+2?"

    # wrapped in markdown code block
    wrapped='```json\n[{"question": "capital of France?", "options": {"A": "Berlin", "B": "Madrid", "C": "Paris", "D": "Rome"}, "answer": "C"}]\n```'
    result=parse_ai_response(wrapped)
    assert len(result)==1
    assert result[0]["answer"]=="C"

    # extra text before and after, but valid json inside
    messy='here are your questions: [{"question": "q", "options": {"A": "1", "B": "2", "C": "3", "D": "4"}, "answer": "A"}] hope this helps'
    result=parse_ai_response(messy)
    assert len(result)==1

    # broken json
    assert parse_ai_response("not json at all")==[]
    assert parse_ai_response("")==[]
    assert parse_ai_response("[{broken]")==[]

    # missing fields should be skipped
    missing='[{"question": "no options or answer"}]'
    assert parse_ai_response(missing)==[]

    # answer letter not in options should be skipped
    bad_answer='[{"question": "q", "options": {"A": "1", "B": "2", "C": "3", "D": "4"}, "answer": "Z"}]'
    assert parse_ai_response(bad_answer)==[]
