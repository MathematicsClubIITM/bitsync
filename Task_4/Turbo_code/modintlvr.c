#include <stdio.h>
#include <stdlib.h>

// Function to allocate and generate the interleaver permutation
int *generatePermutation(int m, int n) {
    // Allocate memory for the permutation array
    int *permut = (int *)malloc(n * sizeof(int));

    // Check if memory allocation is successful
    if (permut == NULL) {
        printf("Memory allocation failed!\n");
        exit(1);  // Exit if memory allocation fails
    }

    // Fill the permutation array with modular interleaver values
    for (int i = 0; i < n; ++i) {
        permut[i] = (m * (i + 1)) % n;
    }
    return permut;
}

// Function to print the permutation array
void printPermutation(int *permut, int n) {
    for (int i = 0; i < n; ++i) {
        printf("%d ", permut[i]);
    }
    printf("\n");
}

int main() {
    int m, n;
    
    // Take user input for m and n
    printf("Enter values for m and n: ");
    scanf("%d %d", &m, &n);

    // Generate the modular interleaver permutation
    int *p = generatePermutation(m, n);
    
    // Print the permutation result
    printPermutation(p, n);

    // Free the allocated memory
    free(p);
    
    return 0;
}
