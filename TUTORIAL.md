# LangChain 从零入门教程

本教程配合本仓库代码一起学习，目标是从零搭建一个完整的 LangChain 项目。

- LLM 服务商：DeepSeek（OpenAI 兼容接口）
- 依赖管理：pip + `requirements.txt`
- 每一步都会在这里补充讲解和对应的代码文件

> **Windows 小贴士**：如果终端里运行脚本时中文输出显示为乱码，是 Windows 控制台默认编码（GBK）和 Python 输出编码（UTF-8）不一致导致的，和代码逻辑无关。加上环境变量 `PYTHONUTF8=1` 即可解决，例如：`$env:PYTHONUTF8=1; .venv/Scripts/python.exe xxx.py`

## 大纲

| 步骤 | 内容 | 状态 |
| --- | --- | --- |
| 1 | 环境准备与依赖安装 | ✅ 已完成 |
| 2 | 配置 DeepSeek API Key | ✅ 已完成 |
| 3 | 第一个 LLM 调用 | ✅ 已完成 |
| 4 | Prompt Template 提示词模板 | ⏳ 进行中 |
| 5 | LCEL 链式调用 | 未开始 |
| 6 | 输出解析 Output Parser | 未开始 |
| 7 | 对话记忆 Memory | 未开始 |
| 8 | 工具调用与 Agent | 未开始 |
| 9 | RAG 检索增强问答（可选） | 未开始 |

---

## 第 1 步：环境准备与依赖安装

### 做了什么

在 `requirements.txt` 中声明了三个直接依赖：

```
langchain==1.3.14
langchain-openai==1.4.0
python-dotenv==1.2.2
```

- **langchain**：核心框架，提供 Prompt、Chain、Agent 等抽象。
- **langchain-openai**：LangChain 对接 OpenAI 兼容接口（Chat/Embedding 等）的适配包。DeepSeek 提供的 API 与 OpenAI 接口格式兼容，所以我们后面会用这个包里的 `ChatOpenAI` 类，只是把请求地址指向 DeepSeek。
- **python-dotenv**：从 `.env` 文件读取环境变量（比如 API Key），避免把密钥写死在代码里。

然后用项目自带的虚拟环境 `.venv` 安装依赖：

```powershell
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

安装时会自动带出一批间接依赖（比如 `langchain-core`、`openai`、`pydantic`、`tiktoken` 等），这些不需要逐个记住，`requirements.txt` 里只锁定我们直接用到的三个包版本即可，保证教程可复现。

### 为什么这样做

- 固定版本号（`==`）是为了让教程里的代码示例在你未来重新安装时行为一致，不会因为某天 LangChain 发布了破坏性更新（LangChain 大版本之间 API 变化较多）而跑不通。
- 选 `langchain-openai` 而不是国内厂商专用的 SDK（如 `dashscope`），是因为 DeepSeek official 兼容 OpenAI 协议，用最主流的 `ChatOpenAI` 接口学习，之后换成任何其他 OpenAI 兼容服务商（Moonshot、通义千问兼容模式等）都只需要改 `base_url` 和 `model` 名字，学到的是通用能力而不是某个厂商的专有 SDK。

---

## 第 2 步：配置 DeepSeek API Key

### 做了什么

1. 在 `.gitignore` 中新增了一行 `.env`，确保密钥文件永远不会被提交到 Git。
2. 新增 `.env.example` 作为模板文件（**这个文件会被提交**，方便别人 clone 项目后知道需要配置哪些变量）：

   ```
   DEEPSEEK_API_KEY=your-api-key-here
   ```

3. 本地复制出一份 `.env`（**这个文件不会被提交**），并把里面的占位符换成了你自己的真实 API Key。

这一步纯粹是配置，不涉及代码逻辑，`load_dotenv()` 的实际效果会在下一步第一次调用 LLM 时一并验证——`load_dotenv()` 会读取项目根目录下的 `.env` 文件，把里面的键值对写入当前进程的环境变量，之后就能用 `os.getenv()` 读出来，效果等价于你在终端里手动 `export`/`set` 了这个变量，只是不用每次开新终端都重新设置。

### 为什么这样做

- **密钥绝不写死在代码里、也不提交到 Git**：一旦密钥被提交过一次，即使后来删除，它依然会留在 Git 历史记录里，别人 clone 仓库后用 `git log` 就能翻出来。用 `.env` + `.gitignore` 是业界标准做法。
- **`.env.example` 提交、`.env` 不提交**：这样任何人拿到这个仓库，都能通过 `.env.example` 知道项目需要哪些环境变量，自己复制一份填上真实值即可，不需要额外的文档说明配置项。
- 用 `python-dotenv` 而不是要求用户每次手动 `set` 环境变量，是因为 `.env` 文件形式更方便管理多个变量，且和几乎所有 Python 项目、部署平台（Docker、CI）的约定一致。

---

## 第 3 步：第一个 LLM 调用

### 做了什么

新增 `03_first_llm_call.py`：

```python
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)

response = llm.invoke("你好，用一句话介绍一下你自己")
print(response.content)
```

运行 `.venv/Scripts/python.exe 03_first_llm_call.py`，实际输出：

```
你好！我是 DeepSeek，一个由深度求索公司开发的免费 AI 助手，能帮你解答问题、处理文档、分析信息，还能陪你聊天～
```

代码逐行拆解：

- `ChatOpenAI(...)`：LangChain 里对接“类 OpenAI 协议”聊天模型的标准类。三个关键参数：
  - `model`：DeepSeek 这边对话模型的名字是 `deepseek-chat`（官方还有一个 `deepseek-reasoner` 推理模型，之后可以试试换成它对比效果）。
  - `api_key`：从上一步 `.env` 里读出来的密钥，`load_dotenv()` 已经把它放进了环境变量。
  - `base_url`：这是让 `ChatOpenAI` 从访问 OpenAI 官方接口，改成访问 DeepSeek 接口地址的关键一行，其他参数和用法完全不变。
- `llm.invoke("...")`：向模型发送一次请求并同步等待返回，返回值是一个 `AIMessage` 对象，`.content` 是其中的文本内容（这个对象还携带了其他信息，比如 token 用量，后面用到时再展开）。

### 为什么这样做

- 只改 `base_url` 就能切换服务商，正是第 1 步选择 `langchain-openai` 而不是厂商专属 SDK 的价值所在：一套写法，换厂商不用重学。
- 用 `llm.invoke()` 而不是更底层的 `requests.post()` 直接调 HTTP 接口，是因为 LangChain 把请求组装、重试、返回结构解析都封装好了，后面学 Prompt Template、Chain、Agent 时都建立在这同一个 `llm` 对象之上，不需要重复造轮子。
