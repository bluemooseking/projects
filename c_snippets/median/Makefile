CC	= gcc
CFLAGS	= -g -lm
RM	= rm -f

default: all

all: med_heap

med_heap: med_heap.c
	$(CC) $(CFLAGS) -o med_heap med_heap.c

clean veryclean:
	$(RM) med_heap
