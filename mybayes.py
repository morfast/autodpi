#!/usr/bin/python

class MyBayesClassifier():

    def __init__(self):
        #self._n_samples_ = 0
        #self._samples_len_ = 0
        self._P_FC_ = {}
        self._P_C_ = {}
        pass

    def fit(self, x, y):
        total_n_samples = len(x)
        assert(len(x) == len(y))
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
            self._P_FC_[c] = [(sum(i) + 1)/float(n_samples) for i in zip(*datas)]
            self._P_C_[c] = n_samples / float(total_n_samples)


    def predict(self, datas):
        res = []
        for data in datas:
            cs = []
            ps = []
            for c in self._P_FC_.keys():
                p_fc = self._P_FC_[c]
                p_cf = 0.0
                for i,d in enumerate(data):
                    if d:
                        p_cf *= p_fc[i]
                p_cf *= self._P_C_[c]
                ps.append(p_cf)
                cs.append(c)

            res.append(max(zip(ps, cs), key=lambda x: x[0])[1])

        return res

    def score(self, x, y):
        self.fit(x, y)
        predict_y = self.predict(x)
        c = 0
        for i, yy in enumerate(y):
            if predict_y[i] == y[i]:
                c += 1

        return float(c)/len(y)


    def get_params(self, deep=False):
        pass
