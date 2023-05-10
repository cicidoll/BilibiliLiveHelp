class DanmuMsg:
    """ 弹幕信息类 """

    def __init__(self, usrname: str, content: str) -> None:
        self.usrname: str = usrname
        self.content: str = content