#include <cs50.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

bool luhns_algorathim(char str[]);
void credit_card(char str[]);
bool count_number(long number);
int get_length(long number);

int main(void)
{
    long number;
    do
    {
        number = get_long("Enter your credit card number (only digits): ");
    }
    while ((number < 0));

    char str[25];
    sprintf(str, "%ld", number);

    bool iscount;
    iscount = count_number(number);
    if (iscount)
    {
        bool is_luhns_algorathim = luhns_algorathim(str);
        if (is_luhns_algorathim)
        {
            credit_card(str);
        }
        else
        {
            printf("INVALID\n");
        }
    }
    else
    {
        printf("INVALID\n");
    }
}

bool luhns_algorathim(char str[])
{
    int sum = 0;
    int len = strlen(str);

    for (int i = 0; i < len; i++)
    {
        int digit = str[i] - '0';
        if ((len - i) % 2 == 0)
        {
            digit *= 2;
            if (digit > 9)
            {
                digit -= 9;
            }
        }
        sum += digit;
    }
    if (sum % 10 == 0)
    {
        return true;
    }
    else
    {
        return false;
    }
}

void credit_card(char str[])
{
    int len = strlen(str);

    if ((len == 16 || len == 13) && (str[0] == '4'))
    {
        printf("VISA\n");
    }
    else if (len == 16 && str[0] == '5' && (str[1] >= '1' && str[1] <= '5'))
    {
        printf("MASTERCARD\n");
    }
    else if (len == 15 && str[0] == '3' && (str[1] == '4' || str[1] == '7'))
    {
        printf("AMEX\n");
    }
    else
    {
        printf("INVALID\n");
    }
}

bool count_number(long number)
{
    int len = get_length(number);
    if (len == 13 || len == 15 || len == 16)
    {
        return true;
    }
    else
    {
        return false;
    }
}

int get_length(long number)
{
    int length = 0;
    while (number != 0)
    {
        number /= 10;
        length++;
    }
    return length;
}
