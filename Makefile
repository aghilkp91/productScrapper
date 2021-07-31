#PHONY: install flake flake add_audio add_directory recognize

install:
	@echo "*** Installing dependencies ***"
	pip3 install -r requirements.txt

flake:
	@echo "*** Linting python code ***"
	flake8 . --ignore="E501"

create_db:
	@echo "*** Creating the database ***"
	python3 Database/createDatabase.py

html:
	@echo "*** Building HTML Documentation***"
	cd docs
	sphinx-apidoc -f -o .\source\ ..
	sphinx-build -b html source build