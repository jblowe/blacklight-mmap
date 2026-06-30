# mmap-code

Code for the **Middle Mekong Archaeology Project (MMAP)** — managing its
metadata, images, and search. This repository collects three independent
codebases, each in its own top-level directory:

| Directory | What it is |
|-----------|------------|
| [`blacklight/`](blacklight/) | Ruby on Rails / [Blacklight](https://projectblacklight.org/) web app: the public search interface over the MMAP Solr index. |
| [`mmap-solr/`](mmap-solr/) | Shell/Python scripts to build and refresh the Solr core from the Postgres database, and to manage images and their derivatives. |
| [`pg-editor/`](pg-editor/) | A small Flask web app for browsing and editing the MMAP Postgres tables directly in the browser. |

Each directory has its own README with setup and usage details.

## How the pieces fit together

- The authoritative data lives in a **Postgres** database, edited via **`pg-editor`**.
- **`mmap-solr`** reads Postgres (e.g. `tblSite`) to build/refresh the **Solr** core
  and to generate image derivatives.
- **`blacklight`** is the Rails web app that searches the Solr core.

```bash
# Refresh the Solr core and image derivatives (from tblSite in Postgres)
cd mmap-solr
./update_mmap.sh

# make_derivatives.sh creates a parallel dir of smaller images
./make_derivatives.sh --clean --size 640 --quality 70 ORIGINAL_DIR DERIVATIVES_DIR
```
