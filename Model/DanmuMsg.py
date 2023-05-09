class DanmuMsg:
    """ 弹幕信息类 """

    def __init__(self, usrname: str, content: str) -> None:
        self.usrname: str = usrname
        self.content: str = content

class DanmuMsgInstance:
    """ 弹幕信息类-工厂 """

    @staticmethod
    def create(event: dict) -> DanmuMsg:
        """ 创建弹幕信息类实例 """
        return DanmuMsg(
            event["data"]["info"][2][1],
            event["data"]["info"][1]
        )