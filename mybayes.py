#!/usr/bin/python

class MyBayesClassifier():

    def __init__(self):
        # number of samples
        self._n_samples_ = 0
        # number of features, length of the feature vector
        self._n_features_ = 0
        # number of classes, usually 2
        self._n_classes_ = 0

        self._P_FC_ = {}
        self._P_C_ = {}

    def fit(self, x, y):
        total_n_samples = len(x)
        assert(len(x) == len(y))
        self._n_samples_ = total_n_samples
        self._n_features_ = len(x[0])
        self._n_classes_ = len(set(y))
        # group the data by class
        data_per_c = {}
        for data, label in zip(x,y):
            if data_per_c.has_key(label):
                data_per_c[label].append(data)
            else:
                data_per_c[label] = [data]

        #  calculate P for each class
        for c in data_per_c.keys():
            datas = data_per_c[c]
            n_samples = len(datas)
            #print zip(datas)[0]
            #s = [sum(i) for i in zip(*datas)]
            self._P_FC_[c] = [(sum(i) + 0.01 ) /float(n_samples) for i in zip(*datas)]
            assert(all(self._P_FC_[c]))
            self._P_C_[c] = n_samples / float(total_n_samples)
        #print self._P_FC_
        #print self._P_C_


    def predict(self, datas):
        res = []
        for data in datas:
            cs = []
            ps = []
            for c in self._P_FC_.keys():
                p_fc = self._P_FC_[c]
                p_cf = 1.0
                for i,d in enumerate(data):
                    if d > 0:
                        p_cf *= p_fc[i]
                p_cf *= self._P_C_[c]
                ps.append(p_cf)
                cs.append(c)

            print "ps: ", ps
            res.append(max(zip(ps, cs), key=lambda x: x[0])[1])
            #print "data:", data, "ps:", ps, "cs", cs

        return res

    def score(self, x, y):
        predict_y = self.predict(x)
        c = 0
        for i, yy in enumerate(y):
            if predict_y[i] == y[i]:
                c += 1

        return float(c)/len(y)

    def get_params(self, deep=False):
        pass

    def store_model(self, sample_name):
        storefilename = "bayes_" + sample_name + ".model"
        f = open(storefilename, "w")

        #float P_C[N_CLASS];
        nclass = self._n_classes_
        f.write("%d\n" % nclass)
        for c in self._P_C_.keys():
            f.write("%d\n" % c)
            f.write("%12.10lf\n" % self._P_C_[c])
            
        #float *P_F_C[N_CLASS];
        f.write("%d\n" % nclass)
        for c in self._P_FC_.keys():
            f.write("%d\n" % c)
            f.write("%d\n" % self._n_features_)
            for v in self._P_FC_[c]:
                f.write("%12.10lf " % v)
            f.write("\n")




#x = [ [1,1,1,1,1], [0,0,0,0,0] ]
#y = [1,0]
#
#clf = MyBayesClassifier()
#clf.fit(x, y)
#print clf.predict(x)
