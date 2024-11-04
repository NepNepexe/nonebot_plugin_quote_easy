import json
import random
import difflib  # 引入用于模糊匹配的库
import re
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from nonebot.plugin import on_command
from nonebot.params import CommandArg
from typing import Dict, List
import os

# 定义保存目录
SAVE_DIR = "data/quote"

# 确保保存目录存在
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

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

# 正则表达式用于提取图片文件路径
rt = r"\[CQ:image,file=(.*?),subType=[\S]*,url=[\S]*\]"

# 添加语录命令
add_quote = on_command("添加语录", priority=50)

@add_quote.handle()
async def handle_add_quote(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 解析输入
    msg_text = args.extract_plain_text().strip()
    msg = str(event.message)
    files = re.findall(rt, msg)
    reply_message_id = event.reply.message_id if event.reply else None

    # 检查是否提供了标签
    if not msg_text:
        await add_quote.finish("tag呢？")

    # 验证输入格式是否包含图片或回复图片
    if not (files or reply_message_id):
        await add_quote.finish("图呢？")

    # 获取图片文件路径
    if files:
        file_id = files[0]
    elif reply_message_id:
        try:
            reply_event = await bot.get_msg(message_id=reply_message_id)
            reply_message_segments = reply_event.get("message", [])
            reply_files = [segment["data"]["file"] for segment in reply_message_segments if segment["type"] == "image"]
            if not reply_files:
                await add_quote.finish("回复的消息中没有图片。")
            file_id = reply_files[0]
        except Exception as e:
            await add_quote.finish(f"获取回复消息失败: {e}")

    # 获取图片信息
    try:
        image_info = await bot.call_api('get_image', **{'file': file_id})
        image_url = image_info['url']
    except Exception as e:
        await add_quote.finish(f"获取图片信息失败: {e}")

    # 保存图片路径和标签
    tag = msg_text
    image_local_path = file_id

    # 初始化和读取群语录数据
    group_id = event.group_id
    initialize_json(group_id)
    quotes = load_quotes(group_id)

    # 添加新的语录
    if tag not in quotes:
        quotes[tag] = []
    quotes[tag].append(image_local_path)
    
    # 保存数据到 JSON 文件
    save_quotes(group_id, quotes)

    # 获取当前语录总数
    total_quotes = sum(len(images) for images in quotes.values())

    # 回复信息
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

    # 如果提供了标签，则进行模糊匹配查找
    if tag:
        # 使用模糊匹配找到最接近的标签
        close_matches = difflib.get_close_matches(tag, quotes.keys(), n=1, cutoff=0.6)
        if close_matches:
            matched_tag = close_matches[0]
            image_local_path = random.choice(quotes[matched_tag])  # 随机选取该标签下的一条语录
            try:
                image_info = await bot.call_api('get_image', **{'file': image_local_path})
                image_url = image_info['url']
                await get_quote.send(MessageSegment.image(image_url) + f"标签：{matched_tag}")
            except Exception as e:
                await get_quote.finish(f"获取图片信息失败: {e}")
        else:
            await get_quote.finish("没有找到这个标签的语录。")
    else:
        # 未提供标签，则随机选取一条语录
        all_images_with_tags = [(url, t) for t, urls in quotes.items() for url in urls]
        if not all_images_with_tags:
            await get_quote.finish("当前没有任何语录。")
        image_local_path, matched_tag = random.choice(all_images_with_tags)  # 随机选取一条语录及其标签
        try:
            image_info = await bot.call_api('get_image', **{'file': image_local_path})
            image_url = image_info['url']
            await get_quote.send(MessageSegment.image(image_url) + f"标签：{matched_tag}")
        except Exception as e:
            await get_quote.finish(f"获取图片信息失败: {e}")

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
