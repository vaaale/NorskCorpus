#!/bin/bash

echo Your container args are: "$@"

APP_PATH=$1
echo "App Path: ${APP_PATH}"

echo "Extracting source files"
#echo $PWD
#ls -la
#echo "Switching dir..."
cd ${APP_PATH}
echo $PWD
#ls -la

find . -type f -not -name '_source.tar.gz' -delete
echo "Extracting _source.tar.gz"
tar zxvf _source.tar.gz
retVal=$?
if [ $retVal -ne 0 ]; then
    echo "Error extracting files"
    return -1
elif
    rm _source.tar.gz
fi
echo "Done"

echo "Install requirements"
pip3 install -r requirements.txt

echo "Staring $2"
python3 ${@:2}

retVal=$?
if [ $retVal -ne 0 ]; then
    echo "Error!"
    return -1
elif
    echo "Success!"
fi

