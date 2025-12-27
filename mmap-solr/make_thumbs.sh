#!/usr/bin/env bash

set -x

ORIGINALfile="$(pwd)/$1.txt"
RESULTfile="$(pwd)/$1-converted.txt"
rm -f ${RESULTfile}

TYPE=image

while IFS=$'\t' read -r ORIGINAL; do
  ((LINES++))
  ORIGINAL_FULL_PATH="originals/${ORIGINAL}"
  SLUG_DIR=$(dirname "${ORIGINAL}")
  mkdir -p "derivatives/${SLUG_DIR}"
  SLUG="derivatives/${ORIGINAL}"
  if [ ! -e "${SLUG}" ]; then
    if [ $TYPE == 'image' ]; then
      # magick -density 300 "${ORIGINAL_FULL_PATH}" -background white -alpha remove -resize '800x>' -strip -quality 90 "${SLUG}"
      magick -density 200 "${ORIGINAL_FULL_PATH}" \
        -background white -alpha remove \
        -resize "640x640>" \
        -strip -interlace JPEG \
        -sampling-factor 4:2:0 \
        -define jpeg:dct-method=float \
        -quality 70 \
        "${SLUG}"
      echo -e "${SLUG}" >>${RESULTfile}
    elif [ $TYPE == 'pdf' ]; then
      magick -density 300 "${ORIGINAL_FULL_PATH}[0]" -resize 1000x -define png:compression-level=9 -strip -background white -alpha remove "${SLUG}"
      echo -e "${SLUG}" >>${RESULTfile}
    else
      echo -e "${SLUG}" >>${RESULTfile}
    fi
  else
    echo "done already: $SLUG"
    echo -e "${SLUG}" >>${RESULTfile}
  fi
done <"${ORIGINALfile}"

echo "${LINES} lines read from ${ORIGINALfile}"
