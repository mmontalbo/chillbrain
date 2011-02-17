#!/bin/bash

js_root="../js/"
processLine(){
  line="$@" # get all args
  ./jsmin <$js_root$line>$js_root${line::${#line}-3}".min"${line:${#line}-3}
}

FILE="files_to_minify"
BAKIFS=$IFS
IFS=$(echo -en "\n\b")
exec 3<&0
exec 0<"$FILE"
while read -r line
do	# use $line variable to process line in processLine() function
	processLine $line
done