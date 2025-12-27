#

BASE_DIR="$1"
set -x
cp make_thumbs.sh ${BASE_DIR}
cd ${BASE_DIR}
find originals -type f | cut -f2- -d "/" | perl -ne 'print if /\.(jpg|jpeg|tif|gif|png|webp)/i' > files-to-convert.txt
# clean up derivatives dir if it exists
mkdir -p derivatives
rm -rf derivatives/*
# nb: no extension, .txt expected
time ./make_thumbs.sh files-to-convert
#
exit

tar czf derivatives.tgz derivatives
scp -i ~/Downloads/jblowe.pem derivatives.tgz ubuntu@54.71.209.160:/mnt/images/

