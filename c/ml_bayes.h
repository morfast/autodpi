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

    int feature_size;
    double P_C[N_CLASS];
    double *P_F_C[N_CLASS];
} ml_bayes_param_t;

/* load parameters of the model */
ml_bayes_param_t* load_bayes_param(const char *filename);

/* predict according to inbound and the corresponding oubound flows */
class_type bayes_predict2(unsigned char *buf_inbound, int n_inbound, 
                         unsigned char *buf_outbound, int n_outbound,
                         ml_bayes_param_t *param);
class_type bayes_predict(unsigned char *buf, int len, ml_bayes_param_t *param);

#endif	/* ml_bayes.h */
