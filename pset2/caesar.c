#include <cs50.h>  // For get_string function
#include <ctype.h> // For isalpha function
#include <stdio.h>
#include <stdlib.h>
#include <string.h> // For strlen function

void caesar_formula(string text, int key);
int main(int argc, string argv[])
{
    // Check for exactly one argument
    if (argc != 2)
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }
    // Check if all characters in argv[1] are digits
    for (int i = 0; argv[1][i] != '\0'; i++)
    {
        if (!isdigit(argv[1][i]))
        {
            printf("Usage: ./caesar key\n");
            return 1;
        }
    }

    // Convert key to integer
    int k = atoi(argv[1]);

    string p = get_string("plaintext: ");

    printf("ciphertext: ");
    caesar_formula(p, k);
    printf("\n");
}

void caesar_formula(string text, int key)
{
    int len = strlen(text);
    for (int i = 0; i < len; i++)
    {
        if (isalpha(text[i]))
        {
            if (isupper(text[i]))
            {
                char cipher = ((text[i] - 'A' + key) % 26) + 'A';
                printf("%c", cipher);
            }
            else
            {
                char cipher = ((text[i] - 'a' + key) % 26) + 'a';
                printf("%c", cipher);
            }
        }
        else
        {
            printf("%c", text[i]);
        }
    }
}
