#!/bin/sh
python create_mongo_table_from_nlu_database.py
#nohup python create_sqlgraph_from_mongo_es.py >log 2>&1 &

curr_path=`pwd`
event_path=$curr_path"/event/"
echo $event_path
scp ${event_path}document.csv sqlgraph@10.60.1.143:data_test
scp ${event_path}event.csv sqlgraph@10.60.1.143:data_test
scp ${event_path}relation.csv sqlgraph@10.60.1.143:data_test
