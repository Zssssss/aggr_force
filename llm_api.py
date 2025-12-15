from langchain_community.llms import OpenAI, Qianfan, Baichuan
# OpenAI
llm_openai = OpenAI(api_key="sk-xxx")
result_openai = llm_openai("Hello world")

# 百度千帆
llm_qianfan = Qianfan(qianfan_api_key="xxx", qianfan_secret_key="xxx")
result_qianfan = llm_qianfan("你好世界")

# 阿里百川
llm_baichuan = Baichuan(api_key="xxx")
result_baichuan = llm_baichuan("你好世界")