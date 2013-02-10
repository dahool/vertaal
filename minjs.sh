#!/bin/bash
BASEDIR=`dirname $0`
BASEDIR=`(cd "$BASEDIR"; pwd)`
cd $BASEDIR
INPUT=$1
OUTPUT=${INPUT%%.*}
java -jar yuicompressor.jar --nomunge --type js -o $OUTPUT.min.js $INPUT