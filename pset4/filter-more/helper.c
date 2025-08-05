#include "helpers.h"
#include <math.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    // Loop over all pixels
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Take average of red, green, and blue
            int avg =
                round((image[i][j].rgbtBlue + image[i][j].rgbtGreen + image[i][j].rgbtRed) / 3.0);

            // Update pixel values
            image[i][j].rgbtBlue = avg;
            image[i][j].rgbtGreen = avg;
            image[i][j].rgbtRed = avg;
        }
    }
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width / 2; j++)
        {
            // Swap pixels
            RGBTRIPLE temp = image[i][j];
            image[i][j] = image[i][width - 1 - j];
            image[i][width - 1 - j] = temp;
        }
    }
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE copy[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            copy[i][j] = image[i][j];
        }
    }
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int redSum = 0;
            int blueSum = 0;
            int greenSum = 0;
            int count = 0;

            for (int k = -1; k <= 1; k++)
            {
                for (int l = -1; l <= 1; l++)
                {
                    int x = k + i;
                    int y = l + j;

                    if (x >= 0 && x < height && y >= 0 && y < width)
                    {
                        redSum += copy[x][y].rgbtRed;
                        greenSum += copy[x][y].rgbtGreen;
                        blueSum += copy[x][y].rgbtBlue;
                        count++;
                    }
                }
            }

            image[i][j].rgbtRed = round((float) redSum / count);
            image[i][j].rgbtBlue = round((float) blueSum / count);
            image[i][j].rgbtGreen = round((float) greenSum / count);
        }
    }
}

// Function for clamping values
int limit(int value)
{
    if (value > 255)
    {
        return 255;
    }
    else if (value < 0)
    {
        return 0;
    }
    return value;
}

// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE copy[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            copy[i][j] = image[i][j];
        }
    }

    // Gx and Gy kernels for Sobel operator
    int Gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};

    int Gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};

    // Loop over each pixel
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int sumRedX = 0, sumGreenX = 0, sumBlueX = 0;
            int sumRedY = 0, sumGreenY = 0, sumBlueY = 0;

            // Loop over 3 x 3 grid
            for (int k = -1; k <= 1; k++)
            {
                for (int l = -1; l <= 1; l++)
                {
                    int x = k + i;
                    int y = l + j;

                    if (x >= 0 && x < height && y >= 0 && y < width)
                    {
                        int gx = Gx[k + 1][l + 1];
                        int gy = Gy[k + 1][l + 1];

                        sumRedX += copy[x][y].rgbtRed * gx;
                        sumGreenX += copy[x][y].rgbtGreen * gx;
                        sumBlueX += copy[x][y].rgbtBlue * gx;

                        sumRedY += copy[x][y].rgbtRed * gy;
                        sumGreenY += copy[x][y].rgbtGreen * gy;
                        sumBlueY += copy[x][y].rgbtBlue * gy;
                    }
                }
            }

            // Using sqrt(Gx^2 + Gy^2)
            int red = round(sqrt(sumRedX * sumRedX + sumRedY * sumRedY));
            int green = round(sqrt(sumGreenX * sumGreenX + sumGreenY * sumGreenY));
            int blue = round(sqrt(sumBlueX * sumBlueX + sumBlueY * sumBlueY));

            // Clamp values
            image[i][j].rgbtRed = limit(red);
            image[i][j].rgbtGreen = limit(green);
            image[i][j].rgbtBlue = limit(blue);
        }
    }
}
