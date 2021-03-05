#!/usr/bin/make -f
# -*- mode:makefile -*-

# target 1: 13.3269107258 12.4670184697 0.0
# target 2: 36.9942196532 12.5329815303 0.0

PROJECT_DIR := $(shell get-project-dir)

setup: clean \
		parse-model \
		prepare-knowledge \
		run-scone-wrapper

run-model-service:
	sleep 1
	gnome-terminal -x sh -c \
	"$(PROJECT_DIR)/model-service/server.py model.gml --Ice.Config=$(PROJECT_DIR)/examples/servers.config; bash"

run-scone-wrapper:
	sleep 1
	cd $(PROJECT_DIR); \
	gnome-terminal -x sh -c \
	"scone-wrapper --Ice.Config=$(PROJECT_DIR)/examples/servers.config; bash"

run-lighter-t1:
	$(PROJECT_DIR)/lighter.py "IgmlLayer1 -t -e 1.1:tcp -h localhost -p 9090 -t 60000" \
	"scone -t -e 1.1:tcp -h localhost -p 5001 -t 60000" \
	13.3269107258 12.4670184697 0.0

run-lighter-t2:
	$(PROJECT_DIR)/lighter.py "IgmlLayer1 -t -e 1.1:tcp -h localhost -p 9090 -t 60000" \
	"scone -t -e 1.1:tcp -h localhost -p 5001 -t 60000" \
	36.9942196532 12.5329815303 0.0

parse-model: run-model-service
	sleep 1
	$(PROJECT_DIR)/igml-to-scone.py \
	"IgmlLayer1 -t -e 1.1:tcp -h localhost -p 9090 -t 60000"

clean:
	cd $(PROJECT_DIR); \
	$(RM) -r \
	scone-knowledge.d/04-model.lisp scone-knowledge.d/05-init.lisp \
	examples/04/.scone examples/04/model.lisp \
	model-service/__pycache__ \
	.scone \

prepare-knowledge:
	ln -s $(PROJECT_DIR)/examples/04/model.lisp $(PROJECT_DIR)/scone-knowledge.d/04-model.lisp;
	ln -s $(PROJECT_DIR)/examples/04/init.lisp $(PROJECT_DIR)/scone-knowledge.d/05-init.lisp

run-sbcl:
	sbcl --load $(PROJECT_DIR)/examples/scone-start.lisp
