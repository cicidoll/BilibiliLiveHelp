from bilibili_api import live, sync
from Model import DanmuMsgInstance, DanmuMsg

room = live.LiveDanmaku(23029447)

msg_template = "%s: %s"

@room.on('DANMU_MSG')
async def on_danmaku(event):
    # 收到弹幕
    try:
        msg_instance: DanmuMsg = DanmuMsgInstance.create(event)
        print(
            msg_template % (
                msg_instance.usrname,
                msg_instance.content
                )
            )
    except Exception as identifier:
        print(identifier)

sync(room.connect())