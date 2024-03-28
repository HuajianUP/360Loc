import os
import cv2
import json
import tqdm
import yaml
import numpy as np
import argparse
from multiprocessing import Pool


def rotate_x(angle):
    r_mat = np.identity(3)
    sin_a = np.sin(angle)
    cos_a = np.cos(angle)
    r_mat[1, 1] = cos_a
    r_mat[2, 2] = cos_a
    r_mat[1, 2] = -sin_a
    r_mat[2, 1] = sin_a
    return r_mat

def rotate_y(angle):
    r_mat = np.identity(3)
    sin_a = np.sin(angle)
    cos_a = np.cos(angle)
    r_mat[0, 0] = cos_a
    r_mat[2, 2] = cos_a
    r_mat[0, 2] = sin_a
    r_mat[2, 0] = -sin_a
    return r_mat

def rotate_z(angle):
    r_mat = np.identity(3)
    sin_a = np.sin(angle)
    cos_a = np.cos(angle)
    r_mat[0, 0] = cos_a
    r_mat[1, 1] = cos_a
    r_mat[0, 1] = -sin_a
    r_mat[1, 0] = sin_a
    return r_mat

def sphereRay(imgh=2048, imgw=4096):
    u, v = np.meshgrid(np.arange(imgw, dtype=np.float32), np.arange(imgh, dtype=np.float32), indexing='xy')
    lon = u * 2 * np.pi / imgw - np.pi
    lat = -v * np.pi / imgh + np.pi * .5
    camera_dirs = np.stack([np.cos(lat) * np.sin(lon),
                            -np.sin(lat), np.cos(lat) * np.cos(lon)], -1)
    return camera_dirs

def xyz2uv_sphere(bearing, imgh=2048, imgw=4096):
    x , y, z = bearing[..., 0],bearing[..., 1],bearing[..., 2]
    fx = imgw / (2 * np.pi)
    fy = -imgh / np.pi
    cx = imgw / 2
    cy = imgh / 2
    lon = np.arctan2(x, z)
    lat = np.arctan2(-y, np.sqrt(x**2 + z**2)) 
    u = lon * fx + cx - 0.5
    v = lat * fy + cy - 0.5
    return u, v

def pinholeRay(camera_model):
    imgw = camera_model["imgw"]
    imgh = camera_model["imgh"]
    u, v = np.meshgrid(np.arange(imgw, dtype=np.float32), np.arange(imgh, dtype=np.float32), indexing='xy')
    x = (u + 0.5 - camera_model["cx"]) / camera_model["fx"]
    y = (v + 0.5 - camera_model["cy"]) / camera_model["fy"]
    camera_dirs = np.stack([x, y, np.ones_like(u)], -1)
    return camera_dirs

def dsRay(camera_model):
    imgw = camera_model["imgw"]
    imgh = camera_model["imgh"]
    xi = camera_model["xi"]
    alpha = camera_model["alpha"]
    u, v = np.meshgrid(np.arange(imgw, dtype=np.float32), np.arange(imgh, dtype=np.float32), indexing='xy')
    mx = (u + 0.5 - camera_model["cx"]) / camera_model["fx"]
    my = (v + 0.5 - camera_model["cy"]) / camera_model["fy"]
    r2 = mx*mx + my*my
    invaild_idx = r2 > 1/(2*alpha-1)
    mz1 = 1 - r2 * (alpha**2)
    mz2 = alpha * np.sqrt(1 - (2*alpha-1)*r2) + 1 - alpha
    mz = mz1/mz2
    pre1 = mz * xi + np.sqrt(mz*mz + (1-xi**2)*r2)
    pre2 = mz * mz + r2
    pre = pre1 / pre2
    x = pre * mx
    y = pre * my
    z = pre * mz - xi
    x[invaild_idx] = 0
    y[invaild_idx] = 0
    z[invaild_idx] = 0
    camera_dirs = np.stack([x, y, z], -1)
    #print(camera_dirs, np.min(camera_dirs));exit()
    return camera_dirs, invaild_idx



def processOnce(scene):
    assert os.path.exists(scene), "Scene {} doesn't exist".format(scene)
    print("Start to process scene {}".format(scene))
    # get the query the sequences
    query_seqs =[seq for seq in sorted(os.listdir(scene)) if "query" in seq and "360" not in seq]
    query_360 = "query_360"
    for query_seq in query_seqs:
        print("--Seq {}".format(query_seq))
        # get the camera model
        camera_model_str = query_seq.split("_")[-1]
        camera_config = os.path.join(scene, "camera_config", camera_model_str+".yaml")
        with open(camera_config, "r") as fin:
            camera_model = yaml.safe_load(fin)
        
        invaild_idx = None
        if "pinhole" in camera_model_str:
            bearing = pinholeRay(camera_model)
        elif "fisheye" in camera_model_str:
            bearing, invaild_idx = dsRay(camera_model)
    
        sub_seqs = sorted(os.listdir(os.path.join(scene, query_seq)))
        for sub_seq in sub_seqs:
            # get the reference poses
            with open(os.path.join(scene, query_360, sub_seq.replace(camera_model_str, "360"), "camera_pose.json"), 'r') as fp:
                poses_ref = json.load(fp)
            # get the current poses
            with open(os.path.join(scene, query_seq, sub_seq, "camera_pose.json"), 'r') as fp:
                poses = json.load(fp)
            assert len(poses) == 2*len(poses_ref)

            image_path = os.path.join(scene, query_seq, sub_seq, "image")
            os.makedirs(image_path, exist_ok=True)
            for pose_idx in tqdm.tqdm(poses, desc="cropping {}".format(sub_seq)):
                if os.path.isfile(os.path.join(image_path, pose_idx)):
                    continue
                pose_ref_idx = pose_idx.split("_")[0]+".jpg"
                img = cv2.imread(os.path.join(scene, query_360, sub_seq.replace(camera_model_str, "360"), "image", pose_ref_idx))
                pose_c2w_ref = np.array(poses_ref[pose_ref_idx])
                pose_c2w = np.array(poses[pose_idx])
                realated_pose = pose_c2w[:3, :3].T @ pose_c2w_ref[:3, :3]
                xyz = bearing @ realated_pose.astype(np.float32)
                u, v = xyz2uv_sphere(xyz, img.shape[0], img.shape[1])
                if invaild_idx is not None:
                    u[invaild_idx] = -1
                    v[invaild_idx] = -1
                out = cv2.remap(img, u, v, interpolation=cv2.INTER_LINEAR, borderValue=[0,0,0]) #INTER_LINEAR
                cv2.imwrite(os.path.join(image_path, pose_idx), out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser() 
    parser.add_argument('-d', '--dir', type=str, required=True, help='dataset path')
    args = parser.parse_args()

    scenes = ["atrium", "concourse", "hall", "piatrium"]
    scenes = [os.path.join(args.dir, scene) for scene in scenes]

    with Pool(processes=4) as pool:
        for scene in scenes:
            pool.apply_async(func=processOnce, args=(scene, ))
        pool.close()
        pool.join()




      