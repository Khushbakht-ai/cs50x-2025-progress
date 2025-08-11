from cs50 import get_int


# Function for implemeting Luhn's Algorithm
def luhns_algorithm(card_str):
    total_sum = 0
    length = len(card_str)

    for i in range(length):
        digit = int(card_str[i])

        # Check if this digit is in an even position (from the right)
        if (length - i) % 2 == 0:
            digit *= 2
            if digit > 9:
                digit -= 9
        total_sum += digit

    return total_sum % 10 == 0


# Function to find card type
def credit_card_type(card_str):
    length = len(card_str)

    # VISA: 13 or 16 digits and starts with 4
    if length in (13, 16) and card_str.startswith("4"):
        print("VISA")

    # MASTERCARD: 16 digits and starts with 51-55
    elif length == 16 and card_str[:2] in ("51", "52", "53", "54", "55"):
        print("MASTERCARD")

    # AMEX: 15 digits and starts with 34 or 37
    elif length == 15 and card_str[:2] in ("34", "37"):
        print("AMEX")

    else:
        print("INVALID")

# Function for finding length


def valid_length(number):
    length = len(str(number))
    return length in [13, 15, 16]


# Prompt user for valid input
while True:
    number = get_int("Enter your credit card number (only digits): ")
    if number >= 0:
        break

# Convert number to string for easier digit processing
card_str = str(number)

# Check length and Luhn's Algorithm validity before identifying card type
if valid_length(number):
    if luhns_algorithm(card_str):
        credit_card_type(card_str)
    else:
        print("INVALID")
else:
    print("INVALID")
