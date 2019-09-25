def filter_file():
    # try:
    with open('entity_all.csv','r') as f:
        with open('entity_new.csv', 'w') as p:
            while True:
                s = f.readline()
                if len(s.split(',')) == 5:
                    p.write(s)
                if not s:
                    break
    # except Exception as error:
        # print(error)

filter_file()
