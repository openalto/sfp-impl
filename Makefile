all:
	/home/ubuntu/Env/unicorn/bin/python setup.py install
	/home/ubuntu/Env/unicorn/bin/gunicorn -b 0.0.0.0:8399 -w 4 sfp:app
