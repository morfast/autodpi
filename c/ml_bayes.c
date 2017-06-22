#include<stdio.h>
#include<stdlib.h>
#include<assert.h>
#include<string.h>

#include "ml_bayes.h"

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
class_type bayes_predict2(unsigned char *buf_inbound, int n_inbound, 
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
        }
        while (i < n_max) {
            result_P[c] *= (pfc[NULL_ENCODE_VALUE + (BYTE_ENCODE_SIZE * i)]);
            i += 1;
        }
        /* outbound */
        for (i = 0; i < n_outbound && i < n_max; i++) {
            result_P[c] *= (pfc[buf_outbound[i] + (BYTE_ENCODE_SIZE * (i + n_max))]);
        }
        while (i < n_max) {
            result_P[c] *= (pfc[NULL_ENCODE_VALUE + 
                            (BYTE_ENCODE_SIZE * (i + n_max))]);
            i += 1;
        }
        //printf("%e\n", result_P[c]);

    }

    double maxp = 0.0;
    int maxi = -1;
    for (c = 0; c < N_CLASS; c++) {
        assert(result_P[c] != 0.0);
        if (result_P[c] > maxp) {
            maxp = result_P[c];
            maxi = c;
        }
    }
    
    return maxi;
}

class_type bayes_predict(unsigned char *buf, int len, ml_bayes_param_t *param)
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
        for (i = 0; i < len && i < n_max; i++) {
            result_P[c] *= (pfc[buf[i] + (BYTE_ENCODE_SIZE * i)]);
        }
        while (i < n_max) {
            result_P[c] *= (pfc[NULL_ENCODE_VALUE + (BYTE_ENCODE_SIZE * i)]);
            i += 1;
        }
        //printf("%e\n", result_P[c]);

    }

    double maxp = 0.0;
    int maxi = -1;
    for (c = 0; c < N_CLASS; c++) {
        assert(result_P[c] != 0.0);
        if (result_P[c] > maxp) {
            maxp = result_P[c];
            maxi = c;
        }
    }
    
    return maxi;
}

