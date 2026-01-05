python csv_to_postgres_load.py \
  "$1" \
  '"public"."tblSite"' \
  "$2" \
  "$3" \
  --null-blank

