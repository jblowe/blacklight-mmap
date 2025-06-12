# holder for global variables and other parameters
class parmz:
    pass


# TODO: this needs a good deal of cleanup

parmz.TITLE = 'MMAP'
parmz.CITATION = 'mmap project'
parmz.BANNER = 'MMAP banner'
parmz.BANNER_COLOR = '#EC5800'
parmz.SOLR_CORE = 'mmap-public'
parmz.SOLR_SERVER = 'http://localhost:8983'
parmz.FACET_LIMIT = 100
parmz.FACET_MINCOUNT = 2
parmz.ROW_LIMITS = [10, 20, 30]
parmz.IMAGE_FIELD = 'IMAGENAME_s'
parmz.TITLE_FIELD = 'mmap_artifact_id_s'
parmz.PORT = 3011

FIELD_DEFINITIONS = {}

parmz.SEARCH = [
    ('Artifact Id', 'mmap_artifact_id_s'),
    ('Site Name', 'site_name_s'),
    ('Date Discovered', 'date_discovered_s'),
    ('Bag Id', 'bag_id_s'),
    ('Artifact Condition', 'artifact_condition_s'),
    ('Artifact Class', 'artifact_class_s'),
    ('Maximum Dimension', 'maximum_dimension_s'),
    ('Weight', 'weight_s'),
    ('Count', 'count_s'),
    ('Burial No', 'burial_no_s'),
    ('Period', 'period_s'),
    ('Material', 'material_s'),
    ('Comments', 'comments_s'),
    ('Bur Phase', 'bur_phase_s'),
    ('Level', 'level_s'),
    ('Depcontext', 'depcontext_s'),
    ('Square', 'square_s'),
    ('Quad', 'quad_s'),
    ('Layer', 'layer_s'),
    ('Feano', 'feano_s'),
    ('Featype', 'featype_s'),
    ('Burassoc', 'burassoc_s'),
    ('Blocation', 'blocation_s'),
    ('Bodypart', 'bodypart_s'),
    ('Sherdample? S', 'sherd_sample?_s'),
    ('Sherdamp Location S', 'sherd_samp_location_s'),
    ('Thinection S', 'thin_section_s'),
    ('Ts Location', 'ts_location_s'),
    ('Ts No', 'ts_no_s'),
    ('Metample S', 'met_sample_s'),
    ('Metamp Loc S', 'met_samp_loc_s'),
    ('Sample Comment', 'sample_comment_s'),
    ('Artloc', 'artloc_s'),
    ('Conserved', 'conserved_s'),
    ('Glassample S', 'glass_sample_s'),
    ('Glamp S', 'gl_samp_s'),
    ('Gl Tech', 'gl_tech_s'),
    ('Gl Analy Date', 'gl_analy_date_s'),
    ('Entered By', 'entered_by_s'),
    ('Initial Date', 'initial_date_s'),
    ('Date Last Modified', 'date_last_modified_s'),
    ('Txtimagename1', 'txtimagename1_s'),
    ('Txtimagename2', 'txtimagename2_s'),
    ('Txtimagename3', 'txtimagename3_s'),
    ('Txtimagename4', 'txtimagename4_s'),
    ('Txtimagename5', 'txtimagename5_s'),
    ('Txtdrawingname', 'txtdrawingname_s'),
]
FIELD_DEFINITIONS['SEARCH'] = parmz.SEARCH

parmz.FACETS = [
    ('Site Name', 'site_name_s'),
    ('Date Discovered', 'date_discovered_s'),
    ('Bag Id', 'bag_id_s'),
    ('Artifact Class', 'artifact_class_s'),
    ('Period', 'period_s'),
    ('Material', 'material_s'),
    ('Bur Phase', 'bur_phase_s'),
    ('Level', 'level_s'),
    ('Square', 'square_s'),
    ('Quad', 'quad_s'),
    ('Layer', 'layer_s'),
    ('Feano', 'feano_s'),
    ('Featype', 'featype_s'),
    ('Flag For Check', 'flag_for_check_s')
]

parmz.LIST = [
    ('Artifact Id', 'mmap_artifact_id_s'),
    ('Site Name', 'site_name_s'),
    ('Date Discovered', 'date_discovered_s'),
    ('Bag Id', 'bag_id_s'),
    ('Artifact Condition', 'artifact_condition_s'),
    ('Artifact Class', 'artifact_class_s'),
    ('Maximum Dimension', 'maximum_dimension_s'),
    ('Weight', 'weight_s'),
    ('Count', 'count_s'),
    ('Burial No', 'burial_no_s'),
    ('Period', 'period_s'),
    ('Material', 'material_s'),
    ('Comments', 'comments_s'),
    ('Bur Phase', 'bur_phase_s'),
    ('Level', 'level_s'),
    ('Depcontext', 'depcontext_s'),
    ('Square', 'square_s'),
    ('Quad', 'quad_s'),
    ('Layer', 'layer_s'),
    ('Feano', 'feano_s'),
    ('Featype', 'featype_s'),
    ('Burassoc', 'burassoc_s'),
    ('Blocation', 'blocation_s'),
    ('Bodypart', 'bodypart_s'),
    ('Sherdample? S', 'sherd_sample?_s'),
    ('Sherdamp Location S', 'sherd_samp_location_s'),
    ('Thinection S', 'thin_section_s'),
    ('Ts Location', 'ts_location_s'),
    ('Ts No', 'ts_no_s'),
    ('Metample S', 'met_sample_s'),
    ('Metamp Loc S', 'met_samp_loc_s'),
    ('Sample Comment', 'sample_comment_s'),
    ('Artloc', 'artloc_s'),
    ('Conserved', 'conserved_s'),
    ('Glassample S', 'glass_sample_s'),
    ('Glamp S', 'gl_samp_s'),
    ('Gl Tech', 'gl_tech_s'),
    ('Gl Analy Date', 'gl_analy_date_s'),
    ('Entered By', 'entered_by_s'),
    ('Initial Date', 'initial_date_s'),
    ('Date Last Modified', 'date_last_modified_s'),
    ('Txtimagename1', 'txtimagename1_s'),
    ('Txtimagename2', 'txtimagename2_s'),
    ('Txtimagename3', 'txtimagename3_s'),
    ('Txtimagename4', 'txtimagename4_s'),
    ('Txtimagename5', 'txtimagename5_s'),
    ('Txtdrawingname', 'txtdrawingname_s'),
    ('Flag For Check', 'flag_for_check_s'),
]
FIELD_DEFINITIONS['LIST'] = parmz.LIST

parmz.TABLE = [
    ('Id', 'id'),
    ('Artifact Id', 'mmap_artifact_id_s'),
    ('Site Name', 'site_name_s'),
    # ('Bag Id', 'bag_id_s'),
    ('Artifact Class', 'artifact_class_s'),
    ('Maximum Dimension', 'maximum_dimension_s'),
    ('Weight', 'weight_s'),
    ('Count', 'count_s'),
    ('Burial No', 'burial_no_s'),
    ('Period', 'period_s'),
    ('Material', 'material_s'),
    ('Level', 'level_s'),
    ('Square', 'square_s'),
    ('Quad', 'quad_s'),
    ('Layer', 'layer_s'),
    ('Feano', 'feano_s'),
]
FIELD_DEFINITIONS['TABLE'] = parmz.TABLE

parmz.GALLERY = [
    ('Artifact Id', 'mmap_artifact_id_s'),
    ('Site Name', 'site_name_s'),
    ('Artifact Class', 'artifact_class_s'),
]
FIELD_DEFINITIONS['GALLERY'] = parmz.GALLERY

parmz.FULL = [
    ('Artifact Id', 'mmap_artifact_id_s'),
    ('Site Name', 'site_name_s'),
    ('Date Discovered', 'date_discovered_s'),
    ('Bag Id', 'bag_id_s'),
    ('Artifact Condition', 'artifact_condition_s'),
    ('Artifact Class', 'artifact_class_s'),
    ('Maximum Dimension', 'maximum_dimension_s'),
    ('Weight', 'weight_s'),
    ('Count', 'count_s'),
    ('Burial No', 'burial_no_s'),
    ('Period', 'period_s'),
    ('Material', 'material_s'),
    ('Comments', 'comments_s'),
    ('Bur Phase', 'bur_phase_s'),
    ('Level', 'level_s'),
    ('Depcontext', 'depcontext_s'),
    ('Square', 'square_s'),
    ('Quad', 'quad_s'),
    ('Layer', 'layer_s'),
    ('Feano', 'feano_s'),
    ('Featype', 'featype_s'),
    ('Burassoc', 'burassoc_s'),
    ('Blocation', 'blocation_s'),
    ('Bodypart', 'bodypart_s'),
    ('Sherdample? S', 'sherd_sample?_s'),
    ('Sherdamp Location S', 'sherd_samp_location_s'),
    ('Thinection S', 'thin_section_s'),
    ('Ts Location', 'ts_location_s'),
    ('Ts No', 'ts_no_s'),
    ('Metample S', 'met_sample_s'),
    ('Metamp Loc S', 'met_samp_loc_s'),
    ('Sample Comment', 'sample_comment_s'),
    ('Artloc', 'artloc_s'),
    ('Conserved', 'conserved_s'),
    ('Glassample S', 'glass_sample_s'),
    ('Glamp S', 'gl_samp_s'),
    ('Gl Tech', 'gl_tech_s'),
    ('Gl Analy Date', 'gl_analy_date_s'),
    ('Entered By', 'entered_by_s'),
    ('Initial Date', 'initial_date_s'),
    ('Date Last Modified', 'date_last_modified_s'),
    ('Txtimagename1', 'txtimagename1_s'),
    ('Txtimagename2', 'txtimagename2_s'),
    ('Txtimagename3', 'txtimagename3_s'),
    ('Txtimagename4', 'txtimagename4_s'),
    ('Txtimagename5', 'txtimagename5_s'),
    ('Txtdrawingname', 'txtdrawingname_s'),
    ('Flag For Check', 'flag_for_check_s'),
]
FIELD_DEFINITIONS['FULL'] = parmz.FULL

FIELD_DEFINITIONS['FACETS'] = parmz.FACETS
parmz.FACET_LABELS = {}
for f in parmz.FACETS:
    parmz.FACET_LABELS[f[1]] = f[0]

parmz.LAYOUTS = 'SEARCH FACETS LIST TABLE GALLERY FULL'.split(' ')

