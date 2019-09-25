ids = {}
l = ['9ff5080ff7f7331eb544a90c0c2cead9', '4bb8d805c5a43e06ae856bb5776d58a9', '62e89a4c165430d5a5f3a5a4cce650d6', 'e32abd2aca9b382881f1167732abb627', '6732cbf3130d36069a75877bc133bd25', '47919943ce5235448d250fcddbda2e2b', '0fe6a33fd5e83ecca63cc9453873e6d0', 'f6286019bf593cf293f584885a07cb38', '245e0c8ed639351b86b74825a7b2f921', '8a0627538efb3b5397fd5ec0ae4c5698', '411b0c620a5e38d4a004c81e5a049f30', '252bb4a12bb63d1a9550148d865787ff', 'ad666a4d253c3ea881dd8af1c5324ac8', '8c5a66f09d523283ac94941a716cbd6b', '45c7872a4bf9336b8ff697f3e7753016', '8b313601ee993d589a233deef4470efd', '1fde80d784a939e1b8a51ac46b8149d6', '5f38e19b1fa33bc185f96e1b8e6fca61', 'b0fa219c57c33e328f17f8c1f914368e', 'e91d139419d731018b06233dbba0dfc7', '9957ddfb19c63002a4732703e6ab4fc4', 'e25142be08283645bcd8adc1044302c0', 'f7afc4bb08f13e26ac6815428bab9f87', '4699e3a4cf4e3b84ae3142dac8a699d1', 'e0597b56c1b433ce9006fc366afff523', '96dfd4104a7d337a83474f14c9cb45b9', '7175298224e834b384c9e379693a049e', 'f20590b1d289368abb9d26fc5b40b26d', 'ad28376ec1983bb0abb524f9b4a92283', '1619fca64e923d4abcabc1cb303c0531', 'dec768dc83d0362db7e72cd521c21bee', '0b51090d802737fa8f9cb6009d698ce1', 'c8cbf905b8c131d9b2dac1af8de28a1f', '1f0bd17358dc37ddad815d8bf9ecd870', '4ed1ccd88b363ddca9cb757856c8c4d6', 'fa9fd4a560f2397eaf43efd421cce63e', '1e5d0cc8069a344b9908f18ac508c6f1', 'b1efde65d0a436608ee00e0f890c64b0', '1534ad5f52133f9db5e451aaa77c79c5', 'de33951d8d923ad983ed24b19fd55402', '5eb6acdf5fa6345db5f45f2561c8cf90', 'b37c62d2296a3246ba50d478e80a2ac3', '4df1dc706d0e3f71a3c571538b86237f', '17b0e9bb52273ca0b8adfb833a116557', '4b32252d930b357eb48686ab2fe5e0ab', '80c006c8ea1b3aa7af46dc02cb78466f', '741475485aaf371daf045ae93f101c07', '505b17764e0f33ef850e39e86db1523b', '18b56b5745263a05905202822f32f95b', 'ccfe10cef5e73ed3a3b333ba04dcd681', '31f9a77352913253b02e07a477cf521d', '4ddf6df58cd531618245fffe8af70ee2', 'd80f2187c27f32f283c2e3ead10858cc', '563ca3c3d5453c29b0924c395db18106', '1659fd9b4a143fc1a1f29c2b2d802b1e', '0b4cccee26193026ba3d40408d4aaffa']

def filter_file():
    i = 0
    j = 0
    # try:
    with open('./relation_singular.csv','r') as f:
        with open('./relation_singular_v2.csv', 'w') as p:
            print("start!")
            while True:
                i += 1
                s = f.readline()
                s2 = s.split(",")
                if s2[1] in l or s2[4].replace("\n", "") in l:
                    print("------------pop-------------")
                    print(s2)
                    continue
                j += 1
		#print s2
                try:
                    print("-----------i-j------------")
                    print("i", i)
                    print("j", j)
                    print(s)
                    p.write(s)
                except:
                    pass
                if not s:
                    break
            print("end!")
    # except Exception as error:
        # print(error)

filter_file()
