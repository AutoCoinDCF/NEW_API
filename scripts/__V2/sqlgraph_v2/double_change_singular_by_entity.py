ids = {}

def filter_file():
    # try:
    with open('./relation.csv','r') as f:
        with open('./relation_v2.csv', 'w') as p:
            print("start!")
            while True:
                s = f.readline()
                s2 = s.split(",")
		#print s2
                try:
                    if s2[0] + s2[1]in ids:
                        s2[2] = ids[s2[0] + s2[1]]
                    elif s2[1] + s2[0] in ids:
                        s2[2] = ids[s2[1] + s2[0]]
                    else:
                        ids[s2[0] + s2[1]] = s2[2]
                    p.write(",".join(s2))
                except:
                    pass
                if not s:
                    break
            print("end!")
    # except Exception as error:
        # print(error)

filter_file()
