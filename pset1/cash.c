#include <cs50.h>
#include <stdio.h>

int calculate_coins(int cents);
int main(void)
{
    int cents;
    do
    {

        cents = get_int("Change owed: ");
    }
    while (cents < 0);

    int Total = calculate_coins(cents);
    printf("%i\n", Total);
}

int calculate_coins(int cents)
{
    int quarters = cents / 25;
    cents %= 25;

    int dimes = cents / 10;
    cents %= 10;

    int nickels = cents / 5;
    cents %= 5;

    int pennies = cents / 1;

    return quarters + dimes + nickels + pennies;
}
