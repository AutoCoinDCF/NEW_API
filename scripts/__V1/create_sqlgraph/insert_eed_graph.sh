echo "[Insert sqlGraph start!]"
use EEDGraph;
clickhouse client --query="INSERT INTO EEDGraph.relations FORMAT CSVWithNames" < ./kr_case.csv;

clickhouse client --multiquery --query="
use EEDGraph;

create table if not exists relationGraph(
id  String,
Relation_id String,
Relation_name String
)engine=Loop;
insert into relationGraph select Head_id, Tail, id, Relation_id, Relation_name from relations;
"
echo "[Insert sqlGraph end!]"