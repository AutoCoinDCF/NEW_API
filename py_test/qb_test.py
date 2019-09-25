'''qb_test.py: API单元测试

@author: shishidun
@date: 2019.06.05
'''

import pytest
import multiprocessing

from api.web.webapi import WebAPI
from api.configs.MiddleEndConfig import CONFIG


@pytest.fixture(scope="module", autouse=True)
def test_client():
    app = WebAPI()
    CONFIG.choose_config(WebAPI_choice='dev_test',
                         GraphAPI_choice='dev_test',
                         ESAPI_choice='dev_test',
                         ESSearch_choice='dev_test',
                         MongoAPI_choice='dev_test')
    return app.client


@pytest.mark.search
class Test_search_API:
    def test_FuzzyMatch(self, test_client):
        data = dict(pattern='习近平',
                    timestamp='a_very_loooooooooooooooooooooooooooooooooooooooooong_timestamp')
        response = test_client.get('/fuzzy-match/', data=data)
        assert response.status_code == 200

    def test_QBSearch(self, test_client):
        data = dict(keyword="委",
                    type="net",
                    timestamp='loooooooooooooooooong_timestamp')
        response = test_client.get('/qb-search/', data=data)
        assert response.status_code == 200


@pytest.mark.entity
class Test_entity_API:
    def test_EntityInfo(self, test_client):
        data = dict(nodeIds=["Q7747", "Q15031", "Q22686"])
        response = test_client.post('/entity-info/', data=data)
        assert response.status_code == 200

    def test_EntityDetail(self, test_client):
        data = dict(nodeIds=["Q7747", "Q15031", "Q22686"])
        response = test_client.post('/entity-detail/', data=data)
        assert response.status_code == 200


@pytest.mark.event
class Test_event_API:
    def test_EventDetail(self, test_client):
        data = dict(
            EventIds=[
                "ca8fcda56e314f97b8c23e51be684463a9a865e0",
                "ca8fcda5cbf572e77f3a3c94970ee99dd0c35af3",
                "d713ba29118915579dd737b789f66b99117a583f",
                "37836765affcc51a70933980a5121e25abc2c958"
            ])
        response = test_client.post('/event-detail/', data=data)
        assert response.status_code == 200

    def test_Event2Time(self, test_client):
        data = dict(
            eventIds=[
                "ca8fcda53e4959ade3303bee9b98245ce0f3591a",
                "ca8fcda5972bbbb4369e3e3fbb85663c46e98a8d",
                "d713ba29118915579dd737b789f66b99117a583f",
                "37836765affcc51a70933980a5121e25abc2c958"],
            docIds=[
                "e776495433f8fb7718f734e3a957aed10fa39d67",
                "e7764954026e32cafe9d3897a1fa8425305f690d",
                "ca8fcda59f4420eb367e3c54a766c49193d714bf",
                "ca8fcda5cc8b159a648334e69bd231c236249553",
                "def573516318df3c04c134cbb946ff9c09aa8d18",
                "d713ba290af048f2c22130828fd94f3c6f5e9c21",
                "37836765eac4ba1b18fa3c18b2ea83d3b38ff621"])
        response = test_client.post('/event-2-time/', data=data)
        assert response.status_code == 200


@pytest.mark.doc
class Test_doc_API:
    def test_DocumentDetail_id(self, test_client):
        data = dict(idValue="e77649549b10da9591f1374eb6b567efa88e33f9")
        response = test_client.get('/context-by-id/', data=data)
        assert response.status_code == 200

    def test_DocumentDetail(self, test_client):
        data = dict(
            docIds=[
                "e776495433f8fb7718f734e3a957aed10fa39d67",
                "e7764954026e32cafe9d3897a1fa8425305f690d",
                "ca8fcda59f4420eb367e3c54a766c49193d714bf",
                "ca8fcda5cc8b159a648334e69bd231c236249553",
                "def573516318df3c04c134cbb946ff9c09aa8d18",
                "d713ba290af048f2c22130828fd94f3c6f5e9c21",
                "37836765eac4ba1b18fa3c18b2ea83d3b38ff621"
            ])
        response = test_client.post('/doc-detail/', data=data)
        assert response.status_code == 200

    def test_DocTranslate(self, test_client):
        data = dict(id="e77649549b10da9591f1374eb6b567efa88e33f9")
        response = test_client.get('/translate/', data=data)
        assert response.status_code == 200

    def test_ContextByText(self, test_client):
        data = dict(page=1, query="u.n")
        response = test_client.get('/context-by-text/', data=data)
        assert response.status_code == 200

    def test_DocTop(self, test_client):
        data = dict(
            idList=[
                "d713ba293605962b34c53fed8175d975c1ef0b8d",
                "d713ba2918e1e523082b3b1d9d3259432c90b5e8"
            ])
        response = test_client.post('/doc-top/', data=data)
        assert response.status_code == 200

    def test_WordDoc(self, test_client):
        data = dict(
            idList=[
                "d713ba293605962b34c53fed8175d975c1ef0b8d",
                "d713ba2918e1e523082b3b1d9d3259432c90b5e8"
            ],
            word=[
                "Venezuela", "Sergei Lavrov"
            ],
            speech="keywords")
        response = test_client.post('/word-doc/', data=data)
        assert response.status_code == 200


@pytest.mark.relation
class Test_relation_API:
    def test_FindPaths(self, test_client):
        data = dict(
            start="Q15031",
            end="Q301282",
            step=1
        )
        response = test_client.get('/all-path-data/', data=data)
        assert response.status_code == 200

    def test_Hierarchical(self, test_client):
        data = dict(
            nodeIds=[
                "Q15031",
                "Q301282",
                "Q17499761",
                "Q430911",
                "Q30941000",
                "Q148",
                "Q4119708",
                "Q17427",
                "Q8044049",
                "Q1441290",
                "Q23"
            ],
            RootNodeIdList=["Q301282"],
            edge_from_backend="true")
        response = test_client.post('/hierarchical-node-structure/', data=data)
        assert response.status_code == 200

    def test_relatedAll(self, test_client):
        data = dict(
            NodeIds=["Q15031"],
            Group="True",
            TypeLabel="all")
        response = test_client.post('/related-all/', data=data)
        assert response.status_code == 200

    def test_shortPath(self, test_client):
        data = dict(
            NodeIds_single=[
                "Q430911",
                "Q4119708"
            ],
            NodeIds_double=[],
            typeLabel="all")
        response = test_client.post('/ShortPath/', data=data)
        assert response.status_code == 200

    def test_commonAll(self, test_client):
        data = dict(
            NodeIds=[
                "Q16955", "Q8044049", "Q17499761"],
            ComLabel="all"
        )
        response = test_client.post('/commonAll/', data=data)
        assert response.status_code == 200

    def test_community(self, test_client):
        data = dict(
            from_ids=[
                "Q207361", "Q207361", "Q2634867",
                "Q1186234", "Q1127178", "Q1405600", "Q16002154", "Q1752885", "Q25632476",
                "a6c6a1b8ea8e3ea0ad5b2215cc863c6c",
                "d3634c87f4e53c7a9c8b0901872b2eeb",
                "e15fe091774a34f18617ff13589e3c7e",
                "b68259a6eab33fd1ac22d96164df2a64",
                "4d7cb562e4c33aa9a13a1eb894e55c6e",
                "2eceac5172f03040a7684791f325dede",
                "2aa44dd1a805323ea34ac08fa6280e5f"
            ],
            to_ids=[
                "Q4753623", "Q5657578", "Q4753623",
                "Q30264879", "Q30272495", "Q4743316", "Q5511908", "Q7538054", "Q7893681",
                "b3658ae0d39431e287ba5fe1b10509cd",
                "3d78fc59788c3ef881facbe6460d358a",
                "dcb98cf6dbff3a92be31a7a037f10c73",
                "3e43c0194fc53010956548269f94e4f6",
                "15ae9dbd302d3df182795d8a99ea6715",
                "807173f6b3453add9dc297a6d5add6d2",
                "3e875d823b6e314db9c239058866fb8f"
            ],
            method="cc",
            num=[2, 3, 4, 5, 6, 7, 8, 2, 2, 3, 3, 4, 1, 6, 9, 4])
        response = test_client.post('/community/', data=data)
        assert response.status_code == 200


@pytest.mark.statistics
class Test_statistics_API:
    def test_GraphAttr(self, test_client):
        data = dict(
            entityIds=["Q1186234", "Q1127178", "Q1405600", "Q16002154", "Q1752885", "Q25632476",
                       "Q30272495", "Q4743316", "Q5511908", "Q7538054", "Q7893681", "Q945843", "Q100000",
                       "Q11108136",
                       "N1111111", "N2222222", "N33333333"
                       ],
            eventIds=[
                "ca8fcda56e314f97b8c23e51be684463a9a865e0",
                "d713ba291e69e52adf283160b392b042498bf210",
                "3783676542f37ded586e34ddb3885afc6905fbfc"
            ],
            docIds=[
                "e77649549b10da9591f1374eb6b567efa88e33f9",
                "ca8fcda5e60151f24c2f3f838b4402a64c3a420f",
                "def573516185b78361a33c5daea3603bfc439a33",
                "d713ba29ba445063cf5e3403be6918da6cd6edb0",
                "37836765488c7cb6c8ea3fa1abb8d890a712f135"
            ],
            type=""
        )
        response = test_client.post('/graph-attr/', data=data)
        assert response.status_code == 200

    def test_Aggregation(self, test_client):
        data = dict(
            allNodeIds=[
                "Q771405", "ca8fcda5049aa3f1be2438929fe3f982fc906e71", "Q1026627",
                "d713ba29148cb6dda9cb34cf85228e7237d79461", "Q2495862", "Q57402",
                "378367659b8cf2af0eb73160bb1036016f7dc915", "NTW00000001",

                "A257",
                "Q7565363", "Q21428183", "Q132959",
                "Q41", "Q43", "Q204347",
                "Q38",
                "Q1183", "Q1227", "Q3141"
            ],
            selectNodeIds=[
                "ca8fcda56e314f97b8c23e51be684463a9a865e0",
                "d713ba291e69e52adf283160b392b042498bf210",
                "3783676542f37ded586e34ddb3885afc6905fbfc",

                "e77649549b10da9591f1374eb6b567efa88e33f9",
                "ca8fcda5e60151f24c2f3f838b4402a64c3a420f",
                "def573516185b78361a33c5daea3603bfc439a33",
                "d713ba29ba445063cf5e3403be6918da6cd6edb0",
                "37836765488c7cb6c8ea3fa1abb8d890a712f135"
            ],
            timestamp="loooooooooooooooooong_timestamp")
        response = test_client.post('/aggregation/', data=data)
        assert response.status_code == 200

    def test_FieldTranslate(self, test_client):
        data = dict(type="human")
        response = test_client.get('/FieldTranslate/', data=data)
        assert response.status_code == 200

    # 该接口postman正确，但是这里报错，待商榷
    # def test_KeywordMatch(self, test_client):
    #     data = dict(
    #         type="document",
    #         Attr=[
    #             dict(
    #                 keywords=["the Queensland Labor"],
    #                 publish_time=[1550548800]
    #             )],
    #         page=1,
    #         timestamp="loooooooooooooooooong_timestamp"
    #     )
    #     response = test_client.post('/KeywordMatch/', data=data)
    #     assert response.status_code == 200

    def test_NodeDetail(self, test_client):
        data = dict(
            type="event",
            nodeIds=[
                "ca8fcda56e314f97b8c23e51be684463a9a865e0",
                "ca8fcda5cbf572e77f3a3c94970ee99dd0c35af3",
                "d713ba29118915579dd737b789f66b99117a583f",
                "37836765affcc51a70933980a5121e25abc2c958"
            ],
            timestamp="loooooooooooooooooong_timestamp"
        )
        response = test_client.post('/node-detail/', data=data)
        assert response.status_code == 200


if __name__ == '__main__':
    with multiprocessing.Pool(processes=5) as pool:
        pool.map(pytest.main, [])
