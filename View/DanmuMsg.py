from .main import room
from Model import DanmuMsg
from ViewModel import DanmuMsgInstance

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