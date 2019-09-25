ids = {}

def filter_file(start, end):
    # try:
    with open(start, 'r') as f:
        with open(end, 'w') as p:
            print("start!")
            p.write("Head_id,Tail,id,relation_id,type"+"\n")
            while True:
                s = f.readline()
                s2 = s.split(",")
		#print s2
                try:
                    s3 = []
                    s3.append(s2[1])
                    s3.append(s2[4].replace("\n", ""))
                    s3.append(s2[0])
                    s3.append(s2[2])
                    s3.append(s2[3]+"\n")                
                    p.write(",".join(s3))
                except:
                    pass
                if not s:
                    break
            print("end!")
    # except Exception as error:
        # print(error)

filter_file('./csv/document_event.csv', './csv/document_event_v2.csv')
filter_file('./csv/entity_event.csv', './csv/entity_event_v2.csv')
filter_file('./csv/event_document.csv', './csv/event_document_v2.csv')
filter_file('./csv/document_entity.csv', './csv/document_entity_v2.csv')
filter_file('./csv/entity_document.csv', './csv/entity_document_v2.csv')
filter_file('./csv/event_entity.csv', './csv/event_entity_v2.csv')

