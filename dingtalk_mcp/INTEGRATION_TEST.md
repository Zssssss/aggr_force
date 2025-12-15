# 钉钉文档MCP服务集成测试文档

## 1. 测试目的
验证钉钉文档MCP服务的整体流程是否正常，包括配置加载、客户端初始化、API调用等各个环节的交互。

## 2. 测试环境
### 2.1 系统环境
- 操作系统: Linux/Windows/macOS
- Python版本: 3.7+
- 网络: 能够访问钉钉开放平台API

### 2.2 依赖准备
```bash
pip install httpx mcp
```

### 2.3 配置准备
在系统环境变量中设置以下配置项：
```bash
export DINGTALK_APP_KEY="your_app_key"
export DINGTALK_APP_SECRET="your_app_Secret"
```

## 3. 测试流程
1. 配置加载测试
2. 客户端初始化测试
3. access_token获取测试
4. 文档创建测试
5. 文档内容获取测试
6. 文档内容更新测试
7. 文档列表获取测试

## 4. 测试用例

### 4.1 配置加载测试
**测试目的**: 验证配置能够正确加载  
**测试步骤**:
```python
from dingtalk_mcp.config import load_config

# 尝试加载配置
try:
    config = load_config()
    print("配置加载成功")
    print(f"AppKey: {config.app_key}")
    print(f"Base URL: {config.base_url}")
except Exception as e:
    print(f"配置加载失败: {e}")
```

**预期结果**: 配置加载成功，能够看到AppKey和Base URL信息


### 4.2 客户端初始化测试
**测试目的**: 验证客户端能够正确初始化  
**测试步骤**:
```python
from dingtalk_mcp.config import load_config
from dingtalk_mcp.dingtalk_client import DingTalkClient

# 加载配置
config = load_config()

# 初始化客户端
try:
    client = DingTalkClient(config)
    print("客户端初始化成功")
except Exception as e:
    print(f"客户端初始化失败: {e}")
```

**预期结果**: 客户端初始化成功


### 4.3 access_token获取测试
**测试目的**: 验证能够正确获取access_token  
**测试步骤**:
```python
from dingtalk_mcp.config import load_config
from dingtalk_mcp.dingtalk_client import DingTalkClient

# 加载配置并初始化客户端
config = load_config()
client = DingTalkClient(config)

# 尝试获取access_token
try:
    access_token = client.get_access_token()
    print(f"获取access_token成功: {access_token[:20]}...")  # 只显示前20位
except Exception as e:
    print(f"获取access_token失败: {e}")
```

**预期结果**: 成功获取access_token，显示部分token信息


### 4.4 完整流程测试
**测试目的**: 验证从文档创建到删除的完整流程  
**测试步骤**:
```python
from dingtalk_mcp.config import load_config
from dingtalk_mcp.dingtalk_client import DingTalkClient

# 加载配置并初始化客户端
config = load_config()
client = DingTalkClient(config)

# 1. 创建文档
print("1. 创建文档...")
try:
    create_result = client.create_document(
        title="测试文档",
        content="这是一个测试文档"
    )
    print(f"创建文档成功: {create_result}")
    document_id = create_result["document_id"]
except Exception as e:
    print(f"创建文档失败: {e}")
    exit()

# 2. 获取文档内容
print("\n2. 获取文档内容...")
try:
    get_result = client.get_document(document_id)
    print(f"获取文档内容成功: {get_result}")
except Exception as e:
    print(f"获取文档内容失败: {e}")

# 3. 更新文档内容
print("\n3. 更新文档内容...")
try:
    update_result = client.update_document(
        document_id=document_id,
        content="这是更新后的文档内容",
        mode="overwrite"
    )
    print(f"更新文档内容成功: {update_result}")
except Exception as e:
    print(f"更新文档内容失败: {e}")

# 4. 获取更新后的文档内容
print("\n4. 获取更新后的文档内容...")
try:
    get_result = client.get_document(document_id)
    print(f"获取更新后的文档内容成功: {get_result}")
except Exception as e:
    print(f"获取更新后的文档内容失败: {e}")

# 5. 列出文档
print("\n5. 列出文档...")
try:
    list_result = client.list_documents(page_size=5)
    print(f"列出文档成功: {list_result}")
except Exception as e:
    print(f"列出文档失败: {e}")
```

**预期结果**: 所有步骤都成功完成，能够看到完整的流程输出


## 5. 错误处理测试
### 5.1 无效文档ID测试
**测试目的**: 验证无效文档ID的错误处理  
**测试步骤**:
```python
from dingtalk_mcp.config import load_config
from dingtalk_mcp.dingtalk_client import DingTalkClient

# 加载配置并初始化客户端
config = load_config()
client = DingTalkClient(config)

# 尝试使用无效文档ID
try:
    client.get_document("invalid_document_id")
except Exception as e:
    print(f"错误处理正常: 无效文档ID时获取错误: {e}")
```

**预期结果**: 能够正确捕获错误并显示错误信息


## 6. 测试总结
- 如果所有测试用例都通过，说明系统流程正常
- 如果某个环节失败，需要根据错误信息定位问题
  - 配置错误: 检查环境变量是否正确
  - 网络问题: 检查网络连接是否正常
  - API权限: 检查应用是否有相关API的调用权限

## 7. 注意事项
1. 确保应用已在钉钉开放平台开通文档管理权限
2. 测试时使用真实的AppKey和AppSecret
3. 测试完成后建议删除测试文档
4. 注意保护access_token等敏感信息