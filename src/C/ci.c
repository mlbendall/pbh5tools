#include <stdlib.h>
#include <string.h>
#include <stdio.h>

int _bisect(int val, int* vec,  int l,  int r) {
    if ((r - l) <= 3) {
	// a cheat :)
	while (((r - 1) >= 0) && (vec[r-1] >= val)) {
	    r--;
	}
	return r;
    }
    else {
	int i = (l + r)/2;

	if (vec[i] > val) {
	    return _bisect(val, vec, l, i);
	} else {
	    return _bisect(val, vec, i, r);
	}
    }
}

int left_bin_search(int val, int* vec, int l) {
    int s = _bisect(val, vec, 0, l);
    int v = -1;
    
    if (s == 0) {
	return s;
    }
    else if (s == l) {
	v = vec[--s];
    } 
    else {
	v = vec[s];
    }

    if (v > val) {
	s--;
    }
    while (s > 0 && vec[s-1] == vec[s])	s--;

    return s;
}

int right_bin_search(int val, int* vec,  int l) {
    int s = _bisect(val, vec, 0, l);
    
    if (s == l)
	return(s);
    while (s + 1 < l && vec[s + 1] == val)
	s++;
    return s;
}

int number_within_range(int* vec, int s, int e, int vlen) {
    int i,t = 0;
    int lI = left_bin_search(s, vec, vlen);
    int rI = right_bin_search(e, vec, vlen);
    
    for (i = lI; i < rI; i++) {
	if ((s <= vec[i]) && (vec[i] < e)) t++;
    }
    return t;
}


#define _2COL_ME_(i,j) (((i)*2) + (j))

void print_matrix(int* mat, int n, int m) {
    int i,j;
    for (i = 0; i < n; i++) {
	for (j = 0; j < m; j++) {
	    printf("%d ", mat[_2COL_ME_(i,j)]);
	}
	printf("\n");
    }
    printf("----");
}

void compute_indices(int* t_start, int* t_end, int* sorted_t_ends, int* results, int n) {
    int i,k,n_ending,advance = 0;

    // print_matrix(results, n, 2);

    for (i = 1; i < n; i++) {
	// print_matrix(results, n, 2);

	n_ending = number_within_range(sorted_t_ends, t_start[i-1], t_start[i], n);
	// printf("n_ending: %d\n", n_ending);
	if (n_ending == 0) { 
            results[_2COL_ME_(i, 0)] = results[_2COL_ME_(i - 1, 0)] + 1;
	    results[_2COL_ME_(i, 1)] = results[_2COL_ME_(i - 1, 1)] + 1;
	} 
	else {
	    results[_2COL_ME_(i, 1)] = results[_2COL_ME_(i - 1, 1)] - n_ending + 1;
	    
	    advance = 0;
            for (k = i - 1 - results[_2COL_ME_(i - 1, 0)]; k < i; k++) {
                if (t_end[k] > t_start[i]) {
                    break;
		}
		advance++;
	    }
	    
	    results[_2COL_ME_(i, 0)] = results[_2COL_ME_(i - 1, 0)] - advance + 1;
	}
    }
}



