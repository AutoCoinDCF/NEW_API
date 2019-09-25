#!/bin/bash

echo "[Create sqlGraph start!]"
clickhouse client --multiquery --query="
create database if not exists EventGraph2;
use EventGraph2;
drop table if exists human;
drop table if exists administrative;
drop table if exists organization;
drop table if exists occupation;
drop table if exists document;
drop table if exists event;
drop table if exists warship;
drop table if exists relations;
drop table if exists relationGraph;
create table if not exists human (
entity_id String,
entity_name String,
chinese_name String,
entity_type String,
image String,
meta_type String
) engine=MergeTree order by entity_id; 

create table if not exists administrative (
entity_id String,
entity_name String,
chinese_name String,
entity_type String,
image String,
meta_type String
) engine=MergeTree order by entity_id; 

create table if not exists organization (
entity_id String,
entity_name String,
chinese_name String,
entity_type String,
image String,
meta_type String
) engine=MergeTree order by entity_id;

create table if not exists occupation (
entity_id String,
entity_name String,
entity_type String,
meta_type String
) engine=MergeTree order by entity_id;

create table if not exists warship (
entity_id String,
entity_name String,
chinese_name String,
entity_type String,
image String,
meta_type String
) engine=MergeTree order by entity_id;

create table if not exists document (
entity_id String,
adp String,
author String,
sent String,
title String,
url String,
entity_type String,
meta_type String
) engine=MergeTree order by entity_id;

create table if not exists event (
entity_id String,
event_type String,
event_subtype String,
time_list String,
location_list String,
meta_type String
) engine=MergeTree order by entity_id;

create table if not exists relations (
id String,
start_id String,
end_id String,
type String
) engine=MergeTree order by id;
";

clickhouse client --format_csv_allow_single_quotes 0 --format_csv_allow_double_quotes 0 --query="INSERT INTO EventGraph2.human FORMAT CSVWithNames" < ./event/new_human.csv;
clickhouse client --format_csv_allow_single_quotes 0 --format_csv_allow_double_quotes 0 --query="INSERT INTO EventGraph2.organization FORMAT CSVWithNames" < ./event/new_organization.csv;
clickhouse client --format_csv_allow_single_quotes 0 --format_csv_allow_double_quotes 0 --query="INSERT INTO EventGraph2.administrative FORMAT CSVWithNames" < ./event/new_administrative.csv;
clickhouse client --format_csv_allow_single_quotes 0 --format_csv_allow_double_quotes 0 --query="INSERT INTO EventGraph2.occupation FORMAT CSVWithNames" < ./event/occupation.csv;
clickhouse client --format_csv_allow_single_quotes 0 --format_csv_allow_double_quotes 0 --query="INSERT INTO EventGraph2.warship FORMAT CSVWithNames" < ./event/warship.csv;
clickhouse client --query="INSERT INTO EventGraph2.event FORMAT CSVWithNames" < ./event/event.csv;
clickhouse client --format_csv_allow_single_quotes 0 --query="INSERT INTO EventGraph2.document FORMAT CSVWithNames" < ./event/document.csv;
clickhouse client --query="INSERT INTO EventGraph2.relations FORMAT CSVWithNames" < ./event/knowledge_relation.csv;
clickhouse client --query="INSERT INTO EventGraph2.relations FORMAT CSVWithNames" < ./event/relation.csv;

clickhouse client --multiquery --query="
use EventGraph2;
create table if not exists relationGraph(
id String,
type String
)engine=Loop;
insert into relationGraph select start_id, 
end_id, id, type from relations;
"

clickhouse client --multiquery --query="
use EventGraph2;
insert property relationGraph(
entity_name String,
chinese_name String,
entity_type String,
image String,
meta_type String
) select entity_id,entity_name,chinese_name,entity_type,image,meta_type
 from human;

insert property relationGraph(
entity_name String,
chinese_name String,
entity_type String,
image String,
meta_type String
) select entity_id,entity_name,chinese_name,entity_type,image,meta_type
 from administrative;

insert property relationGraph(
entity_name String,
chinese_name String,
entity_type String,
image String,
meta_type String
) select entity_id,entity_name,chinese_name,entity_type,image,meta_type
 from organization;

insert property relationGraph(
entity_name String,
entity_type String,
meta_type String
) select entity_id,entity_name,entity_type,meta_type
 from occupation;

insert property relationGraph(
entity_name String,
chinese_name String,
entity_type String,
image String,
meta_type String
) select entity_id,entity_name,chinese_name,entity_type,image,meta_type
 from warship;

insert property relationGraph(
adp String,
author String,
sent String,
title String,
url String,
entity_type String,
meta_type String
) select entity_id,adp,author,sent,title,url,entity_type,meta_type
 from document;

insert property relationGraph(
event_type String,
event_subtype String,
time_list String,
location_list String,
meta_type String
) select entity_id, event_type, event_subtype, time_list, location_list, meta_type
 from event;

"
echo "[Create sqlGraph end!]"
