#include <stdio.h>
#include <stdlib.h>

// Function to print the interleaved array
void Print(int *p, int size) {
    for (int i = 0; i < size; i++) {
        printf("%d ", p[i]);  // Print each element
    }
    printf("\n");
}

// Block interleaver function: it arranges elements in a 2D matrix and reads them column-wise
int *Block_Interleaver(int r, int c) {
    // Allocate memory for the interleaved array
    int *p = (int *)malloc(r * c * sizeof(int));
    if (p == NULL) {
        printf("Memory allocation failed!\n");
        exit(1);  // Exit if memory allocation fails
    }

    // Create a 2D array (row-major order) to fill with the numbers
    int **arr = (int **)malloc(r * sizeof(int *));
    for (int i = 0; i < r; i++) {
        arr[i] = (int *)malloc(c * sizeof(int));
    }

    // Fill the 2D array with sequential values
    int k = 1;
    for (int i = 0; i < r; ++i) {
        for (int j = 0; j < c; ++j) {
            arr[i][j] = k;
            k++;
        }
    }

    // Now interleave the values column by column into the 1D array 'p'
    int idx = 0;
    for (int i = 0; i < c; ++i) {  // Iterate over columns
        for (int j = 0; j < r; ++j) {  // Iterate over rows
            p[idx] = arr[j][i];  // Column-major order filling
            idx++;
        }
    }

    // Free the dynamically allocated 2D array
    for (int i = 0; i < r; i++) {
        free(arr[i]);
    }
    free(arr);

    return p;
}

int main() {
    int r, c;

    // Prompt the user for the number of rows and columns of the matrix
    printf("Enter the number of rows and columns for the interleaver matrix (r, c): ");
    scanf("%d %d", &r, &c);

    // Call the Block_Interleaver function to get the interleaved data
    int *p = Block_Interleaver(r, c);

    // Print the interleaved data
    int size = r * c;
    printf("Interleaved Data: ");
    Print(p, size);

    // Free the memory allocated for the interleaved array
    free(p);

    return 0;
}
