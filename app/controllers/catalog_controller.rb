# frozen_string_literal: true
class CatalogController < ApplicationController

  include Blacklight::Catalog

  configure_blacklight do |config|
    config.view.gallery(document_component: Blacklight::Gallery::DocumentComponent, icon: Blacklight::Gallery::Icons::GalleryComponent)
    config.show.tile_source_field = :content_metadata_image_iiif_info_ssm
    config.show.partials.insert(1, :openseadragon)

    #config.view.gallery(document_component: Blacklight::Gallery::DocumentComponent)

    # disable these three document action until we have resources to configure them to work
    config.show.document_actions.delete(:citation)
    config.show.document_actions.delete(:sms)
    config.show.document_actions.delete(:email)

    # config.add_results_document_tool(:bookmark, partial: 'bookmark_control', if: :render_bookmarks_control?)

    config.add_results_collection_tool(:sort_widget)
    config.add_results_collection_tool(:per_page_widget)
    config.add_results_collection_tool(:view_type_group)

    # config.add_show_tools_partial(:bookmark, partial: 'bookmark_control', if: :render_bookmarks_control?)
    # config.add_nav_action(:bookmark, partial: 'blacklight/nav/bookmark', if: :render_bookmarks_control?)
    config.add_nav_action(:search_history, partial: 'blacklight/nav/search_history')

    # solr path which will be added to solr base url before the other solr params.
    config.solr_path = 'select'
    config.document_solr_path = 'select'

    # items to show per page, each number in the array represent another option to choose from.
    config.per_page = [80,160,240,1000]

    config.default_facet_limit = 10

    ## Class for sending and receiving requests from a search index
    # config.repository_class = Blacklight::Solr::Repository
    #
    ## Class for converting Blacklight's url parameters to into request parameters for the search index
    # config.search_builder_class = ::SearchBuilder
    #
    ## Model that maps search index responses to the blacklight response model
    # config.response_model = Blacklight::Solr::Response

    ## Default parameters to send to solr for all search-like requests. See also SearchBuilder#processed_parameters
    #
    # customizations to support existing Solr cores
    config.default_solr_params = {
        'rows': 12,
        'facet.mincount': 1,
        'q.alt': '*:*',
        'defType': 'edismax',
        'df': 'text',
        'q.op': 'AND',
        'q.fl': '*,score'
    }

    # solr path which will be added to solr base url before the other solr params.
    # config.solr_path = 'select'

    ## Default parameters to send on single-document requests to Solr. These settings are the Blackligt defaults (see SearchHelper#solr_doc_params) or
    ## parameters included in the Blacklight-jetty document requestHandler.
    #
    config.default_document_solr_params = {
        qt: 'document',
        #  ## These are hard-coded in the blacklight 'document' requestHandler
        #  # fl: '*',
        #  # rows: 1,
        # this is needed for our Solr services
        q: '{!term f=id v=$id}'
    }

    # solr field configuration for search results/index views
    # list of images is hardcoded for both index and show displays
    #{index_title}
    config.index.thumbnail_field = 'THUMBNAIL_s'

    # solr field configuration for document/show views
    #{show_title}
    config.show.thumbnail_field = 'THUMBNAIL_s'

    # Have BL send all facet field names to Solr, which has been the default
    # previously. Simply remove these lines if you'd rather use Solr request
    # handler defaults, or have no facets.
    config.add_facet_fields_to_solr_request!

    # use existing "catchall" field called text
    # config.add_search_field 'text', label: 'Any field'
    config.spell_max = 5

    # SEARCH FIELDS
    config.add_search_field 'text', label: 'Any field'

    [
       ['mmap_artifact_id_s'     'Artifact Id'],
       ['site_name_s'     'Site Name'],
       ['date_discovered_s'     'Date Discovered'],
       ['bag_id_s'     'Bag Id'],
       ['artifact_condition_s'     'Artifact Condition'],
       ['artifact_class_s'     'Artifact Class'],
       ['maximum_dimension_s'     'Maximum Dimension'],
       ['weight_s'     'Weight'],
       ['count_s'     'Count'],
       ['burial_no_s'     'Burial No'],
       ['period_s'     'Period'],
       ['material_s'     'Material'],
       ['comments_s'     'Comments'],
       ['bur_phase_s'     'Bur Phase'],
       ['level_s'     'Level'],
       ['depcontext_s'     'Depcontext'],
       ['square_s'     'Square'],
       ['quad_s'     'Quad'],
       ['layer_s'     'Layer'],
       ['feano_s'     'Feano'],
       ['featype_s'     'Featype']
      ].each do |search_field|
      config.add_search_field(search_field[0]) do |field|
        field.label = search_field[1]
        #field.solr_parameters = { :'spellcheck.dictionary' => search_field[0] }
        field.solr_parameters = {
          qf: search_field[0],
          pf: search_field[0],
          op: 'AND'
        }
      end
    end

    # Configuration for autocomplete suggestor
    config.autocomplete_enabled = false
    config.autocomplete_path = 'suggest'

    # FACET FIELDS
     config.add_facet_field  'site_name_s', label: 'Site Name', limit: true
     config.add_facet_field  'date_discovered_s', label: 'Date Discovered', limit: true
     config.add_facet_field  'bag_id_s', label: 'Bag Id', limit: true
     config.add_facet_field  'artifact_class_s', label: 'Artifact Class', limit: true
     config.add_facet_field  'period_s', label: 'Period', limit: true
     config.add_facet_field  'material_s', label: 'Material', limit: true
     config.add_facet_field  'bur_phase_s', label: 'Bur Phase', limit: true
     config.add_facet_field  'level_s', label: 'Level', limit: true
     config.add_facet_field  'square_s', label: 'Square', limit: true
     config.add_facet_field  'quad_s', label: 'Quad', limit: true
     config.add_facet_field  'layer_s', label: 'Layer', limit: true
     config.add_facet_field  'feano_s', label: 'Feano', limit: true
     config.add_facet_field  'featype_s', label: 'Featype', limit: true
     config.add_facet_field  'flag_for_check_s', label: 'Flag For Check', limit: true

    # INDEX DISPLAY
     config.add_index_field  'id', label: 'Id'
     config.add_index_field  'mmap_artifact_id_s', label: 'Artifact Id'
     config.add_index_field  'site_name_s', label: 'Site Name'
     config.add_index_field  'bag_id_s', label: 'Bag Id'
     config.add_index_field  'artifact_class_s', label: 'Artifact Class'
     config.add_index_field  'maximum_dimension_s', label: 'Maximum Dimension'
     config.add_index_field  'weight_s', label: 'Weight'
     config.add_index_field  'count_s', label: 'Count'
     config.add_index_field  'burial_no_s', label: 'Burial No'
     config.add_index_field  'period_s', label: 'Period'
     config.add_index_field  'material_s', label: 'Material'
     config.add_index_field  'level_s', label: 'Level'
     config.add_index_field  'square_s', label: 'Square'
     config.add_index_field  'quad_s', label: 'Quad'
     config.add_index_field  'layer_s', label: 'Layer'
     config.add_index_field  'feano_s', label: 'Feano'


    # SHOW DISPLAY
     config.add_show_field  'mmap_artifact_id_s', label: 'Artifact Id'
     config.add_show_field  'site_name_s', label: 'Site Name'
     config.add_show_field  'date_discovered_s', label: 'Date Discovered'
     config.add_show_field  'bag_id_s', label: 'Bag Id'
     config.add_show_field  'artifact_condition_s', label: 'Artifact Condition'
     config.add_show_field  'artifact_class_s', label: 'Artifact Class'
     config.add_show_field  'maximum_dimension_s', label: 'Maximum Dimension'
     config.add_show_field  'weight_s', label: 'Weight'
     config.add_show_field  'count_s', label: 'Count'
     config.add_show_field  'burial_no_s', label: 'Burial No'
     config.add_show_field  'period_s', label: 'Period'
     config.add_show_field  'material_s', label: 'Material'
     config.add_show_field  'comments_s', label: 'Comments'
     config.add_show_field  'bur_phase_s', label: 'Bur Phase'
     config.add_show_field  'level_s', label: 'Level'
     config.add_show_field  'depcontext_s', label: 'Depcontext'
     config.add_show_field  'square_s', label: 'Square'
     config.add_show_field  'quad_s', label: 'Quad'
     config.add_show_field  'layer_s', label: 'Layer'
     config.add_show_field  'feano_s', label: 'Feano'
     config.add_show_field  'featype_s', label: 'Featype'
     config.add_show_field  'burassoc_s', label: 'Burassoc'
     config.add_show_field  'blocation_s', label: 'Blocation'
     config.add_show_field  'bodypart_s', label: 'Bodypart'
     config.add_show_field  'sherd_sample?_s', label: 'Sherdample? S'
     config.add_show_field  'sherd_samp_location_s', label: 'Sherdamp Location S'
     config.add_show_field  'thin_section_s', label: 'Thinection S'
     config.add_show_field  'ts_location_s', label: 'Ts Location'
     config.add_show_field  'ts_no_s', label: 'Ts No'
     config.add_show_field  'met_sample_s', label: 'Metample S'
     config.add_show_field  'met_samp_loc_s', label: 'Metamp Loc S'
     config.add_show_field  'sample_comment_s', label: 'Sample Comment'
     config.add_show_field  'artloc_s', label: 'Artloc'
     config.add_show_field  'conserved_s', label: 'Conserved'
     config.add_show_field  'glass_sample_s', label: 'Glassample S'
     config.add_show_field  'gl_samp_s', label: 'Glamp S'
     config.add_show_field  'gl_tech_s', label: 'Gl Tech'
     config.add_show_field  'gl_analy_date_s', label: 'Gl Analy Date'
     config.add_show_field  'entered_by_s', label: 'Entered By'
     config.add_show_field  'initial_date_s', label: 'Initial Date'
     config.add_show_field  'date_last_modified_s', label: 'Date Last Modified'
     config.add_show_field  'txtimagename1_s', label: 'Txtimagename1'
     config.add_show_field  'txtimagename2_s', label: 'Txtimagename2'
     config.add_show_field  'txtimagename3_s', label: 'Txtimagename3'
     config.add_show_field  'txtimagename4_s', label: 'Txtimagename4'
     config.add_show_field  'txtimagename5_s', label: 'Txtimagename5'
     config.add_show_field  'txtdrawingname_s', label: 'Txtdrawingname'
     config.add_show_field  'flag_for_check_s', label: 'Flag For Check'


    # SORT FIELDS
    config.add_sort_field 'site_name_s asc', label: 'Site'
    config.add_sort_field 'bag_id_s asc', label: 'Bag ID'
    config.add_sort_field 'mmap_artifact_id_s asc', label: 'Artifact ID'

    # TITLE
    config.index.title_field = 'mmap_artifact_id_s'
    config.show.title_field = 'mmap_artifact_id_s'

  end
end
