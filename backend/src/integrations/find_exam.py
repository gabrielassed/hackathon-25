from src.data.exams import EXAMS
from unidecode import unidecode

def match_exam(lines):
    exams = []
    for line in lines:
        find_for = line.lower()
        for exam in EXAMS:
            name = unidecode(exam['name']).lower()
            if name.startswith(find_for):
                exams.append(exam)
    return exams or None