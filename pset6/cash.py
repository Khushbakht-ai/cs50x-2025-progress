from cs50 import get_float

# Function to calculate coins


def calculate_coins(cents):
    quarters = cents // 25
    cents %= 25

    dimes = cents // 10
    cents %= 10

    nickels = cents // 5
    cents %= 5

    pennies = cents // 1

    return quarters + dimes + nickels + pennies


# Prompt user for valid input
while True:
    dollars = get_float("Change owed: ")
    if dollars >= 0:
        break

# Convert dollars to cents
cents = round(dollars * 100)

# Print result
total = calculate_coins(cents)
print(total)
