#!/usr/bin/env bash
echo "This is the install script for development only"

if [ -z "$VIRTUAL_ENV" ]; then
   echo -e "\e[31mPlease ACTIVATE A VIRTUAL ENV before and run me again \e[0m"
   exit -1;
fi

pip install  -e ".[test]"
