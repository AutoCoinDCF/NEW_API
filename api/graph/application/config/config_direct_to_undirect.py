""" which edges should be transform to undirect edges """

undirected_link_types = {
    "父亲": "父子",
    "子女": "亲子",
    "母亲": "母子",
    "母组织": "上下级组织",
    "子组织": "上下级组织",
    "位于": "位于",
    "兄弟姐妹": "兄弟姐妹",
    "夫妻": "夫妻",
    "教育经历": "教育经历",
}
