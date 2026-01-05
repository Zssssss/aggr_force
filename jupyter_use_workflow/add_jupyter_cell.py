#!/usr/bin/env python3
"""
向Jupyter Notebook添加新cell的脚本
"""
import requests
import json

# Jupyter服务器配置
JUPYTER_URL = "http://10.133.168.176:10618"
TOKEN = "4a210f1fcc49eb8f62d5838d61b865038565272ae3c4c062"
NOTEBOOK_PATH = "jupyter/search_api_lihu-zsss-0104.ipynb"

# 并查集代码
UNION_FIND_CODE = '''class UnionFind:
    """并查集数据结构实现"""
    
    def __init__(self, n):
        """初始化并查集，n为元素个数"""
        self.parent = list(range(n))  # 每个元素的父节点
        self.rank = [0] * n  # 每个集合的秩（深度）
        self.count = n  # 连通分量的数量
    
    def find(self, x):
        """查找元素x的根节点，并进行路径压缩"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        """合并元素x和y所在的集合"""
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False  # 已经在同一集合中
        
        # 按秩合并
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        
        self.count -= 1
        return True
    
    def connected(self, x, y):
        """判断元素x和y是否在同一集合中"""
        return self.find(x) == self.find(y)
    
    def get_count(self):
        """获取连通分量的数量"""
        return self.count


# 测试代码
if __name__ == "__main__":
    # 创建一个包含5个元素的并查集
    uf = UnionFind(5)
    print(f"初始连通分量数: {uf.get_count()}")
    
    # 合并操作
    uf.union(0, 1)
    print(f"合并0和1后，连通分量数: {uf.get_count()}")
    
    uf.union(2, 3)
    print(f"合并2和3后，连通分量数: {uf.get_count()}")
    
    uf.union(0, 2)
    print(f"合并0和2后，连通分量数: {uf.get_count()}")
    
    # 查询操作
    print(f"0和3是否连通: {uf.connected(0, 3)}")
    print(f"1和4是否连通: {uf.connected(1, 4)}")'''

def add_cell_to_notebook():
    """向notebook添加新的cell"""
    
    # 1. 获取notebook内容
    url = f"{JUPYTER_URL}/api/contents/{NOTEBOOK_PATH}"
    headers = {
        "Authorization": f"token {TOKEN}"
    }
    
    print(f"正在获取notebook内容: {url}")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"获取notebook失败: {response.status_code}")
        print(response.text)
        return False
    
    notebook_data = response.json()
    content = notebook_data['content']
    
    # 2. 添加新的cell
    new_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": UNION_FIND_CODE.split('\n')
    }
    
    content['cells'].append(new_cell)
    
    # 3. 保存更新后的notebook
    update_data = {
        "type": "notebook",
        "content": content
    }
    
    print("正在保存更新后的notebook...")
    response = requests.put(url, headers=headers, json=update_data)
    
    if response.status_code == 200:
        print("✅ 成功添加并查集代码到notebook!")
        return True
    else:
        print(f"❌ 保存失败: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    add_cell_to_notebook()
