本人第一次写插件，在ChatGPT的辅助下完成的代码编写
功能概览
添加语录：用户可以向机器人发送带有特定标签的图片，以将其作为语录添加到数据库中。
查看语录：用户可以通过指定标签来查找已有的语录，或随机查看一条语录。
删除语录：管理员可以删除特定标签下的所有语录。
如何添加语录
指令
添加语录 <标签>

操作步骤
在聊天框中输入 添加语录 命令后跟一个空格。
输入您希望为这条语录设定的标签名称。
发送带有图片的消息。
如果是通过回复某条含有图片的消息来添加语录，请确保直接回复那条消息，并在回复内容前加上 添加语录 命令及标签。
注意事项
必须包含至少一张图片。
标签不能为空。
如果没有提供图片或标签，机器人会提示“图呢？”或要求重新输入标签。
如何查看语录
指令
查看特定标签的语录：语录 <标签>
查看随机语录：语录
操作步骤
要查看特定标签的语录，请在命令后跟随该标签名称。
若想查看随机语录，只需发送 语录 命令即可。
机器人会从相应的标签或所有语录中随机选择一条语录展示给用户。
注意事项
如果指定的标签不存在，机器人会通知“没有找到这个标签的语录”。
如果数据库中没有任何语录，机器人会显示“当前没有任何语录”。
如何删除语录
指令
删除语录 <标签>

操作步骤
在聊天框中输入 删除语录 命令后跟一个空格。
输入您想要删除的语录标签。
发送指令。
注意事项
只有管理员才有权限执行此操作。
如果标签不存在，机器人会提示“未找到指定的标签”。
成功删除后，机器人会反馈“成功删除标签 ‘<标签>’ 的所有语录”。
请根据上述说明正确使用机器人功能，如果您遇到任何问题或有任何建议，欢迎随时联系我们。感谢您的支持！
