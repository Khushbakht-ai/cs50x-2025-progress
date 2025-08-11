from cs50 import get_string

# Function to calculate Coleman-Liau index


def coleman_liau(text):
    letters = 0
    words = 1
    sentences = 0

    for char in text:
        if char.isalpha():
            letters += 1
        elif char == ' ':
            words += 1
        elif char in ['.', '?', '!']:
            sentences += 1

    # Average number of letters per 100 words
    L = (letters * 100.0) / words

    # Average number of sentences per 100 words
    S = (sentences * 100.0) / words

    # Coleman-Liau formula
    index = 0.0588 * L - 0.296 * S - 15.8
    return index

# Function to print grade based on index


def calculate_grade(index):
    if index < 1:
        print("Before Grade 1")
    elif index >= 16:
        print("Grade 16+")
    else:
        print(f"Grade {round(index)}")


# Main program
text = get_string("Text: ")
index = coleman_liau(text)
calculate_grade(index)
