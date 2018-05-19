CC	= gcc
CFLAGS	= -g -lm
RM	= rm -f

default: all

all: median

median: median.c heap.c
	$(CC) $(CFLAGS) -o median median.c heap.c

clean veryclean:
	$(RM) median
