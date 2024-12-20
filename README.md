# NoneBot语录机器人使用手册

本人第一次开发插件，使用ChatGPT辅助完成代码编写  

欢迎使用我的语录机器人！以下是关于如何使用机器人进行语录管理的详细指南，包括添加、查看和删除语录的功能介绍。

## 目录

- [功能概览](#功能概览)
- [添加语录](#如何添加语录)
- [查看语录](#如何查看语录)
- [删除语录](#如何删除语录)

## 功能概览

| 功能 | 描述 |
| --- | --- |
| **添加语录** | 用户可以向机器人发送带有特定标签的图片，以将其作为语录添加到数据库中。 |
| **查看语录** | 用户可以通过指定标签来查找已有的语录，或随机查看一条语录。 |
| **删除语录** | 管理员可以删除特定标签下的所有语录。 |

## 如何添加语录

### 指令格式
- 添加语录 <标签>

### 操作步骤

1. 在聊天框中输入 `添加语录` 命令后跟一个空格。
2. 输入您希望为这条语录设定的标签名称。
3. 发送带有图片的消息。
4. 如果是通过回复某条含有图片的消息来添加语录，请确保直接回复那条消息，并在回复内容前加上 `添加语录` 命令及标签。

### 注意事项

- 必须包含至少一张图片。
- 标签不能为空。
- 如果没有提供图片或标签，机器人会提示“图呢？”或要求重新输入标签。

## 如何查看语录

### 指令格式

- 查看特定标签的语录：
  语录 <标签>
- 查看随机语录：
  语录

### 操作步骤

1. 要查看特定标签的语录，请在命令后跟随该标签名称。
2. 若想查看随机语录，只需发送 `语录` 命令即可。
3. 机器人会从相应的标签或所有语录中随机选择一条语录展示给用户。

### 注意事项

- 如果指定的标签不存在，机器人会通知“没有找到这个标签的语录”。
- 如果数据库中没有任何语录，机器人会显示“当前没有任何语录”。

## 如何删除语录

### 指令格式
- 删除语录 <标签>

### 操作步骤

1. 在聊天框中输入 `删除语录` 命令后跟一个空格。
2. 输入您想要删除的语录标签。
3. 发送指令。

### 注意事项

- 只有管理员才有权限执行此操作。
- 如果标签不存在，机器人会提示“未找到指定的标签”。
- 成功删除后，机器人会反馈“成功删除标签 ‘<标签>’ 的所有语录”。

## 更新

v0.0.2
- Json换成UTF-8编码，方便手动修改语录
- 增加TAG检查，添加语录必须附带TAG
---
v0.0.3
- 修改语录保存方式，把语录保存到本地

如果您在使用过程中遇到任何问题或者有任何建议，欢迎随时联系我。感谢您的支持！
