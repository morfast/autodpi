#include<stdio.h>
#include<stdlib.h>


#include "ml_bayes.h"

#define BUF_SIZE 10000
typedef struct flow_data {
    unsigned char buf_inbound[BUF_SIZE];
    int n_inbound;
    unsigned char buf_outbound[BUF_SIZE];
    int n_outbound;
} flow_data_t;
    
flow_data_t* read_test_data(const char *filename)
{
    FILE *fp;
    flow_data_t *data;
    unsigned char line[BUF_SIZE];
    unsigned int buf[BUF_SIZE];
    int i, j;
    int line_length;
    int n_scan;
    int ret;

    fp = fopen(filename, "r");

    data = (flow_data_t*)malloc(sizeof(struct flow_data));

    int n = 0;
    while(1) {
        ret = fscanf(fp, "%d", buf + n);
        if (ret == EOF) break;
        n += 1;
    }
    
    j = 0;
    for (i = 0; i < n/2; i++) {
        if (buf[i] < NULL_ENCODE_VALUE) {
            data->buf_inbound[j++] = (unsigned char)buf[i];
        } else {
            break;
        }
    }
    data->n_inbound = i;

    j = 0;
    for(i = n/2; i < n; i++) {
        if (buf[i] < NULL_ENCODE_VALUE) {
            data->buf_outbound[j++] = (unsigned char)buf[i];
        } else {
            break;
        }
    }
    data->n_outbound = i - n/2;

    return data;
}

int test_read_test_data(char *filename)
{
    flow_data_t *data;
    data = read_test_data(filename);

    int i;
    printf("%d\n", data->n_inbound);
    for (i = 0; i < data->n_inbound; i++)
        printf("%d ", data->buf_inbound[i]);

    printf("\n%d\n", data->n_outbound);
    for (i = 0; i < data->n_outbound; i++)
        printf("%d ", data->buf_outbound[i]);
    printf("\n\n", data->n_outbound);
}


int main(int argc, char *argv[])
{
    ml_bayes_param_t *param;
    unsigned int *buf;
    class_type ret;
    int i;
    flow_data_t *data;
    char *buf_inbound;
    int n_inbound; 
    unsigned char *buf_outbound;
    int n_outbound;

    param = load_bayes_param(argv[1]);
    //print_bayes_param(param);

    for (i = 2; i < argc; i++) {
        data = read_test_data(argv[i]);
        ret = bayes_predict(data->buf_inbound, data->n_inbound, 
                         data->buf_outbound, data->n_outbound,
                         param);
        if (ret == NEG) {
            printf("%s: negetive\n", argv[i]);
        } else if (ret == POS) {
            printf("%s: positive\n", argv[i]) ;
        }
    }

    return 0;
}

