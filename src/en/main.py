import os
import requests
import logging
import time
from seting import *
from pathlib import Path


# 确保父目录存在
parent_folder_path = os.path.dirname(folder_path)
os.makedirs(parent_folder_path, exist_ok=True)


# 确保日志目录存在
log_dir = os.path.dirname(os.path.join(folder_path, 'comic_downloader.log'))
os.makedirs(log_dir, exist_ok=True)


# 配置日志记录
logging.basicConfig(
    level=logging.INFO,  # 设置日志记录级别
    format='%(asctime)s - %(levelname)s - %(message)s',  # 格式化日志消息
    handlers=[
        logging.FileHandler(os.path.join(folder_path, 'comic_downloader.log')),  # 写入日志文件
        logging.StreamHandler()  # 可选：同时将日志写入控制台
    ]
)


# 如果文件夹不存在，则创建
os.makedirs(folder_path, exist_ok=True)


def writeMD(info, index, title):
    """将漫画信息写入 MD 文件"""
    text = stencil
    # 替换占位符
    text = text.replace("$image$", info["image"])
    text = text.replace("$url$", xkcd_url + "/" + str(index))
    text = text.replace("$title$", title)  # 替换标题占位符

    # 写入文件
    # 使用 pathlib 重构文件路径操作
    md_file_path = Path(folder_path) / f"{index:04}.md"
    with open(md_file_path, "w") as f:
        f.write(text)
    logging.info(f"已写入漫画信息到 {md_file_path}")


def get_latest_number():
    """获取当前已下载漫画的最新编号"""
    existing_files = os.listdir(folder_path)
    existing_numbers = [
        int(file[:-3]) for file in existing_files if file.endswith('.md')  # 仅处理.md 文件
    ]
    latest = max(existing_numbers, default=0)  # 返回最高编号或 0
    logging.info(f"最新的编号是: {latest}")
    return latest


def get_xkcd_comics(start_number, count=20):
    """下载 XKCD 漫画"""
    url_template = 'https://xkcd.com/{}/info.0.json'

    for i in range(start_number + 1, start_number + count + 1):
        response = requests.get(url_template.format(i))

        if response.status_code == 200:
            comic = response.json()
            info = {"image": comic['img']}
            title = comic['title']  # 获取漫画标题
            writeMD(info, i, title)  # 传递标题到函数
        else:
            logging.warning(f"请求漫画编号 {i} 时出错: {response.status_code}")

        time.sleep(sleep_time)


def organize_comics():
    """整理下载的漫画文件"""
    folder = Path(folder_path)
    all_images = sorted(
        (f for f in folder.glob('*.md')),
        key=lambda x: int(x.stem)  # 提取文件编号
    )

    for i in range(0, len(all_images), 10):
        group_number = i // 10
        group_folder = folder / f'{group_number * 10 + 1:04}-{group_number * 10 + 10:04}'

        # 创建组文件夹
        group_folder.mkdir(exist_ok=True)

        for img in all_images[i:i+10]:
            # 使用 pathlib 重构文件路径操作
            src_path = folder / img.name
            dst_path = group_folder / img.name
            src_path.rename(dst_path)  # 移动文件
            logging.info(f"已移动: {img.name} 到 {group_folder}")


def testing():
    current_dir = Path.cwd()
    absolute_path = (current_dir / folder_path).resolve()
    print("绝对路径:", absolute_path)
    print("cwd: ", current_dir)


if __name__ == "__main__":
    # testing()
    latest_number = get_latest_number()
    get_xkcd_comics(latest_number, count=max_once)  # 下载新漫画
    organize_comics()  # 整理下载的漫画
