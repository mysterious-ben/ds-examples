long long mysum(int n, int* array) {
    if (n <= 1) {
        return 0;
    }
    long long res = 0;
    for (int i = 0; i < n-1; ++i) {
        if (array[i] > array[i+1]) {
            res += array[i];
        }
    }
    return res;
}
