#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <assert.h>

void print_buffer(ushort size, ushort arr[]) {
	ushort x;
	for (x = 0; x < size; x++)
		printf("%d, ", arr[x]);
	printf("\n");
}

#define HEAP_MIN	0
#define HEAP_MAX	1
typedef struct _heap {
	ushort type;
	ushort size;
	ushort tree[128];
} heap_t;

void swap(ushort *a, ushort *b) {
	ushort __swap = *a;
	*a = *b;
	*b = __swap;
}

heap_t* heap_create(ushort type, ushort val) {
	heap_t *heap = malloc(sizeof(heap_t));
	heap->type = type;
	heap->size = 1;
	heap->tree[0] = val;
}

void heap_destory(heap_t *heap) {
	free(heap);
}

ushort heap_peek(heap_t *heap) {
	return heap->tree[0];
}

ushort heap_size(heap_t *heap) {
	return heap->size;
}

#define __HEAP_SORT_UP(dir, opr) 										\
void heap_sort_up_##dir(heap_t *heap) {										\
	ushort idx = heap->size - 1;										\
	ushort parent;												\
	while (idx > 0) {											\
		parent = (idx - 1)/2;										\
		if (heap->tree[idx] opr heap->tree[parent])							\
			swap(&(heap->tree[idx]), &(heap->tree[parent]));					\
		else												\
			break;											\
		idx = parent;											\
	}													\
}
__HEAP_SORT_UP(max, >)
__HEAP_SORT_UP(min, <)
#define __heap_sort_up(dir, heap)	heap_sort_up_##dir((heap))

void heap_sort_up(heap_t *heap) {
	if (heap->type == HEAP_MAX) {
		__heap_sort_up(max, heap);
	} else {
		__heap_sort_up(min, heap);
	}
}

#define __HEAP_SORT_DOWN(dir, opr) 										\
void heap_sort_down_##dir(heap_t *heap) {									\
	ushort parent = 0;											\
														\
	while (1) {												\
		ushort child_a = (2 * parent) + 1;								\
		ushort child_b = child_a + 1;									\
														\
		if (child_a >= heap->size)									\
			break;											\
														\
		if (child_b < heap->size) {									\
			int a_p = (heap->tree[child_a] opr heap->tree[parent]);					\
			int b_p = (heap->tree[child_b] opr heap->tree[parent]);					\
			int a_b = (heap->tree[child_a] opr heap->tree[child_b]);				\
														\
			if (b_p & !a_b) {									\
				swap(&(heap->tree[parent]), &(heap->tree[child_b]));				\
				parent = child_b;								\
				continue;									\
			}											\
														\
			if (a_p & a_b) {									\
				swap(&(heap->tree[parent]), &(heap->tree[child_a]));				\
				parent = child_a;								\
				continue;									\
			}											\
														\
			if (!a_p & !b_p)									\
				break;										\
														\
			assert(0);										\
														\
		} else {											\
			int a_p = (heap->tree[child_a] opr heap->tree[parent]);					\
														\
			if (a_p)										\
				swap(&(heap->tree[parent]), &(heap->tree[child_a]));				\
			break;											\
		}												\
	}													\
}
__HEAP_SORT_DOWN(max, >);
__HEAP_SORT_DOWN(min, <)
#define __heap_sort_down(dir, heap)	heap_sort_down_##dir((heap))

void heap_sort_down(heap_t *heap) {
	if (heap->type == HEAP_MAX) {
		__heap_sort_down(max, heap);
	} else {
		__heap_sort_down(min, heap);
	}
}


void heap_insert(heap_t *heap, ushort val) {
	heap->tree[heap->size] = val;
	heap->size++;
	heap_sort_up(heap);
}

ushort heap_pop(heap_t *heap) {
	ushort ret = heap->tree[0];
	heap->size--;
	heap->tree[0] = heap->tree[heap->size];
	heap->tree[heap->size] = 0;
	heap_sort_down(heap);
	return ret;
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
