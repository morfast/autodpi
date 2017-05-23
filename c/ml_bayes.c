#include<stdio.h>
#include<stdlib.h>
#include<assert.h>
#include<string.h>

#define BYTE_ENCODE_SIZE 257
#define NULL_ENCODE_VALUE 256

typedef enum {
    NEG, 
    POS, 
    N_CLASS,
} class_type;

typedef struct ml_param {

} ml_param_t;

typedef struct ml_bayes_param {
    ml_param_t common_param;

    /* P(Fn | C)
     * possibility of feature Fn in class C
     */ 
    int feature_size;
    double P_C[N_CLASS];
    double *P_F_C[N_CLASS];
} ml_bayes_param_t;

static void print_bayes_param(ml_bayes_param_t *p)
{
    int i,j;
    printf("n_feature: %d\n", p->feature_size);
    
    for (i = 0; i < N_CLASS; i++) {
        printf("pc: %lf\n", p->P_C[i]);
        printf("pfc: ");
        for (j = 0; j < p->feature_size; j++) {
            printf("%lf ", p->P_F_C[i][j]);
        }
        printf("\n");
    }
}

/* feature_size
 * P_C
 * PFC
 */
ml_bayes_param_t* load_bayes_param(const char *filename)
{
    FILE *fp;
    int i,j;
    int n_class, n_feature;
    int c;
    ml_bayes_param_t *param;

    param = (ml_bayes_param_t*)malloc(sizeof(ml_bayes_param_t));
    fp = fopen(filename, "r");

    fscanf(fp, "%d", &n_class);
    for (i = 0; i < n_class; i++) {
        fscanf(fp, "%d", &c);
        fscanf(fp, "%lf", &(param->P_C[c]));
    }

    fscanf(fp, "%d", &n_class);
    for (i = 0; i < n_class; i++) {
        fscanf(fp, "%d", &c);
        fscanf(fp, "%d", &n_feature);
        param->P_F_C[c] = (double *)malloc(sizeof(double) * n_feature);
        for (j = 0; j < n_feature; j++) {
            fscanf(fp, "%lf", &(param->P_F_C[c][j]));
        }
    }
    param->feature_size = n_feature;

    return param;            

}

/* flow type prediction with naive bayes method
 * buf: original bytes in the flow
 * n: then length of buf */
class_type bayes_predict(unsigned char *buf_inbound, int n_inbound, 
                         unsigned char *buf_outbound, int n_outbound,
                         ml_bayes_param_t *param)
{
    int i;
    double **P_F_C, *P_C;
    int feature_size = param->feature_size;
    int n_max = feature_size / BYTE_ENCODE_SIZE / 2;

    P_C = param->P_C;
    P_F_C = param->P_F_C;

    /* for each class, calculate P(F1|C)P(F2|C)...P(Fn|C)P(C) */
    int c;
    double result_P[N_CLASS];
    for (c = 0; c < N_CLASS; c++) {
        double *pfc = P_F_C[c];
        result_P[c] = P_C[c];
        /* inbound */
        for (i = 0; i < n_inbound && i < n_max; i++) {
            result_P[c] *= (pfc[buf_inbound[i] + (BYTE_ENCODE_SIZE * i)]);
            //printf("%d ", buf_inbound[i]);
        }
        while (i < n_max) {
            result_P[c] *= (pfc[NULL_ENCODE_VALUE + (BYTE_ENCODE_SIZE * i)]);
            //printf("%d ", NULL_ENCODE_VALUE);
            i += 1;
        }
        /* outbound */
        for (i = 0; i < n_outbound && i < n_max; i++) {
            result_P[c] *= (pfc[buf_outbound[i] + (BYTE_ENCODE_SIZE * (i + n_max))]);
            //printf("%d ", buf_outbound[i]);
        }
        while (i < n_max) {
            result_P[c] *= (pfc[NULL_ENCODE_VALUE + (BYTE_ENCODE_SIZE * (i + n_max))]);
            //printf("%d ", NULL_ENCODE_VALUE);
            i += 1;
        }
        printf("%e\n", result_P[c]);

    }

    double maxp = 0.0;
    int maxi = -1;
    for (c = 0; c < N_CLASS; c++) {
        //printf("result_P %e\n", result_P[c]);
        if (result_P[c] > maxp) {
            maxp = result_P[c];
            maxi = c;
        }
    }
    
    return maxi;
}


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

int main2(int argc, char *argv[])
{
    flow_data_t *data;
    data = read_test_data(argv[1]);

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

    for (i = 2; i < argc; i++) {
        data = read_test_data(argv[i]);
        //ret = bayes_predict(buf, 64, param);
        ret = bayes_predict(data->buf_inbound, data->n_inbound, 
                         data->buf_outbound, data->n_outbound,
                         param);
        printf("%s: %d\n", argv[i], ret);
    }
    //print_bayes_param(param);

    return 0;
}

