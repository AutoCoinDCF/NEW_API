ids = {}

def filter_file():
    # try:
    with open('./csv/relation.csv','r') as f:
        with open('./csv/relation_singular.csv', 'w') as p:
            print("start!")
            while True:
                s = f.readline()
                s2 = s.split(",")
		#print s2
                try:
                    if s2[1] + s2[4].replace("\n", "")in ids:
                        s2[0] = ids[s2[1] + s2[4].replace("\n", "")]
                    elif s2[4].replace("\n", "") + s2[1] in ids:
                        s2[0] = ids[s2[4].replace("\n", "") + s2[1]]
                    else:
                        ids[s2[1] + s2[4].replace("\n", "")] = s2[0]
                    p.write(",".join(s2))
                except:
                    pass
                if not s:
                    break
            print("end!")
    # except Exception as error:
        # print(error)

filter_file()
