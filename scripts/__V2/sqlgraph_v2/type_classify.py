import os

ids = {}

def filter_file():
    i = 0
    # try:
    entity_event = open("./csv/entity_event.csv", "w")
    entity_document = open("./csv/entity_document.csv", "w")
    event_entity = open("./csv/event_entity.csv", "w")
    document_entity = open("./csv/document_entity.csv", "w")
    event_document = open("./csv/event_document.csv", "w")
    document_event = open("./csv/document_event.csv", "w")
    with open('./csv/relation_singular.csv','r') as f:
        print("start!")
        while True:
            i += 1
            print("------------loading...------------")
            print(i)
            s = f.readline()
            s2 = s.split(",")
            try:
                if s2[5] == "entity" and s2[6].replace("\n", "") == "event":
                    entity_event.write(",".join(s2))
                elif s2[5] == "entity" and s2[6].replace("\n", "") == "document":
                    entity_document.write(",".join(s2))
                elif s2[5] == "event" and s2[6].replace("\n", "") == "entity":
                    event_entity.write(",".join(s2))
                elif s2[5] == "document" and s2[6].replace("\n", "") == "entity":
                    document_entity.write(",".join(s2))
                elif s2[5] == "event" and s2[6].replace("\n", "") == "document":
                    event_document.write(",".join(s2))
                elif s2[5] == "document" and s2[6].replace("\n", "") == "event":
                    document_event.write(",".join(s2))
            except:
                pass
            if not s:
                break
        print("end!")
    entity_event.close()
    entity_document.close()
    event_entity.close()
    document_entity.close()
    event_document.close()
    document_event.close()
    # except Exception as error:
        # print(error)

filter_file()
