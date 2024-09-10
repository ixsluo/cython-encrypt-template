PROJDIR      := mypkg
PYTHON       := python
DIST_DIR     := dist
TMP_DIST_DIR := dist_tmp
WHL          := $(DIST_DIR)/$(lastword $(shell $(PYTHON) package_tag.py set |tail -1 || echo error |tail -1)).whl


.PHONY: all bdist sdist clean veryclean

all: $(DIST_DIR)/$(WHL)

$(DIST_DIR)/$(WHL): $(TMP_DIST_DIR)/$(WHL)

$(TMP_DIST_DIR)/$(WHL):
ifeq ($(WHL),error.whl)
	$(error Finding TARGET name failed. You can manually check by `$(PYTHON) package_tag.py set`)
endif
	$(PYTHON) setup_compile.py build_ext --inplace
	$(PYTHON) -m build -o $(TMP_DIST_DIR) -s
	tar -zxf $(TMP_DIST_DIR)/*.tar.gz -C $(TMP_DIST_DIR)
	@echo $(WHL)

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
