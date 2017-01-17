#!/bin/sh

BASEDIR=$( (cd `dirname $0` && pwd) )

exec python $BASEDIR/lpwrapper.py
