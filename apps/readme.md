#### 部署
```shell
#模型下载
# from modelscope import snapshot_download
# model_dir = snapshot_download('qwen/Qwen1.5-7B-Chat-GPTQ-Int4', cache_dir='/root/autodl-tmp')
# model_dir = snapshot_download('qwen/Qwen2-7B-Instruct', cache_dir='/root/autodl-tmp')

# 启动pgsql
/etc/init.d/postgresql start
# 大模型  vlm 需3.0.0
python -m vllm.entrypoints.openai.api_server  --model /root/autodl-tmp/qwen/Qwen2-7B-Instruct-GPTQ-Int4 --served-model-name qwen2  --quantization gptq --port 8001
# python -m vllm.entrypoints.openai.api_server  --model /root/autodl-tmp/qwen/Qwen1___5-7B-Chat-GPTQ-Int4  --served-model-name qwen2  --quantization gptq --port 8001

# cogvlm2-llama3-chinese-chat-19B-int4
python llama3_service.py
# 映射
ssh -fCNg -o ExitOnForwardFailure=no -L 8000:127.0.0.1:8000  -L 65432:127.0.0.1:5432  -L 8001:127.0.0.1:8001 -p 23964 root@connect.bjc1.seetacloud.com

# 启动后端
# .venv/script/bin
# 艾科服务器  conda activate maxkb
python main.py start
```

#### 版面分析
> `https://github.com/RapidAI/RapidOCR/tree/main/python/rapidocr_onnxruntime`  
修改为了apps/common/config/layout_config.py

#### pdf转markdown
> `git clone https://www.modelscope.cn/netease-youdao/QAnything-pdf-parser.git`
> 测试代码在test_md.py

#### 计划
- 问答支持返回图片或根据图片进行回答（将段落中的图片丢入多模态）
- 保存上传知识库的文件
  - 考虑先上传再进行分段处理（当前未上传只进行了分段） 当前为批量上传同时处理，需修改为依次处理，争对不同类型的文件指定处理规则
  - 保存文件上传路径 （document中保存文件地址）
- 根据知识库检索对应文件 检索下载文档
  - 命中后怎么获取最相似的文档？ 知识库存在多个文件时选择综合相似度最高的文档进行下载？
- 调用版面分析改为并发进行
- 并行处理多模态生成图片摘要
- 工具箱：多模态测试问答
- 工具箱：合规地址识别
- 工具箱：pdf转markdown
- 工具箱：版面分析+表格展示
- 工具箱：合同信息抽取
- 工具箱：案件分类、案件信息抽取
- 
