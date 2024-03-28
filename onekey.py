import os
import argparse
#import requests 

parser = argparse.ArgumentParser() 
parser.add_argument('-d', '--dir', type=str, required=True, help='dataset path')
args = parser.parse_args()


os.makedirs(args.dir, exist_ok=True)
# download
scenes = ["atrium", "concourse", "hall", "piatrium"]

if not os.path.isfile(os.path.join(args.dir, "atrium.zip")):
    os.system("wget \"https://hkustconnect-my.sharepoint.com/:u:/g/personal/cliudg_connect_ust_hk/EbXzJ2Tdb_9AixIzPLsDmq4BfLaES91M_oktdLtjIlomVg?e=volIya&download=1\" \
          -O {}".format(os.path.join(args.dir, "atrium.zip")))
if not os.path.isfile(os.path.join(args.dir, "concourse.zip")):
    os.system("wget \"https://hkustconnect-my.sharepoint.com/:u:/g/personal/cliudg_connect_ust_hk/EbdqDm8XFrdHm8ICq3qRgswBad2Tugpnnd4uoniZS3S_IQ?e=zappQN&download=1\" \
          -O {}".format(os.path.join(args.dir, "concourse.zip")))
if not os.path.isfile(os.path.join(args.dir, "hall.zip")):
    os.system("wget \"https://hkustconnect-my.sharepoint.com/:u:/g/personal/cliudg_connect_ust_hk/EdEHoZA_bbpAmRZAkpwYuhsBRPpzStCmmu4C4BLo0OESKg?e=GJAi2W&download=1\" \
          -O {}".format(os.path.join(args.dir, "hall.zip")))
if not os.path.isfile(os.path.join(args.dir, "piatrium.zip")): 
    os.system("wget \"https://hkustconnect-my.sharepoint.com/:u:/g/personal/cliudg_connect_ust_hk/EdlqylpvO8dFkmyRzkwtx38BoUucVkeRSliCkwX96JhUrg?e=DkmVze&download=1\" \
           -O {}".format(os.path.join(args.dir, "piatrium.zip")))

print("extract file")
for scene in scenes:
    if not os.path.exists(os.path.join(args.dir, "atrium")):
        os.system("unzip {} -d {}".format(os.path.join(args.dir, "{}.zip".format(scene)), args.dir))
    # remove file
    # os.system("rm -rf {}".format(os.path.join(args.dir, "{}.zip".format(scene))) 

# process
os.system("python process.py --dir {}".format(args.dir))