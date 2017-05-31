bayes_test: ml_bayes.o ml_bayes_test.o
	gcc -O0 -g ml_bayes.o ml_bayes_test.o -o bayes_test

ml_bayes.o: ml_bayes.c
	gcc -c -O0 -g -Werror ml_bayes.c

ml_bayes_test.o: ml_bayes_test.c
	gcc -c -O0 -g ml_bayes_test.c

clean:
	rm -f bayes_test *.o


