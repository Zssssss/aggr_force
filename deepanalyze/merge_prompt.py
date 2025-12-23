from datetime import datetime
def get_prompt(query, ref_data=None):
    from jinja2 import Template
    prompt_template = Template("""
{%- if has_ref_data %}
基于以下数据:
{{ ref_data }}
{%- endif %}

用户提出的问题是“{{question}}”


## 任务目标
请深入理解用户提出的业务问题，基于自身知识与已有数据，将该问题系统性拆解为一组**可验证的假设结构**。  
通过为每个假设设计可量化、可执行的验证路径，形成一份完整、客观、逻辑清晰的研究任务规划。

最终目标是：为用户提供一套可用于“验证原因—收集证据—定位问题”的结构化分析方案。

## 任务拆解原则
在制定分析与任务计划时，请遵循以下原则：

1. **假设驱动**  
   - 从多个可能角度拆解问题成若干核心假设  
   - 各假设之间应尽量相互独立、覆盖全面

2. **可验证性**  
   - 每个假设必须能够通过数据、指标或工具进行验证  
   - 验证方式需具备明确的观测对象和判定标准

3. **量化优先**  
   - 验证项应尽量采用可量化指标、日志、监控或实验数据  
   - 避免仅停留在主观判断或定性描述

4. **权重评估**  
   - 为每个假设分配一个“可能性权重”，用于表达其相对重要性或优先级

5. **工具导向**  
   - 明确指出验证每个问题所需的 MCP 工具  
   - 如涉及参数，请清晰描述调用所需的关键参数


## 输出要求
请**仅以 JSON 结构输出**研究任务规划，不要附加任何额外说明文字。  
输出格式必须严格符合以下结构示例：
```json
{
  "场景": "{{ question }} 深度分析任务规划",
  "假设映射": [
    {
      "假设": "假设原因描述",
      "权重": "0.3",
      "验证项": [
        {
          "问题": "需要被验证的具体问题",
          "MCP工具": [
            "工具名称1",
            "工具名称2",
          ]
          "参数": {
            "示例参数1": "说明",
            "示例参数2": "说明"
          }
        },
        ... //其他子问题
      ]
    }
    ... //其他假设
  ]
}
""")  

    return prompt_template.render(
        has_ref_data=ref_data is not None,
        ref_data=ref_data,
        question=query,
        CURRENT_TIME=datetime.now().strftime('%Y年%m月%d日'),
    )
 
 
if __name__ == "__main__":
    query="用户停留时长下降"
    ref_data = open("aggregated_data.txt").read()
    p=get_prompt(query,ref_data=ref_data)
    print(p)