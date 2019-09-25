echo "[Create sqlGraph start!]"
clickhouse client --multiquery --query="
drop database if exists EEDGraphSingular_v16;
create database if not exists EEDGraphSingular_v16;

use EEDGraphSingular_v16;

drop table if exists document;
drop table if exists event;
drop table if exists relations;
drop table if exists relationGraph;

create table if not exists entity (
Entity_id String Key,
Entity_name String,
Chinese_name String,
Entity_type String,
meta_type String
) engine=V;

create table if not exists document (
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

create table if not exists event (
Entity_id String Key,
doc_id String,
event_type String,
event_subtype String,
description String,
publish_time String,
time_list String,
entity_list String,
location_list String,
Entity_type String,
meta_type String
) engine=V;

create table EEDGraphSingular_v16.document_event( \
Head_id VS(EEDGraphSingular_v16.document), \
Tail VD(EEDGraphSingular_v16.event), \
id String, \
relation_id String, \
type String
) engine=E;

create table EEDGraphSingular_v16.entity_entity( \
Head_id VS(EEDGraphSingular_v16.entity), \
Tail VD(EEDGraphSingular_v16.entity), \
id String, \
relation_id String, \
type String
) engine=E;

create table EEDGraphSingular_v16.entity_document( \
Head_id VS(EEDGraphSingular_v16.entity), \
Tail VD(EEDGraphSingular_v16.document), \
id String, \
relation_id String, \
type String
) engine=E;

create table EEDGraphSingular_v16.entity_event( \
Head_id VS(EEDGraphSingular_v16.entity), \
Tail VD(EEDGraphSingular_v16.event), \
id String, \
relation_id String, \
type String
) engine=E;

create table EEDGraphSingular_v16.kr_case( \
Head_id VS(EEDGraphSingular_v16.entity), \
Tail VD(EEDGraphSingular_v16.entity), \
id String, \
relation_id String, \
type String
) engine=E;

create table EEDGraphSingular_v16.relation_darpa( \
Head_id VS(EEDGraphSingular_v16.entity), \
Tail VD(EEDGraphSingular_v16.entity), \
id String, \
relation_id String, \
type String
) engine=E;

";

clickhouse client --format_csv_allow_single_quotes 0 --format_csv_allow_double_quotes 0 --query="INSERT INTO EEDGraphSingular_v16.entity FORMAT CSVWithNames" < ./entity_v2.csv;
clickhouse client --format_csv_allow_single_quotes 0 --format_csv_allow_double_quotes 0 --query="INSERT INTO EEDGraphSingular_v16.entity FORMAT CSVWithNames" < ./QBDATA_new_entity_v2.csv;
clickhouse client --format_csv_allow_single_quotes 1 --format_csv_allow_double_quotes 1 --query="INSERT INTO EEDGraphSingular_v16.event FORMAT CSVWithNames" < ./csv/event.csv;
clickhouse client --query="INSERT INTO EEDGraphSingular_v16.document FORMAT CSVWithNames" < ./csv/document.csv;
# table of points to insert!
clickhouse client --multiquery --query="
use EEDGraphSingular_v16;
insert into entity select s,'','','other','entity' from file('/home/sqlgraph/ssd/ssd_0625/csv/entity_event_v2.csv',CSV,'s String, d String, a String, b String, c String');
insert into entity select s,'','','other','entity' from file('/home/sqlgraph/ssd/ssd_0625/csv/entity_document_v2.csv',CSV,'s String, d String, a String, b String, c String');
insert into entity select s,'','','other','entity' from file('/home/sqlgraph/ssd/ssd_0625/relation_entity_singular_v2.csv',CSV,'s String, d String, a String, b String, c String');
insert into entity select d,'','','other','entity' from file('/home/sqlgraph/ssd/ssd_0625/relation_entity_singular_v2.csv',CSV,'s String, d String, a String, b String, c String');
insert into entity select s,'','','other','entity' from file('/home/sqlgraph/ssd/ssd_0625/kr_case_singular_v2.csv',CSV,'s String, d String, a String, b String, c String');
insert into entity select d,'','','other','entity' from file('/home/sqlgraph/ssd/ssd_0625/kr_case_singular_v2.csv',CSV,'s String, d String, a String, b String, c String');
insert into document select s,'','','','','','','','','' from file('/home/sqlgraph/ssd/ssd_0625/csv/document_event_v2.csv',CSV,'s String, d String, a String, b String, c String');"

clickhouse client --query="INSERT INTO EEDGraphSingular_v16.entity_event FORMAT CSVWithNames" < ./csv/entity_event_v2.csv;
clickhouse client --query="INSERT INTO EEDGraphSingular_v16.entity_document FORMAT CSVWithNames" < ./csv/entity_document_v2.csv;
clickhouse client --query="INSERT INTO EEDGraphSingular_v16.document_event FORMAT CSVWithNames" < ./csv/document_event_v2.csv;
clickhouse client --query="INSERT INTO EEDGraphSingular_v16.entity_entity FORMAT CSVWithNames" < ./relation_entity_singular_v2.csv;
clickhouse client --query="INSERT INTO EEDGraphSingular_v16.kr_case FORMAT CSVWithNames" < ./kr_case_singular_v2.csv;
# edge table to be inserted

clickhouse client --multiquery --query="
use EEDGraphSingular_v16;

drop table if exists relationGraph;

create symmetric graph relationGraph populate \
as edgeGroup(document_event, entity_document, entity_entity, entity_event, kr_case, relation_darpa);

load property relationGraph;
"
echo "[Create sqlGraph end!]"
