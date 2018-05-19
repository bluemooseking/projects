#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <assert.h>

#include "heap.h"

void print_buffer(ushort size, ushort arr[]) {
	ushort x;
	for (x = 0; x < size; x++)
		printf("%d, ", arr[x]);
	printf("\n");
}

ushort find_median(int size, ushort arr[]) {

	int x;

	ushort mid(ushort x, ushort y) {
		return (ushort)(((uint)x + (uint)y) / 2);
	}

	// corner cases
	if (size==1)
		return arr[0];
	if (size==2)
		return mid(arr[0],arr[1]);

	ushort a, b;
	if (arr[0] < arr[1]) {
		a = arr[0];
		b = arr[1];
	} else {
		a = arr[1];
		b = arr[0];
	}
			
	heap_t *lo_heap = heap_create(HEAP_MAX, a);
	heap_t *hi_heap = heap_create(HEAP_MIN, b);

	for (x=2; x<size; x++) {
		if (heap_peek(hi_heap) < arr[x]) {
			heap_insert(hi_heap, arr[x]);
		} else {
			heap_insert(lo_heap, arr[x]);
		}

		while (heap_size(hi_heap) > heap_size(lo_heap)) {
			heap_insert(lo_heap, heap_pop(hi_heap));
		}

		while (heap_size(lo_heap) > (1 + heap_size(hi_heap))) {
			heap_insert(hi_heap, heap_pop(lo_heap));
		}
		int diff = heap_size(lo_heap) - heap_size(hi_heap);
		assert((diff == 0) || (diff == 1));
	}

	if (heap_size(lo_heap) == ((heap_size(hi_heap) + 1)))
		return heap_peek(lo_heap);
	if (heap_size(lo_heap) == heap_size(hi_heap))
		return mid(heap_peek(lo_heap), heap_peek(hi_heap));

	return -1;
}

void validate_median(ushort median, int size, ushort arr[]) {
	int x;
	int diff = 0;
	for (x = 0; x<size; x++) {
		if (median < arr[x])
			diff--;
		if (median > arr[x])
			diff++;
	}
	assert(diff == 0);
}

int main(int argc, char* argv[]) {

	// Get Size
	if (argc != 2) {
		printf("enter 1 arg\n");
		return -1;
	}
	int size = atoi(argv[1]);
	printf("size: %d\n", size);

	// build array
	ushort *sortlist;
	int bytesize = size * sizeof(*sortlist);
	sortlist = malloc(bytesize);
	int urnd = open("/dev/urandom", O_RDONLY);
	read(urnd, sortlist, bytesize);
	close(urnd);
	printf("sortlist filled\n");

	// Find Median
	ushort median = find_median(size, sortlist);
	print_buffer(size, sortlist);
	printf("median: %d\n", median);

	validate_median(median, size, sortlist);
	printf("median validated!\n");

	free (sortlist);
	return 0;

}
