import argparse
import gradio as gr
from PIL import Image


def read_image_paths(txt_file):
    with open(txt_file, 'r') as file:
        return [line.strip().split("\t") for line in file if line.strip()]


def show_next_image(image_paths, current_index):
    global dict_to_save
    global dict_modify
    if current_index < len(image_paths):
        image_path = image_paths[current_index][0]
        image_pt = dict_to_save[image_path]
        if image_path in dict_modify:
            image_gt = dict_modify[image_path]
        else:
            image_gt = ""
        image = Image.open(image_path)
        width, height = image.size
        if width >= height:
            new_size = (900, min(int(height * 900 / width), 500))
        else:
            new_size = (min(int(height * 500 / width), 500), 500)
        image = image.resize(new_size)
        return image, f"{image_path}\t图片索引：{current_index}", image_pt, image_gt, current_index + 1
    else:
        return None, "已到达最后一张图片", None, None, current_index


def show_pre_image(image_paths, current_index):
    global dict_to_save
    global dict_modify
    if 0 < current_index <= len(image_paths):
        current_index = current_index - 1
        image_path = image_paths[current_index][0]
        image_pt = dict_to_save[image_path]
        if image_path in dict_modify:
            image_gt = dict_modify[image_path]
        else:
            image_gt = ""
        image = Image.open(image_path)
        width, height = image.size
        if width >= height:
            new_size = (900, min(int(height * 900 / width), 500))
        else:
            new_size = (min(int(height * 500 / width), 500), 500)
        image = image.resize(new_size)
        return image, f"{image_path}\t图片索引：{current_index}", image_pt, image_gt, current_index
    else:
        return None, "已到达第一张图片", None, None, current_index


def show_to_image(image_paths, current_index):
    global dict_to_save
    global dict_modify
    if 0 < current_index <= len(image_paths):
        image_path = image_paths[current_index][0]
        image_pt = dict_to_save[image_path]
        if image_path in dict_modify:
            image_gt = dict_modify[image_path]
        else:
            image_gt = ""
        image = Image.open(image_path)
        width, height = image.size
        if width >= height:
            new_size = (900, min(int(height * 900 / width), 500))
        else:
            new_size = (min(int(height * 500 / width), 500), 500)
        image = image.resize(new_size)
        return image, f"{image_path}\t图片索引：{current_index}", image_pt, image_gt, current_index  # 返回图片和下一个索引
    elif current_index <= 0:
        return None, "已到达第一张图片", None, None, current_index
    else:
        return None, "已到达最后一张图片", None, None, current_index


def custom_css():
    """
    生成自定义CSS样式字符串。
    """
    custom_css = """
    footer.svelte-1ax1toq {
        display: none !important;
    }

    .center-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
    }

    .content {
        text-align: center;
    }
    """
    return custom_css


def main_webui_parse_args():
    parser = argparse.ArgumentParser(description='Model training')
    parser.add_argument("--file_name", type=str)
    parser.add_argument(
        "--server_name", help="Server name for demo.launch()", type=str)
    parser.add_argument(
        "--server_port", help="Server port for demo.launch()", type=int)
    args = parser.parse_args()
    if args.server_name is None:
        args.server_name = "0.0.0.0"
    if args.server_port is None:
        args.server_port = 8111
    return args


def update_image_gt(path_gt, image_gt):
    global dict_modify
    dict_modify[path_gt.split("\t")[0]] = image_gt


def save_result(image_path_to_save):
    global txt_file_path
    global dict_modify
    try:
        with open(image_path_to_save, "w") as f:
            for key, value in dict_modify.items():
                f.write(f"{key}" + "\t" + f"{value}" + "\n")
        return "已成功更新"
    except:
        return "更新失败，请检查保存路径是否正确"


def interface(next_btn):
    global current_index
    image, image_path, image_pt, image_gt, current_index = show_next_image(
        image_paths, current_index)
    return image, image_path, image_pt, image_gt


def interface_pre(pre_btn):
    global current_index
    image, image_path, image_pt, image_gt, current_index = show_pre_image(
        image_paths, current_index)
    return image, image_path, image_pt, image_gt


def interface_skip(skip_to_index):
    global current_index
    global image_nums
    if 0 <= int(skip_to_index) < image_nums:
        current_index = int(skip_to_index)
        image, image_path, image_pt, image_gt, current_index = show_to_image(
            image_paths, current_index)
        return image, image_path, image_pt, image_gt
    else:
        return None, '请输入正确索引', None, None


if __name__ == "__main__":

    args = main_webui_parse_args()
    txt_file_path = args.file_name
    image_paths = read_image_paths(txt_file_path)
    image_nums = len(image_paths)
    current_index = 0
    dict_to_save = {}

    for i in image_paths:
        dict_to_save[i[0]] = i[1]
    dict_modify = dict_to_save.copy()

    with gr.Blocks(
            theme=gr.themes.Default(
                spacing_size="sm", text_size='sm'),
            css=custom_css()) as demo:

        gr.Markdown("数据标注工具")

        with gr.Row():
            image = gr.Image(
                value=None,
                show_label=False,
                interactive=False,
                height=500,
                elem_classes=custom_css())
        with gr.Row():
            path_gt = gr.Textbox(label="图片路径", value=None, interactive=False)
            image_pt = gr.Textbox(label="模型预测结果", interactive=False)
            image_gt = gr.Textbox(
                label="图片真实标签，可在此进行标注", value=None, interactive=True)
            image_path_to_save = gr.Textbox(
                label="标注文件保存路径", value=None, interactive=True)
        with gr.Row():
            pre_button = gr.Button(value="上一张", variant='primary')
            pre_button.click(
                interface_pre,
                inputs=[],
                outputs=[image, path_gt, image_pt, image_gt])
            next_button = gr.Button(value="下一张", variant='primary')
            next_button.click(
                interface,
                inputs=[],
                outputs=[image, path_gt, image_pt, image_gt])
            image_gt.blur(update_image_gt, inputs=[path_gt, image_gt])
        with gr.Row():
            skip_to_index = gr.Textbox(
                label="输入跳转图片索引", value=None, interactive=True)
            check_save_varify = gr.Textbox(
                label="更新结果", value="更新图片标签后点击下方按钮以更新标注文件", interactive=False)
        with gr.Row():
            to_current_index_button = gr.Button(value="跳转", variant='primary')
            to_current_index_button.click(
                interface_skip,
                inputs=[skip_to_index],
                outputs=[image, path_gt, image_pt, image_gt])
            save_result_button = gr.Button(value="更新标注文件", variant='primary')
            save_result_button.click(
                save_result,
                inputs=[image_path_to_save],
                outputs=[check_save_varify])

    demo.queue(concurrency_count=20).launch(
        server_name=args.server_name, server_port=args.server_port)
