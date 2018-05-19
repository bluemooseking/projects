#include <stdlib.h>
#include <assert.h>

#include "heap.h"

static void swap(ushort *a, ushort *b) {
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
static void heap_sort_up_##dir(heap_t *heap) {										\
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

static void heap_sort_up(heap_t *heap) {
	if (heap->type == HEAP_MAX) {
		__heap_sort_up(max, heap);
	} else {
		__heap_sort_up(min, heap);
	}
}

#define __HEAP_SORT_DOWN(dir, opr) 										\
static void heap_sort_down_##dir(heap_t *heap) {									\
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

static void heap_sort_down(heap_t *heap) {
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

