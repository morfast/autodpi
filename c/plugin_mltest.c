#include "plugin.h"


#ifdef NDPI_PROTOCOL_MLTEST

#define PLUGIN_DICT_COUNT                         1

#include<stdlib.h>
#include<stdio.h>
#include<assert.h>
#include<string.h>

#define BYTE_ENCODE_SIZE 257
#define NULL_ENCODE_VALUE 256


typedef enum {
    ML_TYPE_NEG, 
    ML_TYPE_POS, 
    N_CLASS,
} class_type;

//typedef struct ml_param {
//
//} ml_param_t;

typedef struct ml_bayes_param {
    //ml_param_t common_param;
    int feature_size;
    double P_C[N_CLASS];
    double *P_F_C[N_CLASS];
} ml_bayes_param_t;

static ml_bayes_param_t g_bayes_param_mltest;
static int g_param_read_success = 0;

/* load parameters of the model */
static int load_bayes_param(const char *filename, ml_bayes_param_t *param)
{
    FILE *fp;
    int i,j;
    int n_class, n_feature;
    int c;

    fp = fopen(filename, "r");
    if (fp == NULL) {
        return -1;
    }

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

    return 0;            

}

/* flow type prediction with naive bayes method
 * buf: original bytes in the flow
 * len: then length of buf 
 * param: loaded model parameters */
static class_type bayes_predict(const unsigned char *buf, int len, ml_bayes_param_t *param)
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



void ndpi_search_mltest(struct ndpi_detection_module_struct *ndpi_struct, struct ndpi_flow_struct *flow)
{
  struct ndpi_packet_struct *packet = &flow->packet;
  class_type ftype;

  if (g_param_read_success <= 0) return;

  ftype = bayes_predict(packet->payload, packet->payload_packet_len, &g_bayes_param_mltest);

  if (ftype == ML_TYPE_POS) { 
    NDPI_LOG(NDPI_PROTOCOL_MLTEST, ndpi_struct, NDPI_LOG_DEBUG, "Found mltest.\n");
    ndpi_set_detected_protocol(ndpi_struct, flow, NDPI_PROTOCOL_MLTEST, NDPI_PROTOCOL_UNKNOWN);
  } else {
    NDPI_LOG(NDPI_PROTOCOL_MLTEST, ndpi_struct, NDPI_LOG_DEBUG, "Exclude mltest.\n");
    NDPI_ADD_PROTOCOL_TO_BITMASK(flow->excluded_protocol_bitmask, NDPI_PROTOCOL_MLTEST);
  }

}

void init_mltest_dissector(struct ndpi_detection_module_struct *ndpi_struct, u_int32_t *id, NDPI_PROTOCOL_BITMASK *detection_bitmask)
{
  int ret;

  ret = load_bayes_param("/usr/local/etc/dpi/config/ml/mltest.model", &g_bayes_param_mltest);
  if (ret >= 0) {
      g_param_read_success = 1; 
  }
  ndpi_set_bitmask_protocol_detection("MLTEST", ndpi_struct, detection_bitmask, *id,
				      NDPI_PROTOCOL_MLTEST,
				      ndpi_search_mltest,
				      NDPI_SELECTION_BITMASK_PROTOCOL_HAS_PAYLOAD,
				      SAVE_DETECTION_BITMASK_AS_UNKNOWN,
				      ADD_TO_DETECTION_BITMASK);
  
  *id += 1;
}


struct protocol_dissector_module plug_module[] =
{
    {
        .ndpi_protocol_id = NDPI_PROTOCOL_MLTEST,
        .label            = "MLTEST",
        .chinese_label    = "ML测试",
        .dir_name         = "GAME",
        .dict_info         = NULL,
        .dict_num         = 0,
        .init_fun         = init_mltest_dissector    
    }
};

DEFINE_PLUGINS_INIT(plug_module, 1);

#endif
