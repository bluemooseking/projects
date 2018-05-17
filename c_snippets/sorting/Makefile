CC	= gcc
CFLAGS	= -g -lm
RM	= rm -f

default: all

all: sort_test

sort_test: sort_test.c
	$(CC) $(CFLAGS) -o sort_test sort_test.c

clean veryclean:
	$(RM) sort_test
