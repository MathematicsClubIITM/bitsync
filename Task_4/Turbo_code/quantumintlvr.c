#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Function to generate an interleaved sequence
int *interleaver(int *data, int size, int key) {
    // Allocate memory for the interleaved data and indices
    int *p = (int *)malloc(size * sizeof(int));
    int *indices = (int *)malloc(size * sizeof(int));

    // Use the provided key as the seed for the random number generator
    srand(key); // Initialize the random number generator with the provided key (seed)
    
    // Initialize indices with original positions (0, 1, 2, ..., size-1)
    for (int i = 0; i < size; i++) {
        indices[i] = i;
    }

    // Shuffle the indices randomly based on the key
    for (int i = 0; i < size; i++) {
        int j = rand() % size;  // Pick a random index j
        int temp = indices[i];
        indices[i] = indices[j];
        indices[j] = temp;
    }

    // Apply the permutation to data (data is shuffled according to indices)
    for (int i = 0; i < size; i++) {
        p[i] = data[indices[i]]; // Place the data elements into the new shuffled order
    }

    // Free the memory allocated for indices
    free(indices);

    // Return the interleaved data
    return p;
}

// Function to print an array
void printArray(int *arr, int size) {
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

int main() {
    int size, key;

    // Ask user for the size of the data (number of elements)
    printf("Enter the number of elements (size): ");
    scanf("%d", &size);
    
    // Ask user for the key (seed) for the random number generator
    printf("Enter the key (seed) for random number generation: ");
    scanf("%d", &key);
    
    // Automatically generate the data array as 1, 2, 3, 4, ..., size
    int *data = (int *)malloc(size * sizeof(int));
    for (int i = 0; i < size; i++) {
        data[i] = i + 1;  // Initialize data as 1, 2, 3, ..., size
    }

    // Generate interleaved data
    int *interleavedData = interleaver(data, size, key);
    printf("Interleaved data: ");
    printArray(interleavedData, size);

    // Free the dynamically allocated memory
    free(data);
    free(interleavedData);

    return 0;
}
