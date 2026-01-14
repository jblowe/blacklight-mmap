# blacklight-mmap

Suite to manage MMAP metadata and images for
various purposes, including:

* Blacklight search engine (RoR web app)
* Solr core creation and refresh
* Managing images and derivatives for web apps, site catalog, etc.
* Postgres database editing app (`pg_edit`)

```
# update solr core and derivatives
# based on tblSite in postgres db
# and sync images in /mnt/images (on ubuntu ec2 server)
cd mmap-solr
./update_mmap.sh
```

```
# make_derivatives.sh creates a parallel dir of smaller images
cd mmap-solr
./make_derviatives.sh --clean --size 640 --quality 70 ORIGINAL_DIR DERIVATIVES_DIR
./make_derviatives.sh  --dry-run ORIGINAL_DIR DERIVATIVES_DIR


```

