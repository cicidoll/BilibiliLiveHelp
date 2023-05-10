import json

class JsonFile:
    """ 操作json文件 """

    @staticmethod
    def load_json(filepath: str) -> dict:
        """ 读取json文件 """
        try:
            with open(filepath, 'r', encoding='utf8') as (json_file):
                json_data = json.load(json_file)
                return json_data
        except Exception as identifier:
            print(identifier)

    @staticmethod
    def save_json_file(file_name: str, data: dict) -> None:
        """ 将json数据保存为文件 """
        json_data = json.dumps(data, indent = 4, separators=(",", ": "), ensure_ascii=False)
        with open(file_name, 'w', encoding="utf-8") as write_file:
            write_file.write(json_data)