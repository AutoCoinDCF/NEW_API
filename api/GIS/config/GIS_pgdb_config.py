dataBaseConfig=[
    # {"tableName":'world_states_countries',"idSign":"world_states_countries_postgis","IdField":"id","queryFields":['id','country','enname'],"type":"country"},
    # {"tableName":'world_states_provinces',"idSign":"world_states_provinces_postgis","IdField":"objectid","queryFields":['objectid','name','enname'],"type":"province"}]
    {"tableName":'country_osm',"IdField":"gid","queryFields":['gid','zhname','enname'],"type":"country"},
    {"tableName":'province_osm',"IdField":"gid","queryFields":['gid','zhname','enname'],"type":"province"}
]