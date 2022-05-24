

setup:
	if which python3.10 && [ ! -d venv ] ; then python3.10 -m venv venv ; fi
	source venv/bin/activate \
		&& pip install -q -U pip \
		&& pip install -e .'[dev,test]' \

