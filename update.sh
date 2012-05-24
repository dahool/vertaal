#!/bin/bash
BASEDIR=`dirname $0`
BASEDIR=`(cd "$BASEDIR"; pwd)`
cd $BASEDIR
git pull
sh appupdate.sh
cd -
