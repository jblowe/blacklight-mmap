# blacklight

The **Blacklight** (Ruby on Rails) web application for the Middle Mekong
Archaeology Project (MMAP) — a public search interface over the MMAP Solr index.

This is one of three codebases in the `mmap-code` repository. The Solr core build
and image tooling live in [`../mmap-solr`](../mmap-solr), and the Postgres table
editor in [`../pg-editor`](../pg-editor); see the
[top-level README](../README.md) for how they fit together.

## Requirements

- Ruby + Bundler (see [`Gemfile`](Gemfile))
- A running Solr instance with the MMAP core (built by [`../mmap-solr`](../mmap-solr))

## Setup

```bash
bundle install

# start the app
bin/rails server
```

Then open http://127.0.0.1:3000.

## Notes

- Solr core creation/refresh and image derivative management are **not** part of
  this app — that tooling lives in [`../mmap-solr`](../mmap-solr):

  ```bash
  cd ../mmap-solr
  ./update_mmap.sh        # refresh the Solr core from tblSite in Postgres
  ```
