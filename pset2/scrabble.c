#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <string.h>

// Function to calculate score of given word.
int count_score(string words);

// Function to compare scores and display result
void display(int s1, int s2);

int main(void)
{
    // Get words from both players
    string word_1 = get_string("Player 1: ");
    string word_2 = get_string("Player 2: ");

    // Claculate scores
    int sum_1 = count_score(word_1);
    int sum_2 = count_score(word_2);

    // Display result
    display(sum_1, sum_2);
}

int count_score(string words)
{
    int scores[26] = {1, 3, 3, 2,  1, 4, 2, 4, 1, 8, 5, 1, 3,
                      1, 1, 3, 10, 1, 1, 1, 1, 4, 4, 8, 4, 10};

    int sum = 0;
    int len = strlen(words);
    for (int i = 0; i < len; i++)
    {
        if (isalpha(words[i])) // check if character is alphabet
        {
            char upper = toupper(words[i]); // convert to upper case
            int index = upper - 'A';        // Get index
            sum += scores[index];
        }
    }
    return sum;
}

void display(int s1, int s2)
{
    // Compare scores and print result
    if (s1 == s2)
    {
        printf("Tie!\n");
    }
    else if (s1 > s2)
    {
        printf("Player 1 wins!\n");
    }
    else
    {
        printf("Player 2 wins!\n");
    }
}
