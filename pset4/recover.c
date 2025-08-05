#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef uint8_t BYTE;
int main(int argc, char *argv[])
{
    // Accept a single command-line argument
    if (argc != 2)
    {
        printf("Usage: ./recover FILE\n");
        return 1;
    }

    // Open memory card file
    FILE *input = fopen(argv[1], "r");
    if (input == NULL)
    {
        printf("Could not open file.\n");
        return 1;
    }

    // Buffer to store 512 bytes
    BYTE buffer[512];

    // File pointer to write recovered image
    FILE *output = NULL;

    // Counter for image filenames
    int file_count = 0;

    // Filename buffer
    char file_name[8];

    // Read blocks of 512 bytes until end of file
    while (fread(buffer, sizeof(BYTE), 512, input) == 512)
    {
        // Check if start of new JPEG
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff &&
            (buffer[3] & 0xf0) == 0xe0)

        {
            // If already writing a JPEG then close it
            if (output != NULL)
            {
                fclose(output);
            }

            // Create new filename
            sprintf(file_name, "%03i.jpg", file_count);
            file_count++;

            output = fopen(file_name, "w");
        }

        // If JPEG file is open, write current block
        if (output != NULL)
        {
            fwrite(buffer, sizeof(BYTE), 512, output);
        }
    }

    // Close last JPEG file if any
    if (output != NULL)
    {
        fclose(output);
    }

    // Close input file
    fclose(input);

    return 0;
}
