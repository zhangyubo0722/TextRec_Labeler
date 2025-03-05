import argparse
import gradio as gr
import shutil
import os
import logging
from PIL import Image


def read_image_paths(txt_file):
    with open(txt_file, 'r') as file:
        return [line.strip().split("\t") for line in file if line.strip()]

def show_image_at_index(image_paths, current_index):
    if 0 <= current_index < len(image_paths):
        image_path = image_paths[current_index][0]
        image_pred = image_paths[current_index][1]
        image = Image.open(image_path)
        width, height = image.size
        if width >= height:
            new_size = (900, min(int(height * 900 / width), 500))
        else:
            new_size = (min(int(height * 500 / width), 500), 500)
        image = image.resize(new_size)
        return image, f"{image_path}\t图片索引：{current_index}", image_pred, f"当前图片索引{current_index}", ""
    else:
        return None, "无效索引", None, current_index, ""

def custom_css():
    """生成自定义CSS样式字符串。"""
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

    .image-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        margin: auto;
    }
    """
    return custom_css

def main_webui_parse_args():
    parser = argparse.ArgumentParser(description='Image Management')
    parser.add_argument("--file_name", type=str)
    parser.add_argument("--output_file", type=str, default="updated_output.txt")
    parser.add_argument("--server_name", help="Server name for demo.launch()", type=str)
    parser.add_argument("--server_port", help="Server port for demo.launch()", type=int)
    args = parser.parse_args()
    if args.server_name is None:
        args.server_name = "0.0.0.0"
    if args.server_port is None:
        args.server_port = 8111
    return args

def copy_image_to_folder(image_path, folder_name, image_pred, updated_records, output_file):
    try:
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        new_path = os.path.join(folder_name, os.path.basename(image_path))
        
        if os.path.exists(new_path):
            return f"图片已存在于 {folder_name}，未更新"
        
        shutil.copy(image_path, new_path)

        updated_record = f"{new_path}\t{image_pred}"
        updated_records.append(updated_record)
        with open(output_file, "a") as file:
            for record in updated_records:
                file.write(record + "\n")

        return f"图片已复制到 {folder_name}，并更新至新文件"
    except Exception as e:
        return f"复制失败: {e}"

def interface_next():
    global current_index
    try:
        output = show_image_at_index(image_paths, current_index)
        current_index += 1
        return output
    except Exception as e:
        return None, "发生错误", None, current_index, str(e)


def interface_pre():
    global current_index
    try:
        current_index -= 1
        return show_image_at_index(image_paths, current_index - 1)
    except Exception as e:
        return None, "发生错误", None, current_index, str(e)

def interface_jump_to(index):
    global current_index
    try:
        current_index = int(index)
        return show_image_at_index(image_paths, current_index)
    except Exception as e:
        return None, "发生错误", None, current_index, str(e)


if __name__ == "__main__":
    args = main_webui_parse_args()
    txt_file_path = args.file_name
    output_file_path = args.output_file
    image_paths = read_image_paths(txt_file_path)
    current_index = 0

    updated_records = []

    with gr.Blocks(
        theme=gr.themes.Default(spacing_size="sm", text_size='sm'),
        css=custom_css()
    ) as demo:

        gr.Markdown("图像管理工具")

        with gr.Row():
            image = gr.Image(
                value=None,
                show_label=False,
                interactive=False,
                height=500,
                elem_classes="image-container"
            )
        with gr.Row():
            path_display = gr.Textbox(label="图片路径", value=None, interactive=False)
            image_pred = gr.Textbox(label="图片标签", interactive=False)

        operation_result = gr.Textbox(label="操作结果", interactive=False)

        with gr.Row():
            pre_button = gr.Button(value="上一张", variant='primary')
            pre_button.click(
                interface_pre,
                inputs=[],
                outputs=[image, path_display, image_pred, operation_result],
            )
            next_button = gr.Button(value="下一张", variant='primary')
            next_button.click(
                interface_next,
                inputs=[],
                outputs=[image, path_display, image_pred, operation_result],
            )

        with gr.Row():
            index_input = gr.Number(label="输入待跳转的图片索引", value=0)
            jump_button = gr.Button("跳转")
            jump_button.click(
                interface_jump_to,
                inputs=[index_input],
                outputs=[image, path_display, image_pred, operation_result],
            )

        with gr.Row():
            folder1_button = gr.Button(value="复制到中文印刷体文件夹", variant='primary')
            folder2_button = gr.Button(value="复制到中文手写体文件夹", variant='primary')
            folder3_button = gr.Button(value="复制到英文印刷体文件夹", variant='primary')
            folder4_button = gr.Button(value="复制到英文手写体文件夹", variant='primary')

            folder1_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "printed_chinese",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )
            folder2_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "handwritten_chinese",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )
            folder3_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "printed_english",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )
            folder4_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "handwritten_english",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )

        with gr.Row():
            folder5_button = gr.Button(value="复制到单字识别‌文件夹", variant='primary')
            folder6_button = gr.Button(value="复制到通用场景‌文件夹", variant='primary')
            folder7_button = gr.Button(value="复制到艺术字体文件夹", variant='primary')
            folder8_button = gr.Button(value="复制到特殊字符文件夹", variant='primary')

            folder5_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "single_character",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )
            folder6_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "general_scenes",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )
            folder7_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "artistic_text",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )
            folder8_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "special_characters",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )

        with gr.Row():
            folder9_button = gr.Button(value="复制到希腊字母文件夹", variant='primary')
            folder10_button = gr.Button(value="复制到旋转文本文件夹", variant='primary')
            folder11_button = gr.Button(value="复制到日文文件夹", variant='primary')
            folder12_button = gr.Button(value="复制到古籍文件夹", variant='primary')

            folder9_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "greek_letters",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )
            folder10_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "rotated_text",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )
            folder11_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "japanese",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )
            folder12_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "ancient_text",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )
        with gr.Row():
            folder13_button = gr.Button(value="复制到emoji文件夹", variant='primary')
            folder14_button = gr.Button(value="复制到模糊文本文件夹", variant='primary')
            folder15_button = gr.Button(value="复制到扭曲文本文件夹", variant='primary')
            folder16_button = gr.Button(value="复制到拼音文件夹", variant='primary')

            folder13_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "emoji",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )
            folder14_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "fuzzy_text",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )
            folder15_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "distorted_text",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )
            folder16_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "pinyin_annotation",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )
        with gr.Row():
            folder17_button = gr.Button(value="复制到繁体中文文件夹", variant='primary')
            folder18_button = gr.Button(value="复制到易混淆字符文件夹", variant='primary')

            folder17_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "traditional_chinese",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )
            folder18_button.click(
                lambda: copy_image_to_folder(image_paths[current_index - 1][0], "confusable_characters",
                                             image_paths[current_index - 1][1], updated_records, output_file_path),
                inputs=[],
                outputs=[operation_result],
            )

    demo.launch(
        server_name=args.server_name,
        server_port=args.server_port,
        max_threads=50
    )
