#include <cs50.h>  // For get_string function
#include <ctype.h> // For isalpha function
#include <stdio.h>
#include <stdlib.h>
#include <string.h> // For strlen function

void substitution(string text, string key);
int main(int argc, string argv[])
{
    // Check for exactly one argument
    if (argc != 2)
    {
        printf("Usage: ./substitution key\n");
        return 1;
    }
    // Check if all characters in argv[1] are alphabets
    for (int i = 0; i < 26; i++)
    {
        if (!isalpha(argv[1][i]))
        {
            printf("Usage: ./substitution key\n");
            return 1;
        }

        // Check for repetition
        for (int j = i + 1; j < 26; j++)
        {
            if (toupper(argv[1][i]) == toupper(argv[1][j]))
            {
                printf("Usage: ./substitution key\n");
                return 1;
            }
        }

        // Check for length
        int len = strlen(argv[1]);
        if (len != 26)
        {
            printf("Key must contain 26 characters.\n");
        }
    }

    // Convert key to integer
    string k = (argv[1]);

    string p = get_string("plaintext: ");

    printf("ciphertext: ");
    substitution(p, k);
    printf("\n");

    return 0;
}

void substitution(string text, string key)
{
    int len = strlen(text);
    for (int i = 0; i < len; i++)
    {
        if (isalpha(text[i]))
        {
            if (isupper(text[i]))
            {
                int index = text[i] - 'A';
                printf("%c", toupper(key[index]));
            }
            else
            {
                int index = text[i] - 'a';
                printf("%c", tolower(key[index]));
            }
        }
        else
        {
            printf("%c", text[i]);
        }
    }
}
