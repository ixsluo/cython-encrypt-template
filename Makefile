PROJDIR      := mypkg
PYTHON       := python
DIST_DIR     := dist
TMP_DIST_DIR := build/build_custom
WHL          := $(lastword $(shell $(PYTHON) package_tag.py set |tail -1 || echo error |tail -1)).whl


.PHONY: all bdist sdist clean veryclean

all: $(DIST_DIR)/$(WHL)

$(DIST_DIR)/$(WHL):
ifeq ($(WHL),error.whl)
	$(error Finding TARGET name failed. You can manually check by `$(PYTHON) package_tag.py set`)
endif
	$(PYTHON) setup_compile.py build_ext --inplace
	$(PYTHON) -m build -o $(TMP_DIST_DIR) -s
	tar -zxf $(TMP_DIST_DIR)/*.tar.gz -C $(TMP_DIST_DIR)
	find $(TMP_DIST_DIR) -d 1 -type d | xargs -I {} python -m build -w {}
	mkdir -p $(DIST_DIR)
	find $(TMP_DIST_DIR)/*/dist/ -d 1 -type f -name *.whl | xargs -I {} mv {} $(DIST_DIR)/$(WHL)
clean:
	-find $(PROJDIR) -name *.so | xargs rm -f
	-find $(PROJDIR) -name *.c  | xargs rm -f
	-rm -r setup.py $(TMP_DIST_DIR) *.egg-info/ build/
