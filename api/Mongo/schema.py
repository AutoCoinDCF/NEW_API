'''  schema.py: 数据库模板文件 

@author: shishidun
@Date: 2019-06-0620
@reference:
1）此配置页面为mongo接口和ES接口code中要用到的字段，针对与显示的字段单独配置，当前见config_es_rough_query_filter.py;
2）关系接口不需要在项目中配置字段，可根据此页面的mongo配置建点边图即可.
'''

# 事件表.字段类型待添加
event_schema = {
    '_id': '_id',
    'doc_id': 'doc_id',
    'meta_type': 'meta_type',
    'event_type': 'event_type',
    'event_subtype': 'event_subtype',
    'event_content': 'event_content',
    'entity_list': 'entity_list',
    'time_list': 'time_list',
    'location_list': 'location_list',
    'publish_time': 'publish_time'
}

# 文档表
document_schema = {
    '_id': '_id',
    'meta_type': 'meta_type',
    'channel': 'channel',
    'site_name': 'site_name',
    'title': 'title',
    'content': 'content',
    'publish_time': 'publish_time',
    'document_attribute': 'document_attribute',
    'topic': 'topic',
    'entity_list': 'entity_list',
    'keywords': 'keywords',
    'ner': 'ner',
    'pos': 'pos',
    'sentiment': 'sentiment'
}

# 实体表
entity_schema = {
    '_id': '_id',
    'Entity_id': 'Entity_id',
    'Entity_name': 'Entity_name',
    'Chinese_name': 'Chinese_name',
    'Entity_type': 'Entity_type',
    'population': 'population',
    'area': 'area',

    'English_text': 'English_text',
    'Chinese_text': 'Chinese_text'
}
