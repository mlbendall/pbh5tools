.PHONY: clean all
SHELL = /bin/bash -e

all: build/ci.so

build/ci.so: ci.c
	mkdir -p ./build;\
	gcc -O4 -DGETPROB -shared -fPIC ci.c -o build/ci.so
clean:
	rm -rf build

