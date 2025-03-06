import os
import sys
import logging
import argparse
import shutil
from typing import List, Tuple

import gradio as gr
from PIL import Image

class ImageManager:
    def __init__(self, config):
        self.config = config
        self.setup_logging()
        self.image_paths = self.read_image_paths(config.file_name)
        self.current_index = 0
        self.updated_records = []

    def setup_logging(self):
        """配置日志系统"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler("image_manager.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )

    def read_image_paths(self, txt_file: str) -> List[Tuple[str, str]]:
        """读取图像路径和标签"""
        try:
            with open(txt_file, 'r', encoding='utf-8') as file:
                return [line.strip().split("\t") for line in file if line.strip()]
        except IOError as e:
            logging.error(f"读取文件错误: {e}")
            return []

    def process_image(self, index: int) -> dict:
        """处理指定索引的图像"""
        try:
            if 0 <= index < len(self.image_paths):
                image_path, image_pred = self.image_paths[index]
                image = self._resize_image(image_path)
                return {
                    "image": image,
                    "path": image_path,
                    "pred": image_pred,
                    "index": index
                }
            else:
                logging.warning(f"无效的图像索引: {index}")
                return {}
        except Exception as e:
            logging.error(f"处理图像时发生错误: {e}")
            return {}

    def _resize_image(self, image_path: str, max_width=900, max_height=500):
        """调整图像大小"""
        image = Image.open(image_path)
        width, height = image.size
        if width >= height:
            new_size = (max_width, min(int(height * max_width / width), max_height))
        else:
            new_size = (min(int(width * max_height / height), max_width), max_height)
        return image.resize(new_size)

    def copy_to_folder(self, image_path: str, folder: str, label: str) -> str:
        """复制图像到指定文件夹"""
        try:
            os.makedirs(folder, exist_ok=True)
            new_path = os.path.join(folder, os.path.basename(image_path))
            
            if os.path.exists(new_path):
                return f"图片已存在于 {folder}"
            
            shutil.copy(image_path, new_path)
            
            record = f"{new_path}\t{label}"
            self.updated_records.append(record)
            
            with open(self.config.output_file, "w", encoding='utf-8') as f:
                f.write("\n".join(self.updated_records))
            
            return f"已复制到 {folder}"
        except Exception as e:
            logging.error(f"复制图像错误: {e}")
            return f"复制失败: {e}"

    def next_image(self):
        """获取下一张图像"""
        self.current_index = min(self.current_index + 1, len(self.image_paths) - 1)
        return self.process_image(self.current_index)

    def prev_image(self):
        """获取上一张图像"""
        self.current_index = max(self.current_index - 1, 0)
        return self.process_image(self.current_index)

    def jump_to_image(self, index):
        """跳转到指定索引的图像"""
        self.current_index = max(0, min(index, len(self.image_paths) - 1))
        return self.process_image(self.current_index)

class ConfigManager:
    def __init__(self):
        parser = argparse.ArgumentParser(description='图像管理工具')
        parser.add_argument("--file_name", required=True, help="输入的图片路径文件")
        parser.add_argument("--output_file", default="updated_output.txt", help="输出文件")
        parser.add_argument("--server_name", default="0.0.0.0", help="服务器地址")
        parser.add_argument("--server_port", type=int, default=8111, help="服务器端口")
        
        self.args = parser.parse_args()
        self.file_name = self.args.file_name
        self.output_file = self.args.output_file
        self.server_name = self.args.server_name
        self.server_port = self.args.server_port

def create_gradio_interface(image_manager):
    folders = [
        "printed_chinese", "handwritten_chinese", 
        "printed_english", "handwritten_english",
        "single_character", "general_scenes", 
        "artistic_text", "special_characters",
        "greek_letters", "rotated_text", 
        "japanese", "ancient_text",
        "emoji", "fuzzy_text", 
        "distorted_text", "pinyin_annotation",
        "traditional_chinese", "confusable_characters"
    ]

    with gr.Blocks(css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .image-container {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            height: 500px;
        }
        .image-container img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
    """) as demo:
        current_image_path = gr.State("")
        current_label = gr.State("")

        with gr.Row():
            with gr.Column(scale=2):
                with gr.Row(elem_classes="image-container"):
                    image_display = gr.Image(height=500, type="pil", elem_classes="image-container")
            
        with gr.Row():
            path_display = gr.Textbox(label="图片路径", interactive=False)
            pred_display = gr.Textbox(label="原始标签", interactive=False)
            proofread_text = gr.Textbox(label="校对文本", interactive=True)

        with gr.Row():
            prev_btn = gr.Button("上一张")
            next_btn = gr.Button("下一张")
            jump_index = gr.Number(label="跳转索引", precision=0)
            jump_btn = gr.Button("跳转")

        operation_result = gr.Textbox(label="操作结果", interactive=False)

        with gr.Row():
            folder_buttons = [gr.Button(f"复制到{folder}文件夹") for folder in folders]

        def update_display(image_info):
            if not image_info:
                return [None, "", "", "", ""]
            return [
                image_info.get('image'), 
                image_info.get('path', ''), 
                image_info.get('pred', ''), 
                image_info.get('pred', ''),
                ""
            ]

        def navigate(is_next):
            image_info = image_manager.next_image() if is_next else image_manager.prev_image()
            return update_display(image_info)

        def jump_to(index):
            image_info = image_manager.jump_to_image(int(index))
            return update_display(image_info)

        demo.load(
            lambda: update_display(image_manager.process_image(0)),
            None, 
            [image_display, path_display, pred_display, proofread_text, operation_result]
        )

        prev_btn.click(
            lambda: navigate(False), 
            None,
            [image_display, path_display, pred_display, proofread_text, operation_result]
        )
        
        next_btn.click(
            lambda: navigate(True), 
            None,
            [image_display, path_display, pred_display, proofread_text, operation_result]
        )

        jump_btn.click(
            jump_to, 
            jump_index,
            [image_display, path_display, pred_display, proofread_text, operation_result]
        )

        for btn, folder in zip(folder_buttons, folders):
            btn.click(
                lambda path, label, folder=folder: 
                    (image_manager.copy_to_folder(path, folder, label), path, label),
                [path_display, proofread_text],
                [operation_result, current_image_path, current_label]
            )

    return demo

def main():
    config = ConfigManager()
    image_manager = ImageManager(config)
    
    demo = create_gradio_interface(image_manager)
    demo.launch(
        server_name=config.server_name,
        server_port=config.server_port
    )

if __name__ == "__main__":
    main()
