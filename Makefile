PROJDIR      := mypkg
PYTHON       := python
DIST_DIR     := dist
TMP_DIST_DIR := dist_tmp
VERSION      := $(shell pip list|grep 'setuptools-scm' > /dev/null 2>&1 || pip install setuptools_scm > /dev/null 2>&1 && python -m setuptools_scm -r . 2>/dev/null||echo Unknown)
TARGET       := $(shell $(PYTHON) -m build -o $(TMP_DIST_DIR) -s | tail -1 |awk '{print $$NF}' || echo error;)


.PHONY: all bdist sdist clean veryclean

all:
ifeq ($(lastword $(TARGET)),error)
	$(error Finding TARGET name failed. You can manually check by `$(PYTHON) -m build -o $(TMP_DIST_DIR) -s`)
endif
	echo $(VERSION)
	rm -r $(TMP_DIST_DIR)
	$(PYTHON) setup_b.py build_ext --inplace
	$(PYTHON) -m build -o $(TMP_DIST_DIR) -s

bdist:
	mkdir -p $(DIST_DIR)
	test $$(find $(TMP_DIST_DIR) -maxdepth 1 -name *.whl | wc -l) -eq 1 || { echo "Only one wheel file is expected"; exit 1; }
	ls -t $(TMP_DIST_DIR)/*.whl | head -1 | xargs $(PYTHON) package_tag.py wheel | xargs -I {} mv $(TMP_DIST_DIR)/*.whl $(DIST_DIR)/{}
	rm -r $(TMP_DIST_DIR)
sdist:
	$(PYTHON) setup_compile.py build_ext --inplace
	$(PYTHON) -m build -o $(TMP_DIST_DIR) -s
clean:
	find $(PROJDIR) -name *.so | xargs rm -f
	find $(PROJDIR) -name *.c  | xargs rm -f
	-rm -r setup.py $(TMP_DIST_DIR) *.egg-info/ build/
