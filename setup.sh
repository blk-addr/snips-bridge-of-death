#!/usr/bin/env bash -e

VENV=venv

if [ ! -d "$VENV" ]
then

	PYTHON=`which python2`

	if [ ! -f $PYTHON ]
	then
		echo "Python 2 not found"
	fi

	echo "Running virtualenv -p $PYTHON $VENV"
	virtualenv -p $PYTHON $VENV
fi

. $VENV/bin/activate

pip install -r requirements.txt
