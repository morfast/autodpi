#ifndef	_ML_BAYES_H_
#define	_ML_BAYES_H_	1

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

ml_bayes_param_t* load_bayes_param(const char *filename);
class_type bayes_predict(unsigned char *buf_inbound, int n_inbound, 
                         unsigned char *buf_outbound, int n_outbound,
                         ml_bayes_param_t *param);

#endif	/* ml_bayes.h */
