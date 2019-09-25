#!/bin/bash

clickhouse client --multiquery --query="
load EEDGraph.relationGraph;
load KnowledgeGraph.relationGraph;
load KnowledgeGraph2.relationGraph;
load BigDataAnalysis.relationGraph;
load EventGraph.EventEntityRelationGraph;
"
#load EventGraph2.relationGraph;
