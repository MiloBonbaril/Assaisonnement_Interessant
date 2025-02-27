.PHONY: setup

setup:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "Virtual environment setup complete. To activate it, run 'source venv/bin/activate'."