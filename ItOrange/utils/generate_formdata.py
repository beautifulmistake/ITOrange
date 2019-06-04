"""
此工具文件用于生成POST 请求所需要的 formdata 参数
"""

import json


# 初始的formdata
base_data = {
            "pagetotal": str(134260), "total": str(0), "per_page": str(20), "page": str(1), "scope": "", "sub_scope": "", "round": [],
            "location": "", "prov": "", "city": [], "status": "", "sort": "", "selected": "", "year": [],
            "com_fund_needs": "", "keyword": ""
        }
# 初始页号
page = 1

# 保存 formdata 的文件路径
FILE_PATH = r'F:\project\ItOrange\ItOrange\keyword\formdata.json'

with open(FILE_PATH, 'w+', encoding='utf-8') as f:
    # 此处的逻辑需要做修改，pagetotal 是数据总条数，不是总页数
    while page < int(base_data['pagetotal']):
        base_data.update([("page", str(page))])
        data = json.dumps(base_data, ensure_ascii=False)
        f.write(data)
        f.write("\n")
        page += 1
