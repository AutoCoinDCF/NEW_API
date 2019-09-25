# To front-end: web api definition 
- - -
**docs Template:**  

### x.x Xxxxxx  
**request:**  
* *http method:* xxx  
* *url:* xxx
* *url-params:* 
  * xxx: *type*: xxx
    * *meaning*: xxx
* *http body:* 
    ```json
    xxx
    ```
* ***example:***
  * xxx
  * body:
  ```json
  xxx
  ```
  
**response:**
* ***example:***
    ```json
    xxx
    ```

- - -
## 1.Graph itself operation:
### 1.1 Get node id from a pattern-string  
**request:**  
* *http method:* GET  
* *url:* /node-ids/  
* *url-params:* 
  * pattern: *type*: string
    * *meaning*: the pattern string to match the name of wanted nodes
* *http body:* None
* ***example:***
  * GET 10.60.1.141:5001/node-ids/?pattern=Nero
  * body: None
  
**response:**
* ***example:***
    ```json
    {
      "code": 0,
      "data": [
        {
          "nodes": [
            {
              "name": "Nero",
              "nodeId": "Q370363",
              "tags": "human"
            },
            {
              "name": "Nero",
              "nodeId": "Q1413",
              "tags": "human"
            }
          ]
        }
      ]
    }
    ```

### 1.2 Get nodes' data from nodes' id  
**request:**  
* *http method:* POST
* *url:* /node-datas/
* *url-params:* None
* *http body:* 
  * nodeIds: *type:* list
    * *meaning:* the node-ids to be searched
* ***example:***
  * POST 10.60.1.141:5001/node-datas/
  * body:
    ```json
    {
        "nodeIds": ["Q23","Q24"]
    }
    ```  
**response:**
* ***example:***
    ```json
    {
      "code": 0,
      "data": [
        {
          "nodes": [
            {
              "id": "Q23",
              "type": "human",
              "name": "George Washington",
              "image": "https://commons.wikimedia.org/wiki/File:Gilbert Stuart Williamstown Portrait of George Washington.jpg"
            },
            {
              "id": "Q24",
              "type": "human",
              "name": "Jack Bauer",
              "image": "https://commons.wikimedia.org/wiki/File:Kiefer Sutherland at 24 Redemption premiere 1 (headshot).jpg"
            }
          ]
        }
      ]
    }
    ```

### 1.3 Expand neighbors(links and linked nodes) of a node from its nodeId 
**request:**  
* *http method:* GET  
* *url:* /neighbor-datas/
* *url-params:* 
  * ClassName: *type:* str or **None**
    * *meaning:* the coarse-grained type of links (example: knowledge,event)
    * ***default:*** \[knowledge,event\]
  * nodeId: *type:* str
    * *meaning:* the nodeId whose neighbor nodes and links would be expanded
* *http body:* None
* ***example:***
  * GET 10.60.1.141:5001/neighbor-datas/?ClassName=knowledge&nodeId=Q370363
  * body: None
  
**response:**
* ***example:***
    ```json
    {
      "code": 0,
      "data": [
        {
          "nodes": [
            {
              "id": "Q191039",
              "type": "human",
              "name": "Germanicus",
              "img": ""
            },
            {
              "id": "Q82955",
              "type": "occupation",
              "name": "politician",
              "img": ""
            }
          ],
          "links": [
            {
              "id": "358790739",
              "from": "Q191039",
              "to": "Q370363",
              "img": "",
              "type": "child"
            },
            {
              "id": "896072079",
              "from": "Q370363",
              "to": "Q82955",
              "img": "",
              "type": "occupation"
            }
          ]
        }
      ]
    }
    ```

## 2.WorkingSet Operation:
todo
## 3.Data Pivot Operation:
todo
## 4.Time Operation:
todo
## 5.Geography Operation:
todo