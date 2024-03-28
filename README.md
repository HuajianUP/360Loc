# 360Loc: Omnidirectional Visual Localization with Cross-device Queries

### [Homepage](https://huajianup.github.io/research/360Loc/) | [Paper](https://arxiv.org/abs/2311.17389)

**360Loc: A Dataset and Benchmark for Omnidirectional Visual Localization with Cross-device Queries** <br>
[Huajian Huang](https://huajianup.github.io)\*<sup>1</sup>, [Changkun Liu](https://lck666666.github.io)\*<sup>1</sup>, Yipeng Zhu<sup>1</sup>, Hui Cheng<sup>2</sup>,
[Tristan Braud](https://braudt.people.ust.hk/index.html)<sup>1</sup> and [Sai-Kit Yeung](https://saikit.org/)<sup>1</sup> <br>
<em>* equal contribution</em><br>
The Hong Kong University of Science and Technology<sup>1</sup>, Sun Yat-Sen University<sup>2</sup> <br>
In Proceedings of Computer Vision and Pattern Recognition Conference (CVPR), 2024<br>





## Usage
To save the store space and facilitate data access, we only store the original 360-degree images of query and inference. You can use this tool to generate required images in fisheye and pinhole cameras.
```
git clone https://github.com/HuajianUP/360Loc.git
pip install json tqdm yaml numpy opencv-python requests
```

You can download the 360Loc dataset [link](https://hkustconnect-my.sharepoint.com/:f:/g/personal/cliudg_connect_ust_hk/EqrMZf3qRGBEqQthBUuYKEoBc8BGCG_Gr9OPZPHxlhemGg?e=ZqmV9M) and unzip them in the folder `./360Loc`. 
```
360Loc
├── atrium
│   ├── camera_config
│   ├── pose
│   ├── mapping
│   ├── query_360
│   ├── query_pinhole
│   ├── query_fisheye1
│   ├── query_fisheye2
│   └── query_fisheye3
├── ....
│
└── piatrium
    ├── camera_config
    ├── ....
    └── query_fisheye3
```
And then run the below command to process the data.
```
python process.py --dir PATH_TO_360LOC_DATASET
```

We also provide a script to download and process the 360Loc dataset automatically. 
```
python onekey.py --dir PATH_TO_SAVE_360LOC_DATASET
```

# Pose Format
We provide both json poses files and txt poses files.

For .json poses files:
We give 4*4 matrix 
image_name: ```[R|T]```， ```T``` are camera to world coordinates.
  
For .txt poses files:
```image_name x y z qw qx qy qz```.

```x, y, z``` are camera to world coordinates.
Our 6DoF poses follow the COLMAP coordinate system.

<h3 id="citation">Citation</h3>
		<pre class="citation-code"><code><span>@inproceedings</span>{360Loc,
    title = {360Loc: A Dataset and Benchmark for Omnidirectional Visual Localization with Cross-device Queries},
    author = {Huang, Huajian and Liu, Changkun and Zhu, Yipeng and Cheng Hui and Braud, Tristan and Yeung, Sai-Kit},
    booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
    year = {2024}
}</code></pre>