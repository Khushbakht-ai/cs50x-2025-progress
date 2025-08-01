#include <cs50.h>  // For get_string function
#include <ctype.h> // For isalpha function
#include <math.h>  // For round function
#include <stdio.h>
#include <string.h> // For strlen function

// Prototypes
float Coleman_Liau(string text);
void calculate_Grade(float index);

int main(void)
{
    string text = get_string("Text: ");

    float index = Coleman_Liau(text);
    calculate_Grade(index);
}
float Coleman_Liau(string text)
{
    int len = strlen(text);
    int letters = 0;
    int words = 1;
    int sentences = 0;

    // Loop through text to count letters, words and sentences
    for (int i = 0; i < len; i++)
    {
        if (isalpha(text[i]))
        {
            letters++;
        }
        if ((text[i]) == ' ')
        {
            words++;
        }
        if (text[i] == '.' || text[i] == '?' || text[i] == '!')
        {
            sentences++;
        }
    }

    // Average number of letters and sentences per 100 words
    float L = (letters * 100.0) / words;
    float S = (sentences * 100.0) / words;

    // Applying Coleman Liau formula
    float index = 0.0588 * L - 0.296 * S - 15.8;
    return index;
}

void calculate_Grade(float index)
{
    if (index < 1)
    {
        printf("Before Grade 1\n");
    }
    else if (index >= 16)
    {
        printf("Grade 16+\n");
    }
    else
    {
        printf("Grade %i\n", (int) round(index));
    }
}
