# 基于PaddleOCR的文本识别标注工具

**说明：** 本工具主要是对PaddleOCR的文本识别结果进行重新标注，方便后续训练。

<a name="1"></a>
## 1. 安装

  ```
  pip install -r requirements.txt
  ```

<a name="2"></a>
## 2. 工具使用
<a name="21"></a>
### 2.1 使用PaddleOCR对图片进行预测，得到识别结果

PaddleOCR提供了一系列识别模型以及模型预测方法，点击[这里](https://github.com/PaddlePaddle/PaddleOCR/blob/dygraph/doc/doc_ch/recognition.md#3-%E6%A8%A1%E5%9E%8B%E8%AF%84%E4%BC%B0%E4%B8%8E%E9%A2%84%E6%B5%8B)查看预测流程。

以PaddleOCR提供的PP-OCRv4模型为例，预测命令如下：

```
cd /path/to/PaddleOCR
# 预测多张图片
python3 tools/infer_rec.py -c configs/rec/PP-OCRv4/ch_PP-OCRv4_rec.yml -o Global.pretrained_model={path/to/weights}/best_accuracy Global.infer_img={path/to/images} Global.save_res_path=./output/rec_res.txt
```
其中，`{path/to/weights}` 为模型权重所在的路径，`{path/to/images}` 为待预测图片目录所在路径,`rec_res.txt` 为预测结果文件,我们后续要根据此预测结果文件对图片进行重新标注。

<a name="21"></a>
### 2.2 使用本工具对PaddleOCR的识别结果进行重新标注
```
cd /path/to/ocr_rec_labeled_tools
```

启动命令

```
python tools.py --file_name xxx.txt --server_name xx.xx.xx.xx --server_port xxx
```

`--file_name` PaddleOCR的识别结果，`--server_name` 和 `--server_port` 为服务器的ip地址和端口号。
启动后，在浏览器中输入 `http://xx.xx.xx.xx:xxx/`，进入标注页面。

<a name="21"></a>
### 2.3 窗口功能
点击 `上一张`，`下一张` 按钮，选择需要标注的图片。窗口 `模型预测结果` 可显示PaddleOCR的识别结果，在`图片真实标签，可在此进行标注`处可对标签进行修改，若模型预测结果正确，则无需修改。

<p align="center">
 <img src="https://github.com/PaddlePaddle/PaddleDetection/assets/94225063/92622fdb-da87-4495-b2bd-ec808175d87c" align="middle" width = "600"/>

标注前需在 `标注文件保存路径` 处修改标注结果保存位置，标注完成后，点击 `更新标注文件` 按钮，将当前图片的标签保存到指定路径。

若需跳转至指定图片，在 `输入跳转图片索引` 处输入图片索引即可。

<p align="center">
 <img src="https://github.com/PaddlePaddle/PaddleDetection/assets/94225063/d92cb5c7-0256-4495-a1c9-c5c3e4b573c6" align="middle" width = "600"/>

标注后的结果请查看 `标注文件保存路径` 中输入的文件路径。

**注意：** 为确保标注结果及时保存，请在前端页面断开前，点击 `更新标注文件` 按钮（命令行启动命令kill，网络断开等，都会导致前端页面断开）。
