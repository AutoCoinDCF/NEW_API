import os

def process():
    files_list = ["new_administrative.csv", 
	          "new_human.csv",
	          "new_organization.csv",
	          "warship.csv"]
#   files_list = ["test1.csv"]
    base_url = "http://10.60.1.143/pic_lib/entity/"
    base_dir = "./event/"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    for file in files_list:
        print("Processing file is:")
        print(file)
        path = "{}{}".format(base_dir, file)
        print(path)
        out = open(path, "w")
        for i, line in enumerate(open(file)):
            line = line.strip().split(",")
            new_line = line[:4]
            if i == 0:
                url = "image"
                new_line.append(url)
            else:
                url ="{}{}.png".format(base_url, line[0])
                new_line.append(url)
                new_line[-1] = "{}{}".format(new_line[-1],"\n")
            out_line = ",".join(new_line)
            out.write(out_line)
if __name__ == "__main__":
    process()
