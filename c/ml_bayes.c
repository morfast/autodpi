#include<stdio.h>
#include<stdlib.h>
#include<assert.h>

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
class_type bayes_predict(unsigned int *buf, int n, ml_bayes_param_t *param)
{
    int i;
    double **P_F_C, *P_C;

    P_C = param->P_C;
    P_F_C = param->P_F_C;

    /* for each class, calculate P(F1|C)P(F2|C)...P(Fn|C)P(C) */
    int c;
    double result_P[N_CLASS];
    for (c = 0; c < N_CLASS; c++) {
        double *pfc = P_F_C[c];
        result_P[c] = P_C[c];
        for (i = 0; i < n; i++) {
            //printf("%d %d %lf\n", buf[i], buf[i] + (257 * i), pfc[buf[i] + (257 * i)]);
            result_P[c] *= (pfc[buf[i] + (257 * i)]);
        }
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

unsigned int* read_test_data(const char *filename)
{
    FILE *fp;

    fp = fopen(filename, "r");
    int length = 32 * 2;
    int i;
    unsigned int *buf;

    buf = (unsigned int *)malloc(sizeof(int) * length);

    for (i = 0; i < length; i++) {
        fscanf(fp, "%d", buf + i);
    }

    return buf;
}
    

int main(int argc, char *argv[])
{
    ml_bayes_param_t *param;
    unsigned int *buf;
    class_type ret;

    param = load_bayes_param(argv[1]);
    buf = read_test_data(argv[2]);

    ret = bayes_predict(buf, 64, param);
    printf("ret: %d\n", ret);
    //print_bayes_param(param);

    return 0;
}

