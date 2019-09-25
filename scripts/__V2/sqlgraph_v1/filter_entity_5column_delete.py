'''
Script usage: filters files in CSV format to 5 columns
'''
def filter_file():
    # try:
    with open('./relation_entity_singular.csv','r') as f:
        with open('./relation_entity_singular_v2.csv','w') as p:
            while True:
                s = f.readline()
                if len(s.split(',')) == 5:
                    p.write(s)
                if not s:
                    break
    # except Exception as error:
        # print(error)

filter_file()
