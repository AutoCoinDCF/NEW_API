echo "[Create sqlGraph start!]"

clickhouse client --multiquery --query="
use EEDGraphSingular_v16;
create table set_document_task_id (
Entity_id String Key,
raw_id String,
channel String,
site_name String,
title String,
publish_time String,
topic String,
entity_list String,
Entity_type String,
meta_type String
) engine=V;

create table EEDGraphSingular_v16.set_relation_task_id(
Head_id VS(EEDGraphSingular_v16.set_document_task_id),
Tail VD(EEDGraphSingular_v16.entity),
id String,
relation_id String,
type String
) engine=E;
";

clickhouse client --query="INSERT INTO EEDGraphSingular_v16.set_document_task_id FORMAT CSVWithNames" < /home/sqlgraph/ssd/search_script/csv/set_document_task_id.csv;
clickhouse client --query="INSERT INTO EEDGraphSingular_v16.set_relation_task_id FORMAT CSVWithNames" < /home/sqlgraph/ssd/search_script/csv/set_relation_task_id.csv;

clickhouse client --multiquery --query="
use EEDGraphSingular_v16;
create symmetric graph relationGraph_v2
as edgeGroup(document_event, entity_document, entity_entity, entity_event, kr_case, need_edge);
refresh relationGraph_v2 full;
truncate table if exists relationGraph;
drop table if exists relationGraph;
rename table relationGraph_v2 to relationGraph;
"
echo "[Create sqlGraph end!]"
