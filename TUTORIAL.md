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
| 4 | Prompt Template 提示词模板 | ✅ 已完成 |
| 5 | LCEL 链式调用 | ✅ 已完成 |
| 6 | 输出解析 Output Parser | ⏳ 进行中 |
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

---

## 第 4 步：Prompt Template 提示词模板

### 做了什么

上一步里，发给模型的话是硬编码的字符串 `"你好，用一句话介绍一下你自己"`。真实场景里，提示词的“骨架”通常是固定的，变化的只是其中几个变量（比如用户输入的内容、目标语言、角色设定等）。`ChatPromptTemplate` 就是用来把“骨架”和“变量”拆开管理的工具。

新增 `04_prompt_template.py`，做了一个翻译小助手：

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个专业翻译，把用户输入的内容翻译成{language}，只输出翻译结果，不要多余解释。"),
        ("human", "{text}"),
    ]
)

messages = prompt.format_messages(language="英文", text="今天天气真好，我们去公园散步吧。")
```

- `from_messages([...])`：定义一段“对话骨架”，每一项是 `(角色, 模板字符串)`。这里用了两种角色：
  - `"system"`：系统提示，通常用来设定模型的角色/行为规则，用户看不到这段话，但它会影响模型每次的回答方式。
  - `"human"`：用户说的话。
  - 模板字符串里的 `{language}`、`{text}` 是占位符，语法上和 Python 的 `str.format()` 一致。
- `prompt.format_messages(language="英文", text="...")`：把占位符换成真实的值，返回一个消息列表。运行后打印出来是：

  ```python
  [SystemMessage(content='你是一个专业翻译，把用户输入的内容翻译成英文，只输出翻译结果，不要多余解释。', ...),
   HumanMessage(content='今天天气真好，我们去公园散步吧。', ...)]
  ```

  可以看到，`ChatPromptTemplate` 最终产出的还是上一步里 `llm.invoke()` 认识的那种消息对象（`SystemMessage`/`HumanMessage`），只是不用我们手写了。

- 把这个消息列表传给 `llm.invoke(messages)`，实际输出：

  ```
  The weather is so nice today. Let's go for a walk in the park.
  ```

### 为什么这样做

- **骨架和变量分离**：如果不用模板，每次换一个用户输入，都要自己拼字符串、小心处理换行和转义；有了模板，只需要传变量，模板本身可以被复用、被测试、被单独维护（比如以后把提示词存成配置文件，不用改代码）。
- **`system` 角色的意义**：把“翻译规则”放进 `system` 而不是拼进 `human` 消息里，是因为多数模型（包括 DeepSeek）会更稳定地遵守 `system` 里的设定，且用户消息里只保留“真正要处理的内容”，两者职责分开后更容易复用同一套 `system` 提示词处理不同的用户输入。
- 目前是手动调用 `format_messages()` 再手动调用 `llm.invoke()`，这两步之间的“胶水代码”正是下一步 LCEL 要解决的问题——把 `prompt` 和 `llm`直接“粘”成一条链。

---

## 第 5 步：LCEL 链式调用

### 做了什么

上一步的用法是：

```python
messages = prompt.format_messages(language="英文", text="...")
response = llm.invoke(messages)
```

两行代码、两个独立的调用。LCEL（LangChain Expression Language）用 `|` 运算符把它们合并成一条“链”，新增的 `05_lcel_chain.py` 把 `prompt` 和 `llm` 拼在了一起：

```python
chain = prompt | llm

response = chain.invoke({"language": "英文", "text": "今天天气真好，我们去公园散步吧。"})
print(response.content)
```

运行结果和上一步完全一样：

```
The weather is so nice today. Let's go for a walk in the park.
```

`chain = prompt | llm` 这一行，把两个组件（`prompt` 和 `llm`）组合成了一个新的可运行对象 `chain`。调用 `chain.invoke(变量字典)` 时，LangChain 在背后做的事情，其实就是把上一步的两行代码自动串起来：

1. 先把传入的字典 `{"language": ..., "text": ...}` 交给 `prompt`，等价于 `prompt.format_messages(**输入)`，产出消息列表；
2. 再把这个消息列表自动交给 `llm`，等价于 `llm.invoke(消息列表)`，产出最终的 `AIMessage`。

也就是说，`chain.invoke(x)` 约等于 `llm.invoke(prompt.format_messages(**x))`，只是不需要我们手动写中间那一步、也不需要关心上一环节的输出格式是否匹配下一环节的输入格式——只要用 `|` 连起来，LangChain 就负责对接好。

### 为什么这样做

- **可读性**：`prompt | llm` 这种写法本身就在描述“数据先经过 prompt，再经过 llm”，比看两行分散的赋值语句更直观地表达出处理流程。
- **可扩展性**：`|` 可以一直往后接，比如 `prompt | llm | 某个后处理组件 | 另一个组件`，管道有多长都是同样的写法。下一步要学的 `StrOutputParser` 就是接在 `llm` 后面的第三个环节，用来把 `AIMessage` 对象变成一个纯字符串。
- **统一接口**：`prompt`、`llm`，以及后面会遇到的 parser、retriever 等，都实现了同一套“可运行（Runnable）”接口（`invoke`/`batch`/`stream` 等），这也是它们能用同一个 `|` 运算符自由拼接的原因——这是 LangChain 目前的核心设计范式，比早期版本里各种专用的 `XXXChain` 类更统一、更灵活。
