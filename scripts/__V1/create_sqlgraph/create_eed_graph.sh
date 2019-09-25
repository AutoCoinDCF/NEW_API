#!/bin/bash

echo "[Create sqlGraph start!]"
clickhouse client --multiquery --query="
create database if not exists EEDGraph;

use EEDGraph;

drop table if exists document;
drop table if exists event;
drop table if exists relations;
drop table if exists relationGraph;

create table if not exists entity (
entity_id String,
entity_name String,
chinese_name String,
entity_type String,
meta_type String
) engine=MergeTree order by entity_id;

create table if not exists document (
entity_id String,
adp String,
author String,
sent String,
pt String,
title String,
human_topic String,
url String,
entity_type String,
meta_type String
) engine=MergeTree order by entity_id;

create table if not exists event (
entity_id String,
doc_id String,
event_type String,
event_subtype String,
event_content String,
publish_time String,
time_list String,
entity_list String,
location_list String,
entity_type String,
meta_type String
) engine=MergeTree order by entity_id;


create table if not exists relations (
id String,
Head_id String,
Relation_id String,
Relation_name String,
Tail String
) engine=MergeTree order by id;
";

clickhouse client --format_csv_allow_single_quotes 0 --format_csv_allow_double_quotes 0 --query="INSERT INTO EEDGraph.entity FORMAT CSVWithNames" < ./new_csv/entity_new.csv;
clickhouse client --query="INSERT INTO EEDGraph.event FORMAT CSVWithNames" < ./new_csv/event.csv;
clickhouse client --format_csv_allow_single_quotes 0 --query="INSERT INTO EEDGraph.document FORMAT CSVWithNames" < ./new_csv/document.csv;
clickhouse client --query="INSERT INTO EEDGraph.relations FORMAT CSVWithNames" < ./relation.csv;
clickhouse client --query="INSERT INTO EEDGraph.relations FORMAT CSVWithNames" < ./relation_nq_all.csv;
clickhouse client --query="INSERT INTO EEDGraph.relations FORMAT CSVWithNames" < ./kr_case_new.csv;

clickhouse client --multiquery --query="
use EEDGraph;

drop table if exists relationGraph;

create table if not exists relationGraph(
id  String,
Relation_id String,
Relation_name String
)engine=Loop;
insert into relationGraph select Head_id, Tail, id, Relation_id, Relation_name from relations;
"

clickhouse client --multiquery --query="
use EEDGraph;
insert property relationGraph(
entity_name String,
chinese_name String,
entity_type String,
meta_type String
) select entity_id,entity_name,chinese_name,entity_type,meta_type
 from entity;

insert property relationGraph(
doc_id String,
event_type String,
event_subtype String,
event_content String,
publish_time String,
time_list String,
entity_list String,
location_list String,
entity_type String,
meta_type String
) select entity_id,doc_id,event_type,event_subtype,event_content,publish_time,time_list,entity_list,location_list,entity_type,meta_type
 from event;


insert property relationGraph(
adp String,
author String,
sent String,
pt String,
title String,
human_topic String,
url String,
entity_type String,
meta_type String
) select entity_id,adp,author,sent,pt,title,human_topic,url,entity_type,meta_type
 from document;
"
echo "[Create sqlGraph end!]"
