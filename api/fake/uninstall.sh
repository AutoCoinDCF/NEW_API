# 最合理的版本但是数据库报错，跑不通
echo "[Create sqlGraph start!]"
clickhouse client --multiquery --query="
use EEDGraphSingular_v16;
drop table if exists set_relation_task_id;
drop table if exists set_document_task_id;
create symmetric graph relationGraph_v2
as edgeGroup(document_event, entity_document, entity_entity, entity_event, kr_caseneed_edge);
refresh relationGraph_v2 full;
truncate table if exists relationGraph;
drop table if exists relationGraph;
rename table relationGraph_v2 to relationGraph;
"
echo "[Create sqlGraph end!]"
