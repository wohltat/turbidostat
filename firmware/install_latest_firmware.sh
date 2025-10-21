#!/bin/bash

hexfile=$(/usr/bin/fd turbidostat.ino.hex /tmp/)
ts_folder="$HOME/Dokumente/projekte/turbidostat/"
gui_folder="$ts_folder/gui/"
firmware_folder="$gui_folder/update/firmware/"
firmware_source_file="$ts_folder/arduino/turbidostat.ino"

pattern='#define TURBIDOSTAT_VERSION\s*\"\(.*\)\"\s*'
fw_version=$(sed -n "s/$pattern/\1/p" $firmware_source_file)
# echo $fw_version
fw_version="${fw_version//.}"  # remove all "."
# https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html#Shell-Parameter-Expansion
# ${string//substring/replacement}  , 

echo move firmware version $fw_version to folder $firmware_folder
cmd="cp $hexfile $firmware_folder/turbidostat_v$fw_version.ino.hex"
echo $cmd
$cmd
