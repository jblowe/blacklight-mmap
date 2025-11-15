#!/usr/bin/env bash

# drop and then recreate all Solr cores based on the content of this script
# and the default configuration available in solr default configsets

# this script inspired by https://github.com/Brown-University-Library/bul-traject/blob/master/solr7/define_schema.sh
# thanks!

# for solr as deployed on my laptop
SOLR_CMD=solr

# for solr as deployed on RTL-managed Ubuntu servers
#SOLR_CMD=/opt/solr/bin/solr

SOLR_PORT="8983"

SOLR_CORES="mmap-public"

# if we have been given a core to recreate, just recreate that one
if [ $# -ge 1 ]; then
    SOLR_CORES="$1"
    echo "Only recreating the one core ${SOLR_CORES}"
fi

function define_field_types()
{
    # ====================
    # Field types
    # ====================
    echo "Defining new types, redefining others..."

    echo "  alphaOnlySort..."
    curl -s -S -X POST -H 'Content-type:application/json' --data-binary '{
      "add-field-type" : {
         "name":"alphaOnlySort",
         "class":"solr.TextField",
         "sortMissingLast":"true",
         "omitNorms":"true",
         "analyzer" : {
            "tokenizer":{"class":"solr.KeywordTokenizerFactory"},
            "filters":[
              {
                "class":"solr.LowerCaseFilterFactory"
              },
              {
                "class":"solr.TrimFilterFactory"
              },
              {
                "class":"solr.PatternReplaceFilterFactory",
                "pattern":"([^a-z])",
                "replacement":"",
                "replace":"all"
              }
          ]
        }
      }
    }' $SOLR_CORE_URL/schema

    # Notice that the core must be reloaded for this field (that has a default value)
    # to be registered and become effective. See note at the bottom of this script.

    #return 0
    echo "  text_general..."
    curl -s -S -X POST -H 'Content-type:application/json' --data-binary '{
        "replace-field-type": {
            "name": "text_general",
            "class": "solr.TextField",
            "multiValued":true,
            "positionIncrementGap": "100",
            "indexAnalyzer": {
                "tokenizer": {
                    "class": "solr.ClassicTokenizerFactory"},
                "filters": [{
                    "class": "solr.StopFilterFactory",
                    "words": "lang/stopwords_en.txt",
                    "ignoreCase": "true"},
                    {
                        "class": "solr.ASCIIFoldingFilterFactory"},
                    {
                        "class": "solr.LowerCaseFilterFactory"},
                    {
                        "class": "solr.EnglishPossessiveFilterFactory"},
                    {
                        "class": "solr.EnglishMinimalStemFilterFactory"}]},
            "queryAnalyzer": {
                "tokenizer": {
                    "class": "solr.ClassicTokenizerFactory"},
                "filters": [
                    {
                        "class": "solr.StopFilterFactory",
                        "words": "lang/stopwords_en.txt",
                        "ignoreCase": "true"},
                    {
                        "class": "solr.ManagedSynonymGraphFilterFactory",
                        "managed": "english"},
                    {
                        "class": "solr.ASCIIFoldingFilterFactory"},
                    {
                        "class": "solr.LowerCaseFilterFactory"},
                    {
                        "class": "solr.EnglishPossessiveFilterFactory"},
                    {
                        "class": "solr.EnglishMinimalStemFilterFactory"}]},
        }
    }' $SOLR_CORE_URL/schema
}

function define_fields()
    {
    # ====================
    # Fields
    #
    # ====================
    echo "Defining field text..."

    # Notice that we map "text" to "text_en" rather than to "text_general"
    # because Solr 4's "text" field behaved like "text_en" due to the
    # use of the SnowballFilter.
    curl -s -S -X POST -H 'Content-type:application/json' --data-binary '{
      "add-field":{
        "name":"text",
        "type":"text_general",
        "multiValued":true,
        "stored":false,
        "indexed":true
      }
    }' $SOLR_CORE_URL/schema
}

function copy_fields()
{
    # ====================
    # Copy fields
    # ====================

    echo "Making copyFields for $1 $2 ..."
    curl -s -S -X POST -H 'Content-type:application/json' --data-binary "{
      \"add-copy-field\":{
        \"source\": \"$1\",
        \"dest\": [ \"$2\" ]}
    }" $SOLR_CORE_URL/schema
}

function create_copy_fields()
    {
    echo "Reading field definition for copyFields from $1"
    while read field_name
    do
      txt_field_name=${field_name%_*}_txt
      copy_fields $field_name $txt_field_name
    done < $1
    }

function create_synonyms()
    {
    if [[ -f $1 ]]
    then
      echo "Reading synonyms from $1"
      while read synonyms
      do
        [[ ${synonyms} = \#* ]] && continue
        [[ ${synonyms} = '' ]] && continue
        echo "Making synonyms for $1: ${synonyms}..."
        curl -s -S -X PUT -H 'Content-type:application/json' --data-binary "${synonyms}" $SOLR_CORE_URL/schema/analysis/synonyms/english
      done < $1
    else
      echo "No synonyms file found: $1"
    fi
    }

function define_dynamic_fields()
{
    # right now this is a NOOP:
    # we only use the standard, pre-defined dynamic fields
    return 0
    # ====================
    # Dynamic fields
    # ====================
    echo "Defining dynamic fields..."
    curl -s -S -X POST -H 'Content-type:application/json' --data-binary '{
      "add-dynamic-field":{
        "name":"*_txt",
        "type":"text_general",
        "multiValued":true,
        "indexed":true,
        "stored":true},
    }' $SOLR_CORE_URL/schema
}

function define_special_fields()
{
    # ====================
    # special fields
    # ====================
    echo "Defining special fields for $1..."

    if [[ "$1" = "mmap-public" ]]; then
        curl -s -S -X POST -H 'Content-type:application/json' --data-binary '{
            "add-field":{
                "name":"images_ss",
                "stored":true,
                "indexed":true}
        }' $SOLR_CORE_URL/schema
        curl -s -S -X POST -H 'Content-type:application/json' --data-binary '{
            "add-copy-field":{"source":
                "txtimagename1_s",
                "dest": [ "images_ss" ]}
        }' $SOLR_CORE_URL/schema
        curl -s -S -X POST -H 'Content-type:application/json' --data-binary '{
            "add-copy-field":{"source":
                "txtimagename2_s",
                "dest": [ "images_ss" ]}
        }' $SOLR_CORE_URL/schema
        curl -s -S -X POST -H 'Content-type:application/json' --data-binary '{
            "add-copy-field":{"source":
                "txtimagename3_s",
                "dest": [ "images_ss" ]}
        }' $SOLR_CORE_URL/schema
        curl -s -S -X POST -H 'Content-type:application/json' --data-binary '{
            "add-copy-field":{"source":
                "txtimagename4_s",
                "dest": [ "images_ss" ]}
        }' $SOLR_CORE_URL/schema
        curl -s -S -X POST -H 'Content-type:application/json' --data-binary '{
            "add-copy-field":{"source":
                "txtimagename5_s",
                "dest": [ "images_ss" ]}
        }' $SOLR_CORE_URL/schema
        curl -s -S -X POST -H 'Content-type:application/json' --data-binary '{
            "add-copy-field":{"source":
                "txtimagename5_s",
                "dest": [ "images_ss" ]}
        }' $SOLR_CORE_URL/schema
        curl -s -S -X POST -H 'Content-type:application/json' --data-binary '{
            "add-copy-field":{"source":
                "txtdrawingname_s",
                "dest": [ "images_ss" ]}
        }' $SOLR_CORE_URL/schema
    fi
}

for SOLR_CORE in $SOLR_CORES
do
    SOLR_CORE_URL="http://localhost:$SOLR_PORT/solr/$SOLR_CORE"
    # ====================
    # Recreate the Solr core and update the solrconfig.xml file
    # ====================
    echo "Recreating core: $SOLR_CORE_URL ..."
    $SOLR_CMD delete -c $SOLR_CORE
    $SOLR_CMD create -c $SOLR_CORE
    SOLR_RELOAD_URL="http://localhost:$SOLR_PORT/solr/admin/cores?action=RELOAD&core=$SOLR_CORE"

    echo "Updating config files..."
    echo "$SOLR_RELOAD_URL"

    echo "Loading new config..."
    define_field_types
    define_fields
    define_dynamic_fields
    define_special_fields ${SOLR_CORE}
    create_copy_fields ${SOLR_CORE}.fields.txt
    create_synonyms ${SOLR_CORE}.synonyms.txt

    # add all these to the 'catch-all' field
    copy_fields '*_s'   'text'
    copy_fields '*_ss'  'text'
    copy_fields '*_txt' 'text'

    echo "Reloading core ${SOLR_CORE}..."
    curl -s -S "$SOLR_RELOAD_URL"
done

# ====================
# Use this to export all the *actual* fields defined in the code
# *after* importing data
#
# curl -s -S $SOLR_CORE_URL/admin/luke?numTerms=0 > $SOLR_CORE_URL.luke7.xml
# ====================
