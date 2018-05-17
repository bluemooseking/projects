#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <time.h>
#include <math.h>
#include <sys/mman.h>

#include "lock.h"

//#define DEBUG 2
#ifdef DEBUG
#define debug(format, ...)	warn("ID:%d %s(%d) -> " format, finfo.id, __func__, __LINE__, ##__VA_ARGS__)
#else
#define debug
#endif

struct timeval start, current;

static int print_array(int n, int *arr) {
	int idx;
	for (idx=0; idx<n; idx++) {
		printf("%d, ", *(arr + idx));
	}
	printf("\n");
	return 0;
}

static int check_sort_valid(int n, int *arr) {
	int idx;
	for (idx=0; idx<n-1; idx++) {
		if (*(arr + idx) > *(arr + idx + 1))
			return -1;
	}
	return 0;
}

/*
 * BUBBLE SORT
 * */
static int bubble_sort(int n, int *arr) {
	int i, j;
	int *a, *b;

	void swap(int *a, int *b) {
		int __swap = *a;
		*a = *b;
		*b = __swap;
	}

	for (i=0; i<n-1; i++) {
		for (j=0; j<n-i-1; j++) {
			a = arr + j;
			b = a + 1;
			if ( *a > *b )
				swap(a, b);
		}
	}
	return 0;
}

/*
 * INSERTION SORT
 * */
static int insertion_sort(int n, int *arr) {
	int i, j;
	int *a, *b;

	void swap(int *a, int *b) {
		int __swap = *a;
		*a = *b;
		*b = __swap;
	}

	for (i=1; i<n; i++) {
		for (j=i; j; j--) {
			a = arr + j;
			b = a - 1;
			if ( *a < *b )
				swap(a, b);
			else
				break;
		}
	}
	return 0;
}

/* 
 * MERGE SORT
 * */
static int merge_sort(int n, int *arr) {

	void __merge(int *dst, int *src, int low, int mid, int high) {
		int i, j, k;
		i = low;
		j = mid + 1;
		for (k=low; k<=high; k++) {
			if (i > mid) {
				dst[k] = src[j++];
			} else {
				if (j > high) {
					dst[k] = src[i++];
				} else {
					if (src[i] < src[j]) {
						dst[k] = src[i++];
					} else {
						dst[k] = src[j++];
					}
				}
			}
		}
	}

	void __merge_sort(int *dst, int *src, int low, int high) {
		int mid;
		if (low < high) {
			mid = (low + high)/2;
			__merge_sort(src, dst, low, mid);
			__merge_sort(src, dst, mid + 1, high);
			__merge(dst, src, low, mid, high);
		}
	}

	int *tmp = malloc(n * sizeof(arr));
	memcpy(tmp, arr, n * sizeof(*arr));
	
	__merge_sort(arr, tmp, 0, n-1);

	free(tmp);
	return 0;
}

/* 
 * QUICK SORT
 * */
static int quick_sort(int n, int *arr) {
	
	int __quick_divide(int *arr, int low, int high) {
		if (low >= high) return low;

		int i = low;
		int j = high;
		int split = arr[high];
		while (i < j) {
			if (arr[i] > split) {
				arr[j--] = arr[i];
				arr[i] = arr[j];
			} else {
				i++;
			}
		}
		arr[i] = split;
		return i;
	}

	void __quick_sort(int *arr, int low, int high) {
		int mid;
		if (low < high) {
			mid = __quick_divide(arr, low, high);
			__quick_sort(arr, low, mid - 1);
			__quick_sort(arr, mid + 1, high);
		}
	}

	__quick_sort(arr, 0, n-1);
}

#define TESTCNT 4
#define LOOPMIN 2
#define LOOPMAX 21
#define LOOPSTP	2

#define SIZECNT (LOOPMAX - LOOPMIN + 1) / LOOPSTP
#define CELL_LEN 23
#define SIZE_LEN 6

#define __ref(NAME) { .name = #NAME, .func = NAME ## _sort }
struct _ref {
	char *name;
	int (*func)(int, int*);
} x_ref[TESTCNT] = {
	__ref(bubble),
	__ref(insertion),
	__ref(merge),
	__ref(quick)
};
struct sort_set {
	volatile unsigned started;
	volatile unsigned complete;
	volatile double sumx;
	volatile double sumx2;
	struct _ref *ref;
};
struct __shr {
	int size;
	char name[5];
	struct sort_set sort[TESTCNT];
};
struct _shr {
	spinlock lock;
	unsigned pidcnt;
	unsigned sum_complete;
	struct __shr x[SIZECNT];
	struct {
		char **name;
		char **size;
	} proc[128];
};

int set_size_name(char *buffer, int size) {
	int prefix = size;
	int offset = 0;
	while (prefix > 1023) {
	       prefix /= 1024;
	       offset++;
	}
	switch(offset) {
		case 0:
			return sprintf(buffer, "%d", prefix);
		case 1:
			return sprintf(buffer, "%d%s", prefix, "K");
		case 2:
			return sprintf(buffer, "%d%s", prefix, "M");
		case 3:
			return sprintf(buffer, "%d%s", prefix, "T");
		default:
			error(EXIT_FAILURE, 0, "size to big");
	}
}

void init_shr(struct _shr *shr) {
	int idx, jdx, kdx;
	shr->lock = 0;
	shr->pidcnt = 0;

	spin_lock(&(shr->lock));

	shr->sum_complete = SIZECNT * TESTCNT;	// one extra per
	for (idx=LOOPMIN, jdx=0; jdx<SIZECNT; idx+=LOOPSTP, jdx++) {
		shr->x[jdx].size = pow(2, idx);
		set_size_name(shr->x[jdx].name, shr->x[jdx].size);
		for (kdx=0; kdx<TESTCNT; kdx++) {
			shr->x[jdx].sort[kdx].started = 0;
			shr->x[jdx].sort[kdx].complete = 0;
			shr->x[jdx].sort[kdx].sumx = 0;
			shr->x[jdx].sort[kdx].sumx2 = 0;
			shr->x[jdx].sort[kdx].ref = &(x_ref[kdx]);
		}
	}

	spin_unlock(&(shr->lock));
}

double mean(struct sort_set *set) {
	return (set->complete) ? (set->sumx / (double)set->complete) : 0;
}

double stdev(struct sort_set *set) {
	return (set->complete) ?
		sqrt(((double)set->complete * set->sumx2) - (pow(set->sumx, 2))) / (double)set->complete :
		0;
}

#define RESET	"\033[0m"
#define BLACK	"\033[1m\033[30m"
#define RED	"\033[1m\033[31m"
#define GREEN	"\033[1m\033[32m"
#define YELLOW	"\033[1m\033[33m"
#define BLUE	"\033[1m\033[34m"
#define MAGENTA	"\033[1m\033[35m"
#define CYAN	"\033[1m\033[36m"
#define WHITE	"\033[1m\033[37m"
#define __print_cell(c, l)	printf("%-*s", (l), (c))
#define print_cell(c)		__print_cell((c), CELL_LEN)
void print_header() {
	char cell[CELL_LEN + 1];
	int idx;

	// ROW 1
	snprintf(cell, CELL_LEN, "size");
	__print_cell(cell, SIZE_LEN);
	for (idx=0; idx<TESTCNT; idx++) {
		snprintf(cell, CELL_LEN, "%s", x_ref[idx].name);
		print_cell(cell);
	}
	printf("\n");

	// ROW 2
	snprintf(cell, CELL_LEN, "");
	__print_cell(cell, SIZE_LEN);
	for (idx=0; idx<TESTCNT; idx++) {
		snprintf(cell, CELL_LEN, "%-*s", CELL_LEN, "mean     sdev     n");
		print_cell(cell);
	}
	printf("\n");

}

static void print_table(struct _shr *shr) {
	char cell[CELL_LEN + 1];
	int idx, jdx;
	struct _shr tmp;

	gettimeofday(&current, NULL);
	system("clear");

	printf("Elapsed Time: %d secs\n", (current.tv_sec - start.tv_sec));
	print_header();

	// copy the data
	spin_lock(&(shr->lock));
	tmp = *shr;
	spin_unlock(&(shr->lock));

	// print data
	for (jdx=0; jdx<SIZECNT; jdx++) {
		snprintf(cell, SIZE_LEN, "%-*s", SIZE_LEN, tmp.x[jdx].name);
		__print_cell(cell, SIZE_LEN);
		for (idx=0; idx<TESTCNT; idx++) {
			struct sort_set *set = &(tmp.x[jdx].sort[idx]);
			double m = mean(set);
			double s = stdev(set);
			if (!m) 
				printf(BLACK);
			else if (m < 0.000001) {
				printf(GREEN);
			} else if (m < 0.001) {
				printf(YELLOW);
			} else if (m < 1) {
				printf(CYAN);
			} else {
				printf(RED);
			}
			snprintf(cell, CELL_LEN, 
					"%.2e %-.2e %-5d",
					m, s,
					tmp.x[jdx].sort[idx].complete);
			print_cell(cell);
			printf(RESET);
		}
		printf("\n");
	}

	for (idx=1; idx < shr->pidcnt; idx++) {
		printf("CHLD %d: running %s %s\n", idx,
				*(tmp.proc[idx].name),
				*(tmp.proc[idx].size));
	}

}

#define FORK_CNT 5
struct forkinfo {
	unsigned id;
	unsigned chld;
} finfo = {
	.id = 0,
	.chld = 0
};
static void fork_out() {
	unsigned idx = FORK_CNT;
	int pid;

	while(idx--) {
		finfo.id <<= 1;
		pid = fork();

		if (pid<0)
			error(EXIT_FAILURE, 0, "couldn't fork: %u", finfo.id);

		if (pid)
			(finfo.chld)++;
		else
			(finfo.id)++;
	}
}

#define RUN_MAX 9999
static unsigned get_completed_sum(struct _shr *shr, int idx, int jdx, int *target) {
	unsigned val;
	unsigned sum = 0;

	spin_lock(&(shr->lock));

	sum = shr->sum_complete;
	*target = shr->x[idx].sort[jdx].complete + 1;

	spin_unlock(&(shr->lock));

	return sum;
}

static int find_sort_set(struct _shr *shr, struct sort_set **set) {

	// Determine Random test
	int r, s, t;
	struct sort_set *__set;
	while (1) {

		debug("loop");

		// pick random set
		r = rand() % (SIZECNT * TESTCNT);
		s = r / TESTCNT;
		t = r % TESTCNT;
		__set = &(shr->x[s].sort[t]);
		debug("mod: %d r: %d s: %d t: %d", SIZECNT*TESTCNT, r, s, t);

		debug("started: %d", __set->started);
		if (__set->started >= RUN_MAX)
			continue;

		// Do we have a hit
		int target;
		unsigned sum = get_completed_sum(shr, s, t, &target);
		debug("sum: %d target: %u", sum, target);
		r = rand() % sum;
		if (r > target)
			continue;

		debug("target hit");
		// Try for a lock
		if (atomic_inc(&(__set->started)) < RUN_MAX)
			break;

		debug("false start");
		atomic_dec(&(__set->started));
	}

	debug("sound set: %s size %s", __set->ref->name, shr->x[s].name);
	shr->proc[finfo.id].name = &(__set->ref->name);
	shr->proc[finfo.id].size = &(shr->x[s].name);
	*set = __set;
	return shr->x[s].size;
}

static void child_proc(struct _shr *shr) {
	int status;

#ifdef DEBUG
	int loopcnt = DEBUG;
#endif

	// keep testing
	while (1) {

		// Setup data
		struct sort_set *set;
		int size = find_sort_set(shr, &set);

		// Create Array and fill
		int *sortlist;
		int bytesize = size * sizeof(*sortlist);
		sortlist = malloc(bytesize);
		int urnd = open("/dev/urandom", O_RDONLY);
		read(urnd, sortlist, bytesize);
		close(urnd);
		debug("sortlist filled");

		// Execute sort
		clock_t tic = clock();
		set->ref->func(size, sortlist);
		clock_t toc = clock();
		double msdiff = (double)(toc - tic) / CLOCKS_PER_SEC;
		debug("test elapsed: %e", msdiff);

		// Update dataset
		spin_lock(&(shr->lock));

		set->sumx += msdiff;
		set->sumx2 += msdiff * msdiff;
		(set->complete)++;
		(shr->sum_complete)++;
		if (set->complete >= RUN_MAX) {
			shr->sum_complete -= RUN_MAX + 1;
		}
		debug("test values -> c: %d sc: %d sx: %e sx2: %e", 
				set->complete,
				shr->sum_complete,
				set->sumx,
				set->sumx2);

		spin_unlock(&(shr->lock));

		free(sortlist);
#ifdef DEBUG
		if (--loopcnt == 0)
			break;
		debug("%d more loops", loopcnt);
#endif
	}

	while ((finfo.chld)--) {
		wait(&status);
		debug("id detect end: %u(%d)", finfo.id, status);
	}

	exit(0);
}

static void __set_seed() {
	int i, stime;
	long ltime;

	/* get the current calendar time */
	ltime = time(NULL);
	stime = (unsigned) ltime/2;
	srand(stime);
}

int main(void) {
	
	int status;
	struct _shr *shr;
	debug("Begin Sort Test...\n");
	
	__set_seed();

	gettimeofday(&start, NULL);
	shr = mmap(NULL, sizeof(struct _shr),
			PROT_READ | PROT_WRITE,
			MAP_SHARED | MAP_ANONYMOUS,
			-1, 0);
	init_shr(shr);

	fork_out();
	atomic_inc(&(shr->pidcnt));
	debug("id start: %u(%u)", finfo.id, finfo.chld);

	// CHILD PROCESSES
	if (finfo.id) {
		child_proc(shr);
		error(EXIT_FAILURE, 0, "child proc breakout");
	}
		
	// MAIN PROCESS
#ifndef DEBUG
	while (1) {
		print_table(shr);
		sleep(1);
	}
#endif
	
	while ((finfo.chld)--) {
		wait(&status);
		warn("id detect end: %u(%d)", finfo.id, status);
	}
	munmap(shr, sizeof(struct _shr));
	return 0;
}
