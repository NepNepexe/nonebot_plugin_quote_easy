import json
import random
import difflib  # 引入用于模糊匹配的库
import re
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from nonebot.plugin import on_command
from nonebot.params import CommandArg
from typing import Dict, List
import os
import uuid
import httpx
import logging
# 新增：图片处理和数组拼接所需依赖
import cv2
import numpy as np

# 日志配置
logging.basicConfig(level=logging.DEBUG)

# 定义保存目录
SAVE_DIR = os.path.join(os.getcwd(), "data", "quote")
os.makedirs(SAVE_DIR, exist_ok=True)  # 确保保存目录存在

# 根据群号生成 JSON 文件路径
def get_quotes_file(group_id: int) -> str:
    return os.path.join(SAVE_DIR, f"quotes_{group_id}.json")

# 初始化 JSON 文件（如果文件不存在则创建）
def initialize_json(group_id: int):
    try:
        with open(get_quotes_file(group_id), "r", encoding="utf-8") as f:
            json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(get_quotes_file(group_id), "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False)

# 加载语录数据
def load_quotes(group_id: int) -> Dict[str, List[str]]:
    with open(get_quotes_file(group_id), "r", encoding="utf-8") as f:
        return json.load(f)

# 保存语录数据
def save_quotes(group_id: int, data: Dict[str, List[str]]):
    with open(get_quotes_file(group_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 下载并保存图片到本地
async def download_and_save_image(bot: Bot, file_id: str, group_id: int) -> str:
    try:
        image_info = await bot.get_image(file=file_id)
        image_url = image_info.get('url')
        if not image_url:
            raise Exception("无法获取图片 URL")
        logging.debug(f"获取到图片 URL: {image_url}")
    except Exception as e:
        raise Exception(f"获取图片信息失败: {e}")

    # 下载图片
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(image_url)
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"图片下载失败: {e}")

        # 保存图片
        random_filename = f"{uuid.uuid4().hex}.png"
        image_local_path = os.path.join(SAVE_DIR, str(group_id), random_filename)
        os.makedirs(os.path.dirname(image_local_path), exist_ok=True)
        with open(image_local_path, "wb") as f:
            f.write(response.content)

    logging.debug(f"图片已保存到本地路径: {image_local_path}")
    return image_local_path

# 新增：统一图片尺寸（避免拼接时维度不匹配报错）
def unify_image_size(image_path: str, target_size: tuple = (200, 200)) -> np.ndarray:
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        raise Exception(f"无法读取图片：{image_path}")
    # 缩放至目标尺寸（保持宽高比可选，这里直接强制缩放方便拼接）
    img_resized = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
    return img_resized

# 新增：合并多张图片为一张（使用np.concatenate）
def merge_images(image_paths: List[str], row_col: tuple = (2, 5)) -> str:
    row, col = row_col
    if len(image_paths) != row * col:
        raise Exception(f"图片数量必须为{row*col}张，当前为{len(image_paths)}张")
    
    # 1. 读取并统一所有图片尺寸
    target_size = (200, 200)
    unified_images = [unify_image_size(img_path, target_size) for img_path in image_paths]
    
    # 2. 分批次拼接（先横向拼接每一行，再纵向拼接所有行）
    merged_rows = []
    for i in range(row):
        # 提取当前行的图片
        row_images = unified_images[i*col : (i+1)*col]
        # 横向拼接（axis=1，水平方向）
        row_merged = np.concatenate(row_images, axis=1)
        merged_rows.append(row_merged)
    
    # 3. 纵向拼接所有行（axis=0，垂直方向）
    final_merged = np.concatenate(merged_rows, axis=0)
    
    # 4. 保存合并后的图片
    merge_filename = f"{uuid.uuid4().hex}_merged.png"
    merge_save_path = os.path.join(SAVE_DIR, merge_filename)
    cv2.imwrite(merge_save_path, final_merged)
    
    return merge_save_path

# 添加语录命令
add_quote = on_command("添加语录", priority=50)

@add_quote.handle()
async def handle_add_quote(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 解析输入
    msg_text = args.extract_plain_text().strip()
    msg = event.message
    file_id = None

    # 提取图片的 file ID
    for seg in msg:
        if seg.type == "image":
            file_id = seg.data.get("file")
            break

    # 如果没有直接附带图片，检查是否是回复消息中带图片
    reply_message_id = event.reply.message_id if event.reply else None
    if not file_id and reply_message_id:
        try:
            reply_event = await bot.get_msg(message_id=reply_message_id)
            for seg in reply_event["message"]:
                if seg["type"] == "image":
                    file_id = seg["data"]["file"]
                    break
        except Exception as e:
            await add_quote.finish(f"获取回复消息失败: {e}")

    # 若仍未找到图片，提示用户
    if not file_id:
        await add_quote.finish("图呢？")

    # 检查标签
    if not msg_text:
        await add_quote.finish("tag呢？")

    # 下载并保存图片到本地
    try:
        image_local_path = await download_and_save_image(bot, file_id, event.group_id)
    except Exception as e:
        await add_quote.finish(str(e))

    # 保存图片路径和标签
    group_id = event.group_id
    initialize_json(group_id)
    quotes = load_quotes(group_id)

    if msg_text not in quotes:
        quotes[msg_text] = []
    quotes[msg_text].append(image_local_path)
    save_quotes(group_id, quotes)

    # 统计语录总数
    total_quotes = sum(len(images) for images in quotes.values())
    await add_quote.send(f"整好了，当前有{total_quotes}条语录~")

# 查看语录命令
get_quote = on_command("语录", priority=50)

@get_quote.handle()
async def handle_get_quote(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    group_id = event.group_id
    tag = args.extract_plain_text().strip()

    # 初始化和加载群语录数据
    initialize_json(group_id)
    quotes = load_quotes(group_id)

    # 如果提供了标签，则模糊匹配
    if tag:
        close_matches = difflib.get_close_matches(tag, quotes.keys(), n=1, cutoff=0.3)
        if close_matches:
            matched_tag = close_matches[0]
            image_local_path = random.choice(quotes[matched_tag])  # 随机选取该标签下的一条语录
            await get_quote.send(MessageSegment.image(f"file:///{os.path.abspath(image_local_path)}") + f"标签：{matched_tag}")
        else:
            await get_quote.finish("没有找到这个标签的语录。")
    else:
        # 未提供标签，则随机选取一条语录
        all_images_with_tags = [(url, t) for t, urls in quotes.items() for url in urls]
        if not all_images_with_tags:
            await get_quote.finish("当前没有任何语录。")
        image_local_path, matched_tag = random.choice(all_images_with_tags)  # 随机选取一条语录及其标签
        await get_quote.send(MessageSegment.image(f"file:///{os.path.abspath(image_local_path)}") + f"标签：{matched_tag}")

# 删除语录命令
delete_quote = on_command("删除语录", priority=50)

@delete_quote.handle()
async def handle_delete_quote(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 解析输入
    tag = args.extract_plain_text().strip()

    if not tag:
        await delete_quote.finish("请提供要删除的语录标签。")

    # 初始化和读取群语录数据
    group_id = event.group_id
    initialize_json(group_id)
    quotes = load_quotes(group_id)

    # 精确匹配标签并删除
    if tag in quotes:
        del quotes[tag]
        save_quotes(group_id, quotes)
        await delete_quote.send(f"成功删除标签 '{tag}' 的所有语录。")
    else:
        await delete_quote.finish("未找到指定的标签。")

# 新增：十连语录命令（触发词「十连语录」）
ten_quote = on_command("十连语录", priority=50)

@ten_quote.handle()
async def handle_ten_quote(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    # 1. 初始化和加载群语录数据
    initialize_json(group_id)
    quotes = load_quotes(group_id)

    # 2. 提取所有语录图片路径
    all_image_paths = [url for urls in quotes.values() for url in urls]
    total_count = len(all_image_paths)

    # 3. 检查是否有足够的图片（至少10张）
    if total_count < 10:
        await ten_quote.finish(f"当前语录图片仅有{total_count}张，不足10张无法十连抽~")

    # 4. 随机选取10张不重复的图片（若允许重复可改为random.choices）
    selected_image_paths = random.sample(all_image_paths, 10)

    # 5. 合并图片（2行5列，使用np.concatenate实现）
    try:
        merged_image_path = merge_images(selected_image_paths, row_col=(2, 5))
    except Exception as e:
        await ten_quote.finish(f"图片合并失败：{e}")

    # 6. 发送合并后的图片
    await ten_quote.send(MessageSegment.image(f"file:///{os.path.abspath(merged_image_path)}") + "十连抽完成~")
