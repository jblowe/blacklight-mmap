### hasty description of how the solr core for mmap artifacts is populated.

1. crosswalk.py generates the sql to extract the fields from artifacts_master and
   join
2. get_tables.sh runs the many sql commands and produces .csv files
3. solrETL-artifacts.sh loads the .csv files into solr

The results of step 1. (a couple dozen files each containing one sql SELECT) have
been committed to the repo in solr_sql.

The intermediate files are not committed and are stored in solr_date. These
are regenerated each time `solrETL-artifacts.sh` is run.

The list of subtables to be queried is in `export_tables.sh`; this file is sourced
by `get_tables.sh`

You'll need to set the db credentials in `CONNECT_STRING` in `solrETL-artifacts.sh`

```
# construct the sql to fetch data in .csv format
rm -f nohup.out; nohup time python crosswalk.py &
# run the sql to fetch all the data
rm -f nohup.out; nohup time ./get_tables.sh &
# load all the subrecords for artifacts
rm -f nohup.out; nohup time ./solrETL-artifacts.sh mmap &

# old single table solr refresh. this is obsolete
rm -f nohup.out; nohup time ./solrETL-public.sh mmap &

```
