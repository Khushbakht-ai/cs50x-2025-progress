#include <cs50.h>
#include <stdio.h>

void loop(int n);  
int main(void)
{
    int n;
    do
    {
        n = get_int("Height: ");
    }
    while (n < 1 || n > 8);

    loop(n);  
}

void loop(int n)
{
    for (int i = 1; i <= n; i++)
    {
        
        for (int j = n - 1; j >= i; j--)
        {
            printf(" ");
        }

        for (int k = 1; k <= i; k++)
        {
            printf("#");
        }

        printf("  ");

        for (int k = 1; k <= i; k++)
        {
            printf("#");
        }

        printf("\n");
    }
}  
