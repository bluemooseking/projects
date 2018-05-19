#ifndef __HEAP_H__
#define __HEAP_H__

#define ushort		unsigned short
#define HEAP_MIN	0
#define HEAP_MAX	1
typedef struct _heap {
	ushort type;
	ushort size;
	ushort tree[128];
} heap_t;

heap_t* heap_create(ushort type, ushort val);
void heap_destory(heap_t *heap);
ushort heap_size(heap_t *heap);
ushort heap_peek(heap_t *heap);
void heap_insert(heap_t *heap, ushort val);
ushort heap_pop(heap_t *heap);

#endif
