import requests
import os
import getopt
import sys
import json
import base64
import random
from qiniu_auth import AuthFactory

FaceSimService = "http://argus.atlab.ai/v1/face/sim"
Base64Header = "data:application/octet-stream;base64,"

def NormQuery(conf,root_dir,result_file):
    factory = AuthFactory(conf["access_key"], conf["secret_key"])
    if conf["auth"] == "qiniu/mac":
        fauth = factory.get_qiniu_auth
    else:
        fauth = factory.get_qbox_auth

    data_folders = os.listdir(root_dir)
    if len(data_folders)<1:
        print "invalid number of folders in the dataset dir"
        return

    with open(result_file,'w') as output:
        output.writelines(["image1\timage2\tsimilarity\n"])
        for fold in data_folders:
            signle=os.path.join(root_dir,fold)
            if not os.path.isdir(signle):
                print "%s is not a dir".format(signle)
                continue

            files=ParseFiles(signle)
            if files is None:
                print "there is no valid files in dir",signle
                continue
            cimg= base64.b64encode(open(files[0],'rb').read())
            card = Base64Header + cimg

            for file in files[1:]:
                fimg=base64.b64encode(open(file, 'rb').read())
                face = Base64Header + fimg
                token = fauth()
                dt=json.dumps({"data": [{"uri":card},{"uri":face}]})
                try:
                    resp = requests.post(FaceSimService, data=dt, timeout=60,headers={"Content-Type": "application/json"}, auth=token)
                except Exception, e:
                    print "http request exception occur:", e
                    continue
                if resp.status_code/100!=2:
                    print "http response error:",resp.status_code
                    continue
                try:
                    ret = json.loads(resp.text)
                except Exception, e:
                    print "json loads http resp error:", resp.text
                    continue
                print ret
                output.writelines([files[0]+"\t"+file+"\t"+str(ret["result"]['similarity'])+"\n"])



def RandomQuery(conf,root_dir,result_file):
    factory = AuthFactory(conf["access_key"], conf["secret_key"])
    if conf["auth"] == "qiniu/mac":
        fauth = factory.get_qiniu_auth
    else:
        fauth = factory.get_qbox_auth

    data_folders = os.listdir(root_dir)
    if len(data_folders)<1:
        print "invalid number of folders in the dataset dir"
        return

    with open(result_file,'w') as output:
        output.writelines(["image1\timage2\tsimilarity\n"])
        for fold in data_folders:
            signle=os.path.join(root_dir,fold)
            if not os.path.isdir(signle):
                print "%s is not a dir".format(signle)
                continue

            #face_folders = data_folders[random.randint(0,len(data_folders)-1)]
            #random_num = random.sample(range(0,len(data_folders)-1),4)

            for num in range(0,3):
                face_folders = data_folders[random.randint(0,len(data_folders)-1)]
                #face_folders = data_folders[num]
                face_abspath = os.path.join(root_dir,face_folders)
                files=RamdonQueryParseFiles(signle,face_abspath)
                
                if files is None:
                    print "there is no valid files in dir",signle
                    continue
                cimg= base64.b64encode(open(files[0],'rb').read())
                card = Base64Header + cimg

                for file in files[1:]:
                    fimg=base64.b64encode(open(file, 'rb').read())
                    face = Base64Header + fimg
                    token = fauth()
                    dt=json.dumps({"data": [{"uri":card},{"uri":face}]})
                    try:
                        resp = requests.post(FaceSimService, data=dt, timeout=60,headers={"Content-Type": "application/json"}, auth=token)
                    except Exception, e:
                        print "http request exception occur:", e
                        continue
                    if resp.status_code/100!=2:
                        print "http response error:",resp.status_code
                        continue
                    try:
                        ret = json.loads(resp.text)
                    except Exception, e:
                        print "json loads http resp error:", resp.text
                        continue
                    print ret
                    output.writelines([files[0]+"\t"+file+"\t"+str(ret["result"]['similarity'])+"\n"])



def ParseFiles(sub_dir):
    print "parse files in dir:",sub_dir
    files=os.listdir(sub_dir)
    if len(files)<2:
        return None

    face=[]
    ret=[]
    card=None
    for file in files:
        if "card" in file:
            card=os.path.join(sub_dir,file)
        if "face" in file:
            face.append(os.path.join(sub_dir,file))
    if card is None:
        return  None
    ret.append(card)
    ret.extend(face)
    return ret

def RamdonQueryParseFiles(card_dir,face_dir):
    cardfiles=os.listdir(card_dir)
    if len(cardfiles)<2:
        return None

    facefiles=os.listdir(face_dir)
    if len(facefiles)<2:
        return None
  
    face=[]
    ret=[]
    card=None
    for file in cardfiles:
        if "card" in file:
            card=os.path.join(card_dir,file)
    if card is None:
        return  None

    for file in facefiles:
        if "face" in file:
            face.append(os.path.join(face_dir,file))
    if face is None:
        return  None

    ret.append(card)
    ret.extend(face)
    return ret

def Params(argv):

    help="""
    Usage:
     -d [--data-dir]   <root directory of the dataset>
     -f [--qiniu-auth] <configure file>
     -o [--result-file] <the file to keep testing results>
     
    """

    opts, args = getopt.getopt(argv, "hf:d:o:",
                               ["result-file=","qiniu-auth=", "data-dir="])


    auth_conf=None
    data_location=""
    result_file=""
    try:
        for opt, arg in opts:
            if opt == '-h':
                print help
                sys.exit()
            elif opt in ("-f", "--qiniu-auth"):
                auth_conf = json.load(open(arg))
            elif opt in ("-d","--data-dir"):
                data_location= arg
            elif opt in ("-o", "--result-file"):
                result_file=arg
    except getopt.GetoptError, e:
        print e
        print help
        sys.exit(1)

    if not os.path.isabs(data_location):
        print "%s not a abs path".format(data_location)
        print  help
        return None,None,None

    return auth_conf,data_location,result_file

if __name__=="__main__":

    auth_conf,data_loc,result_file=Params(sys.argv[1:])
    NormQuery(auth_conf, data_loc, result_file)
    #RandomQuery(auth_conf, data_loc, result_file)
