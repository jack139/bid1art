PY = python3 -O -m compileall -b -q -f

CONFIG = config

SRC = src
SRC_CONF = $(SRC)/$(CONFIG)

JS_PATH=static/js/
JS_FILES=

TARGETS = bid1art
TARGET_CONF = $(TARGETS)/$(CONFIG)

all: clean $(TARGETS)

$(TARGETS):
	@echo "Compiling ..."
	@cp -r $(SRC) $(TARGETS)
	@cat $(TARGETS)/app_settings.py >> $(TARGETS)/app_helper.py
	-$(PY) $(TARGETS)
	@find $(TARGETS) -name '*.py' -delete
	@find $(TARGETS) -name "__pycache__" |xargs rm -rf
	@rm $(TARGET_CONF)/setting.pyc
	@rm $(TARGETS)/app_settings.pyc
	@cp $(SRC_CONF)/setting.py $(TARGET_CONF)

js:
	@for c in $(JS_FILES); do \
		echo "compressing $$c ..."; \
		$(JAVA) $(JS_PATH)$$c.js > $(JS_PATH)$$c.min.js; \
	done

clean:
	@echo "Clean ..." 
	@find . -name "__pycache__" |xargs rm -rf
	@rm -rf $(TARGETS)
