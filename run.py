# -*- coding:utf8 -*-
"""This module prepares and runs the whole system.
nohup python -u run.py --webapi --webapi_config test --graphapi_config test --esapi_config test --es_search_config test >app.log 2>&1 &

nohup python -u run.py --webapi --webapi_config dev --graphapi_config test --esapi_config test --es_search_config test >app.log 2>&1 &

nohup python -u run.py --webapi --webapi_config dev-front-labeled-data --graphapi_config dev-front-labeled-data --esapi_config dev-front-labeled-data --es_search_config dev-front-labeled-data >app.log 2>&1 &

nohup python -u run.py --webapi --webapi_config dev_test --graphapi_config dev_test --esapi_config dev_test --es_search_config dev_test >app.log 2>&1 &

nohup python -u run.py --webapi --webapi_config dev --graphapi_config dev --esapi_config dev --es_search_config dev >app.log 2>&1 &

nohup python -u run.py --webapi --webapi_config test --graphapi_config dev_test --esapi_config dev_test --es_search_config dev_test >app.log 2>&1 &
"""

import os
import argparse
import logging
#from api.graph import test
#from api.graph.utility import select_utility
from api.graph.utility import graph_inquiry
from api.web.webapi import WebAPI
from api.configs.MiddleEndConfig import CONFIG
#from api.graph.application import test
#from api.graph import test_graph
#from api.graph.application import config_application
#from api.script import test_script


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser('Run QB AIP system')
    parser.add_argument('--prepare', action='store_true',
                        help='create the directories, prepare the dataset')
    parser.add_argument('--webapi', action='store_true',
                        help='web api applications')
    parser.add_argument('--webapi_config', type=str, choices=('test', 'dev', 'dev_test'), default='test',
                        help='set web api config: test or dev or product')
    parser.add_argument('--graphapi_config', type=str, choices=('test', 'dev', 'dev_test'), default='test',
                        help='set graph api config: test or dev or product')
    parser.add_argument('--esapi_config', type=str, choices=('test', 'dev', 'dev_test'), default='test',
                        help='set es api config: test or dev or product')
    parser.add_argument('--es_search_config', type=str, choices=('test', 'dev', 'dev_test'), default='test',
                        help='set es search config: test or dev or product')
    parser.add_argument('--graph', action='store_true',
                        help='graph operations, such as sql_to_select_out_neighbor graph')
    parser.add_argument('--es', action='store_true',
                        help='es operations')
    parser.add_argument('--event', action='store_true',
                        help='event operations')
    parser.add_argument('--gpu', type=str, default='0',
                        help='specify gpu device')
    # train settings
    train_settings = parser.add_argument_group('train settings')
    train_settings.add_argument('--optim', default='sgd',
                                help='optimizer type')
    train_settings.add_argument('--learning_rate', type=float, default=0.0001,
                                help='learning rate')
    train_settings.add_argument('--weight_decay', type=float, default=0,
                                help='weight decay')
    train_settings.add_argument('--dropout_keep_prob', type=float, default=1,
                                help='dropout keep rate')
    train_settings.add_argument('--batch_size', type=int, default=3,
                                help='train batch size')
    train_settings.add_argument('--epochs', type=int, default=10,
                                help='train epochs')
    train_settings.add_argument('--min_cnt', type=int, default=2,
                                help='tokens with frequency '
                                     'less than min_cnt is filtered')
    # model settings
    model_settings = parser.add_argument_group('model settings')
    model_settings.add_argument('--algo', choices=['sqlgraph', 'sql_to_select_out_neighbor'],
                                default='sqlgraph',
                                help='choose the algorithm to use')
    model_settings.add_argument('--embed_size', type=int, default=300,
                                help='size of the embeddings')
    model_settings.add_argument('--beta', type=float, default=100,
                                help=' parameter that balances the loss part')
    # path settings
    path_settings = parser.add_argument_group('path settings')
    path_settings.add_argument('--emb_files', nargs='+',
                               default=['../data/glove.6B/glove.6B.300d.txt'],
                               help='list of files that '
                                    'contain the preprocessed train data')
    path_settings.add_argument('--train_files', nargs='+',
                               default=['../data/demo/100_train.csv'],
                               help='list of files that '
                                    'contain the preprocessed train data')
    path_settings.add_argument('--dev_files', nargs='+',
                               default=['../data/demo/100_train.csv'],
                               help='list of files that '
                                    'contain the preprocessed dev data')
    path_settings.add_argument('--test_files', nargs='+',
                               default=['../data/demo/100_train.csv'],
                               help='list of files that '
                                    'contain the preprocessed test data')
    path_settings.add_argument('--vocab_dir', default='../data/vocab/',
                               help='the dir to save vocabulary')
    path_settings.add_argument('--model_dir', default='../data/models/',
                               help='the dir to store models')
    path_settings.add_argument('--result_dir', default='../data/results/',
                               help='the dir to output the results')
    path_settings.add_argument('--summary_dir', default='../data/summary/',
                               help='the dir to write tensorboard summary')
    path_settings.add_argument('--log_path',
                               help='path of the log file. '
                                    'If not set, logs are printed to console')
    path_settings.add_argument('--draw_path', default='.log/',
                               help='tensorboard')
    return parser.parse_args()


def prepare(args):
    """Check data, create the directories..."""
    logger = logging.getLogger("qbapi")
    logger.info('Start preparing data')
    return 0


def webapi(args):
    """Operate web api related things."""
    logger = logging.getLogger("qbapi")
    logger.info('Start web api')
    web_api = WebAPI()
    web_api.run()
    return 0


def graph(args):
    """Operate graph related things."""
    logger = logging.getLogger("qbapi")
    logger.info('Start process graph')

    graph_app = graph_inquiry.GraphApplication()
    data = graph_app.select_entity_by_name('Nero')
    #print('----------data 0:', data)
    #data['nodeIds'] = data["data"][0]["nodes"]
    str_data = {}
    str_data['nodeIds'] = ["Q1413", "Q23"]
    #data = graph_app.select_entity_by_id(str_data)
    #data = graph_app.select_neighbor_by_outid(str_data)
    #print('----------data 1:', data)
    data = graph_app.select_neighbor_by_id(str_data)
    #data = graph_app.select_neighbor_by_id('Q23')
    return 0


def es(args):
    """Operate ES related things."""
    logger = logging.getLogger("qbapi")
    logger.info('Start process es')
    return 0
    

def run():
    """Prepare and run the whole system."""
    args = parse_args()
    logger = logging.getLogger("qbapi")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if args.log_path:
        file_handler = logging.FileHandler(args.log_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger.info('Running with args : {}'.format(args))

    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu

    CONFIG.choose_config(WebAPI_choice=args.webapi_config,
                         GraphAPI_choice=args.graphapi_config,
                         ESAPI_choice=args.esapi_config,
                         ESSearch_choice=args.es_search_config)
    if args.prepare:
        prepare(args)
    if args.webapi:
        webapi(args)
    if args.graph:
        graph(args)
    if args.es:
        es(args)


if __name__ == '__main__':
    run()
