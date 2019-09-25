#!/bin/bash

echo "[Create sqlGraph start!]"
clickhouse client --multiquery --query="
create database if not exists EEDGraphSingular_v16;

use EEDGraphSingular_v16;

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
raw_id String,
channel String,
i_sn String,
title String,
time String,
sentiment String,
topic String,
entity_list String,
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
relation_id String,
type String,
Tail String
) engine=MergeTree order by id;
";

clickhouse client --format_csv_allow_single_quotes 0 --format_csv_allow_double_quotes 0 --query="INSERT INTO EEDGraphSingular_v16.entity FORMAT CSVWithNames" < ./entity_v2.csv;
clickhouse client --format_csv_allow_single_quotes 0 --format_csv_allow_double_quotes 0 --query="INSERT INTO EEDGraphSingular_v16.entity FORMAT CSVWithNames" < ./QBDATA_new_entity_v2.csv;
clickhouse client --query="INSERT INTO EEDGraphSingular_v16.event FORMAT CSVWithNames" < ./csv/event.csv;
clickhouse client --format_csv_allow_single_quotes 0 --query="INSERT INTO EEDGraphSingular_v16.document FORMAT CSVWithNames" < ./csv/document.csv;
clickhouse client --query="INSERT INTO EEDGraphSingular_v16.relations FORMAT CSVWithNames" < ./csv/relation_singular.csv;
clickhouse client --query="INSERT INTO EEDGraphSingular_v16.relations FORMAT CSVWithNames" < ./relation_entity_singular.csv;
clickhouse client --query="INSERT INTO EEDGraphSingular_v16.relations FORMAT CSVWithNames" < ./kr_case_singular.csv;

clickhouse client --multiquery --query="
use EEDGraphSingular_v16;

drop table if exists relationGraph;

create table if not exists relationGraph(
id  String,
relation_id String,
type String
)engine=Loop;
insert into relationGraph select Head_id, Tail, id, relation_id, type from relations;
"

clickhouse client --multiquery --query="
use EEDGraphSingular_v16;
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
raw_id String,
channel String,
i_sn String,
title String,
time String,
sentiment String,
topic String,
entity_list String,
entity_type String,
meta_type String
) select entity_id,raw_id,channel,i_sn,title,time,sentiment,topic,entity_list,entity_type,meta_type
 from document;
"
echo "[Create sqlGraph end!]"
