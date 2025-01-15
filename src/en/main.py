import os
import requests
import time  # 确保导入time以使用sleep功能
from seting import *  # 假设该文件包含folder_path、stencil_path、xkcd_url、sleep_time和max_once

# 如果文件夹不存在，则创建
os.makedirs(folder_path, exist_ok=True)
stencil = '''## $title$

![图片不见了~~~]($image$)

[原址]($url$) [下载]($image$)
'''

def writeMD(info, index, title):
    """将漫画信息写入MD文件"""
    text = stencil
    # 替换占位符
    text = text.replace("$image$", info["image"])
    text = text.replace("$url$", xkcd_url + "/" + str(index))
    text = text.replace("$title$", title)  # 替换标题占位符
    
    # 写入文件
    md_file_path = os.path.join(folder_path, f"{index}.md")
    with open(md_file_path, "w") as f:
        f.write(text)
    print(f"已写入漫画信息到 {md_file_path}")

def get_latest_number():
    """获取当前已下载漫画的最新编号"""
    existing_files = os.listdir(folder_path)
    existing_numbers = [
        int(file[:-3]) for file in existing_files if file.endswith('.md')  # 仅处理.md文件
    ]
    latest = max(existing_numbers, default=0)  # 返回最高编号或0
    print(f"最新的编号是: {latest}")
    return latest

def get_xkcd_comics(start_number, count=20):
    """下载XKCD漫画"""
    url_template = 'https://xkcd.com/{}/info.0.json'
    
    for i in range(start_number + 1, start_number + count + 1):
        response = requests.get(url_template.format(i))
        
        if response.status_code == 200:
            comic = response.json()
            info = {"image": comic['img']}
            title = comic['title']  # 获取漫画标题
            writeMD(info, i, title)  # 传递标题到函数
        else:
            print(f"请求漫画编号 {i} 时出错: {response.status_code}")
        
        time.sleep(sleep_time)

def organize_comics():
    """整理下载的漫画文件"""
    all_images = sorted(
        (f for f in os.listdir(folder_path) if f.endswith('.md')),
        key=lambda x: int(x[:-3])  # 提取文件编号
    )
    
    for i in range(0, len(all_images), 10):
        group_number = i // 10 
        group_folder = os.path.join(folder_path, f'{group_number * 10 + 1:04}-{group_number * 10 + 10:04}')
        
        # 创建组文件夹
        os.makedirs(group_folder, exist_ok=True)
        
        for img in all_images[i:i+10]:
            src_path = os.path.join(folder_path, img)
            dst_path = os.path.join(group_folder, img)
            os.rename(src_path, dst_path)  # 移动文件
            print(f"已移动: {img} 到 {group_folder}")

if __name__ == "__main__":
    latest_number = get_latest_number()
    get_xkcd_comics(latest_number, count=max_once)  # 下载新漫画
    organize_comics()  # 整理下载的漫画
