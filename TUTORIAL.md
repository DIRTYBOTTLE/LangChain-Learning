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
| 6 | 输出解析 Output Parser | ✅ 已完成 |
| 7 | 对话记忆 Memory | ✅ 已完成 |
| 8 | 工具调用与 Agent | ✅ 已完成 |
| 9 | RAG 检索增强问答（可选） | ✅ 已完成 |
| 10 | 流式输出 Streaming | ✅ 已完成 |
| 11 | 持久化向量库 | ✅ 已完成 |
| 12 | 整合成一个小应用 | ✅ 已完成 |
| 13 | LangGraph 基础概念 | ✅ 已完成 |
| 14 | LangGraph 条件边 | ✅ 已完成 |
| 15 | LangGraph 接入 LLM 节点 | ✅ 已完成 |
| 16 | LangGraph 手写工具调用循环 | ✅ 已完成 |
| 17 | LangGraph Checkpointer 持久化对话 | ✅ 已完成 |
| 18 | LangGraph Human-in-the-loop 人工介入 | ✅ 已完成 |
| 19 | LangGraph SQLite Checkpointer 持久化会话 | ✅ 已完成 |

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

---

## 第 6 步:输出解析 Output Parser

### 做了什么

到目前为止，`chain.invoke(...)` 拿到的都是一个 `AIMessage` 对象，要用 `.content` 才能取出文本。新增 `06_output_parser.py`，演示两种更进一步的输出解析方式。

**1）`StrOutputParser`：接到纯字符串**

```python
str_chain = prompt | llm | StrOutputParser()
result = str_chain.invoke({"language": "英文", "text": "今天天气真好，我们去公园散步吧。"})
```

在链的末尾再接一个 `StrOutputParser()`，`chain.invoke(...)` 的返回值就直接是字符串本身，不再是 `AIMessage` 对象，也就不用再手写 `.content` 了。运行结果：

```
True The weather is lovely today. Let's go for a walk in the park.
```

（`True` 是 `isinstance(result, str)` 的结果，用来证明返回值就是一个普通字符串。）

**2）结构化输出：直接拿到一个 Python 对象**

有时候我们不只是要一段文本，而是要模型返回“翻译结果 + 识别出的原文语言”这种带多个字段的结构化数据。用 `pydantic.BaseModel` 描述期望的字段，交给 `llm.with_structured_output(...)`：

```python
class Translation(BaseModel):
    translated_text: str = Field(description="翻译后的文本")
    source_language: str = Field(description="识别出的原文语言，例如：中文")


structured_llm = llm.with_structured_output(Translation, method="function_calling")
structured_chain = prompt | structured_llm
structured_result = structured_chain.invoke({"language": "英文", "text": "今天天气真好，我们去公园散步吧。"})
```

运行结果：

```
<class '__main__.Translation'> translated_text="The weather is so nice today. Let's go for a walk in the park." source_language='中文'
```

`structured_result` 已经是一个 `Translation` 实例，可以直接用 `structured_result.translated_text`、`structured_result.source_language` 访问字段，不需要自己写正则或者手动解析 JSON。

> **踩坑记录**：`with_structured_output` 默认会尝试用最新的 `response_format`（JSON Schema）方式让模型返回结构化数据，但 DeepSeek 当前的 API 还不支持这种方式，会报错 `This response_format type is unavailable now`。解决办法是显式传 `method="function_calling"`，改用“函数调用”的方式实现结构化输出——这是一种更通用、几乎所有支持 tool calling 的模型都兼容的方式。

### 为什么这样做

- **`StrOutputParser` 的意义**：当下游只关心文本内容（比如要把结果存进数据库、展示在页面上）时，链的调用方不需要知道也不用关心 `AIMessage` 的存在，直接拿字符串最省心。这也是为什么它常被放在生产环境链路的最后一环。
- **结构化输出的意义**：如果程序要根据模型的返回结果做进一步逻辑判断（比如 `if source_language == "中文"`），解析裸文本 / JSON 字符串既啰嗦又脆弱（模型偶尔可能多输出几个字、格式对不齐）。`with_structured_output` 把“保证返回格式正确”这件事交给了 LangChain 和模型的 function calling 能力去做，程序里直接用属性访问，健壮性更好。
- 两种方式本质上都是在 `prompt | llm` 这条链的末端多接一环——`StrOutputParser()` 是接在 `llm` 后面的独立组件，而 `with_structured_output` 是直接对 `llm` 这个对象做了包装（返回一个新的、行为不同的可运行对象），两种思路后面在 Agent、RAG 里都会反复用到。

---

## 第 7 步：对话记忆 Memory

### 做了什么

前面几步每次 `invoke` 都是独立的一轮问答，模型不知道上一轮聊了什么——因为压根没把上一轮的内容发给它。LLM 本身是无状态的，所谓“记忆”，其实就是**把之前的对话历史，跟着这一轮的问题一起再发一遍**。

新增 `07_memory.py`：

```python
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个友好的助手，会记住之前聊过的内容。"),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
    ]
)

chain = prompt | llm

history = []


def chat(user_input):
    response = chain.invoke({"history": history, "input": user_input})
    history.append(HumanMessage(content=user_input))
    history.append(response)
    print(f"用户: {user_input}")
    print(f"助手: {response.content}\n")


chat("我叫小明，最喜欢的水果是芒果。")
chat("你还记得我的名字和喜欢的水果吗？")
```

运行结果：

```
用户: 我叫小明，最喜欢的水果是芒果。
助手: 你好小明！很高兴认识你，我记得你最喜欢的水果是芒果啦！...

用户: 你还记得我的名字和喜欢的水果吗？
助手: 当然记得呀！你叫小明，最喜欢的水果是芒果...
```

关键的两处：

- `MessagesPlaceholder("history")`：在模板骨架里挖了一个“坑”，专门用来插入一整段消息列表（而不是像 `{text}` 那样只能填一个字符串）。调用时传入 `history=history`，这个列表里有多少条消息，就会原样插入多少条。
- `history` 是一个普通的 Python 列表，由**我们自己**在每次调用后维护：先调用 `chain.invoke(...)` 拿到回复，再手动把这一轮的 `HumanMessage` 和模型返回的 `AIMessage` 都追加进 `history`，下一轮调用时它们就会被当成“上下文”一起发给模型。

### 为什么这样做

- **LLM 没有记忆，“记忆”是应用层的责任**：这是理解所有对话式 AI 应用的关键前提。无论是 ChatGPT 网页版的多轮对话，还是这里的例子，本质上都是客户端/服务端把历史消息缓存下来，每次请求时完整或裁剪后再发一遍。理解了这一点，就能理解为什么对话越长、每次请求消耗的 token 越多——历史都要重新发送。
- **先手写 `history` 列表，而不是直接用 LangChain 提供的 `RunnableWithMessageHistory` 封装**：是想先把“记忆”背后最原始的机制搞清楚（无非就是一个消息列表 + 每轮追加）。等这个机制理解了，官方封装的 `RunnableWithMessageHistory`（可以按 `session_id` 自动管理多个用户各自的历史，并支持接入 Redis 等持久化存储）只是把“手动维护 `history` 列表”这件事自动化了，不会再显得神秘。
- 这里用最简单的“全量历史都发给模型”策略。真实项目里，历史一长会超出模型的上下文长度限制、也会增加成本，通常还需要做**历史裁剪/摘要**（比如只保留最近 N 轮，或者定期把旧对话总结成一段摘要），这个优化点先了解，之后有需要可以再深入。

---

## 第 8 步：工具调用与 Agent

### 做了什么

到目前为止，模型只能凭“记忆里的知识”回答问题，答不了实时信息（今天天气、当前时间），也做不了精确计算（大语言模型本质是在“猜”下一个字，算数经常不准）。**工具调用（Tool Calling）**让模型可以说“这个我不会，帮我调用一下某个函数，把结果告诉我”，由我们的代码去真正执行这个函数。

新增 `08_tools_and_agent.py`，分两部分。

**1）先定义两个工具：**

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """查询指定城市当前的天气情况。"""
    fake_weather_db = {"北京": "晴，25°C", "上海": "多云，28°C"}
    return fake_weather_db.get(city, f"暂无 {city} 的天气数据")


@tool
def add(a: float, b: float) -> float:
    """计算两个数字相加的结果。"""
    return a + b
```

`@tool` 装饰器把一个普通 Python 函数包装成 LangChain 认识的“工具”对象。这里的**函数签名**（参数名、类型）和**函数的 docstring**都不是随便写的：它们会被自动转换成一份工具说明书（名字、参数、用途描述）发给模型，模型正是靠读这份说明书来判断“这个问题该不该用工具、该用哪个、参数怎么填”。`get_weather` 用的是写死的假数据，重点是演示机制，不是真的接天气 API。

**2）手动实现一遍“工具调用循环”，看清背后的机制：**

```python
llm_with_tools = llm.bind_tools(tools)

messages = [HumanMessage(content="北京今天天气怎么样？")]
ai_message = llm_with_tools.invoke(messages)
print("模型决定调用的工具：", ai_message.tool_calls)

messages.append(ai_message)
for tool_call in ai_message.tool_calls:
    selected_tool = tools_by_name[tool_call["name"]]
    tool_message = selected_tool.invoke(tool_call)
    messages.append(tool_message)

final_response = llm_with_tools.invoke(messages)
print("最终回答：", final_response.content)
```

运行结果：

```
模型决定调用的工具： [{'name': 'get_weather', 'args': {'city': '北京'}, 'id': '...', 'type': 'tool_call'}]
最终回答： 北京今天天气**晴**，气温 **25°C**...
```

这一步的关键在于，**模型本身不会“执行”任何工具**，它只是在第一次 `invoke` 时返回了一个特殊的 `AIMessage`，其中 `tool_calls` 字段写着“我想调用 `get_weather`，参数是 `city=北京`”。真正调用 `get_weather` 这个函数、拿到 `"晴，25°C"` 这个字符串的，是我们自己写的这几行 `for` 循环代码。拿到结果后，把它包装成一条 `ToolMessage` 追加进 `messages`，再把完整的对话历史（问题 + 模型的调用请求 + 工具的执行结果）第二次发给模型，模型才基于这个结果生成了最终的自然语言回答。

**3）用官方 `create_agent` 封装同一个能力：**

```python
from langchain.agents import create_agent

agent = create_agent(llm, tools=tools)
result = agent.invoke({"messages": [HumanMessage(content="上海天气怎么样？另外，3.5 加 2.7 等于多少？")]})
```

运行结果（`m.pretty_print()` 把每条消息按类型打印出来）：

```
================================ Human Message =================================
上海天气怎么样？另外，3.5 加 2.7 等于多少？
================================== Ai Message ==================================
好的，我来同时查询这两个信息。
Tool Calls:
  get_weather(city: 上海)
  add(a: 3.5, b: 2.7)
================================= Tool Message =================================
Name: get_weather
多云，28°C
================================= Tool Message =================================
Name: add
6.2
================================== Ai Message ==================================
为你查询到以下信息：
1. **上海天气**：目前是多云，气温 **28°C**。
2. **3.5 + 2.7**：等于 **6.2**。
```

`create_agent` 把第 2 部分里手写的“调用模型 → 检查有没有工具调用请求 → 执行工具 → 把结果发回去 → 再调用模型”这一整套循环封装好了，还自动支持了**一次并行调用多个工具**（这次模型一口气决定同时查天气和算加法，我们手写的简化版循环里没有处理并行的情况）。

### 为什么这样做

- **先手动实现一遍再用封装**：和第 7 步的思路一致。工具调用最容易让初学者困惑的地方，就是误以为“模型自己执行了函数”。手写一遍循环之后就会清楚：工具调用的本质仍然是消息的来回传递（一个特殊格式的 `AIMessage` → 我们执行代码 → 一个 `ToolMessage`），模型自己不具备执行任何代码的能力。
- **为什么工具函数要写清楚 docstring 和类型注解**：这是模型判断“该不该调用、调用哪个、参数怎么填”的唯一依据。如果 docstring 写得模糊，模型很可能选错工具或者编造参数，这是实际项目里工具调用出错的最常见原因之一。
- **`create_agent` 什么时候该用**：当工具不止一两个、可能需要连续调用好几轮（比如先查天气，再根据天气结果决定要不要调用另一个工具）时，手写循环会变得繁琐且容易漏掉边界情况（比如这里演示的并行工具调用）。`create_agent` 基于 LangGraph 实现，是 LangChain 1.x 里官方推荐的 Agent 构建方式。

---

## 第 9 步：RAG 检索增强问答（可选）

### 为什么需要 RAG

模型的知识来自训练数据，天然不知道两类内容：**训练截止日期之后发生的事**，以及**从未公开、只存在于你自己文档里的私有信息**（比如公司内部制度、某个项目的技术文档）。让模型“见到”这些信息，通常有两种思路：微调（重新训练模型，成本高、更新麻烦）或者 **RAG（Retrieval-Augmented Generation，检索增强生成）**——每次提问时，先从自己的文档库里找出和问题相关的片段，把这些片段作为“已知资料”一起塞进 prompt，让模型只根据这些资料来回答。RAG 的好处是文档随时能改、不用重新训练，成本也低得多。

### 做了什么

新增 `data/company_faq.txt`——一份**虚构**的公司制度问答（星尘科技的年假、报销、远程办公政策），确保 DeepSeek 不可能在训练数据里见过这些内容，这样如果它答对了，就能证明确实是靠检索到的资料回答的，而不是凭自己的知识瞎猜。

新增 `09_rag.py`，完整走了一遍 RAG 的标准流程：

**1）加载 + 切分文档**

```python
with open("data/company_faq.txt", encoding="utf-8") as f:
    raw_text = f.read()

splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
chunks = splitter.split_text(raw_text)
```

一篇长文档不会整个塞给检索系统，而是先切成一个个小段（这里按大约 100 个字符切一段，相邻两段之间保留 20 个字符的重叠，避免一句完整的话恰好被切分点切断，导致两边都读不出完整语义）。运行后可以看到原文被切成了 4 段，正好对应文档里的 4 段政策说明。

**2）向量化，存进向量库**

```python
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
vector_store = InMemoryVectorStore.from_texts(chunks, embeddings)
```

- `HuggingFaceEmbeddings`：调用一个本地运行的 Embedding 模型，把每一段文字变成一个高维向量（可以理解成用一串数字表示这段话的“语义位置”，语义相近的句子，向量在空间里的距离也相近）。这里选的 `BAAI/bge-small-zh-v1.5` 是一个专门针对中文优化、体积小（约 100MB 出头）、免费开源的模型，首次运行时会自动从 HuggingFace 下载到本地缓存，之后就能离线使用，不需要任何 API Key。
- `InMemoryVectorStore`：LangChain 内置的向量库，把每段文字的向量存在内存里，支持“给一个新向量，找出库里最相似的几个”。这里没有用 FAISS 或 Chroma 这类更专业的向量数据库，因为 `InMemoryVectorStore` 不需要额外安装任何依赖，最适合用来先理解概念；等文档量大到内存放不下、或者需要持久化保存时，再换成生产级的向量数据库，用法（`similarity_search` 等接口）基本是一致的。

**3）检索**

```python
question = "星尘科技的年假政策是怎样的？"
retrieved_docs = vector_store.similarity_search(question, k=2)
```

把问题也用同一个 Embedding 模型转成向量，去向量库里找语义最相似的 `k=2` 段原文。运行结果显示，最相关的一段正是“年假政策”那一段，第二相关的是“远程办公政策”——检索结果不一定 100% 精准，这也是为什么通常会多检索几段（而不是只取最相似的 1 段）给模型兜底。

**4）把检索结果塞进 prompt，让模型基于资料回答**

```python
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是公司内部助手，只根据下面提供的资料回答问题，资料中没有的内容就明确说不知道，不要编造。\n\n资料：\n{context}"),
        ("human", "{question}"),
    ]
)

context = "\n".join(doc.page_content for doc in retrieved_docs)
chain = prompt | llm
response = chain.invoke({"context": context, "question": question})
```

运行结果：

```
根据公司资料，星尘科技有限公司的年假政策是：入职满一年的员工每年享有 10 天带薪年假，年假可跨年结转，但最多结转 3 天，超出部分自动清零。
```

模型准确回答出了这段虚构政策的细节，证明这个答案确实来自我们提供的资料，而不是模型本身的知识——这就是 RAG 最核心的效果验证方式。

### 为什么这样做

- **切分参数 `chunk_size`/`chunk_overlap` 怎么选**：这里为了演示效果用了很小的值（100/20），实际项目里通常从几百到一千字符起步，具体取决于文档类型（代码、新闻、书籍的合适切法都不同）和所用 Embedding 模型的最佳输入长度，没有一个放之四海而皆准的数字，一般需要跑几组实验对比检索效果。
- **用虚构数据而不是真实公开信息来测试**：如果问一个模型本来就知道的问题（比如“中国的首都是哪里”），就算 RAG 流程完全没接上、检索结果是错的，模型也可能凭自己的知识蒙对，看不出 RAG 到底有没有真正生效。用一份模型不可能见过的虚构资料，是验证 RAG 链路是否真正工作的一个简单可靠的办法。
- **本地 Embedding 模型 vs. 调用云端 Embedding API**：本地模型免费、无需网络、没有调用频率限制，缺点是首次要下载模型、且推理速度和效果通常不如商业化的大模型 Embedding API；后者（比如阿里云 DashScope、OpenAI 的 embedding 模型）效果可能更好，但需要额外的 API Key 和调用成本。选哪个是工程权衡，教学阶段优先选免费无门槛的方案。
- 这一步只覆盖了 RAG 最核心的链路（加载 → 切分 → 向量化 → 检索 → 生成）。真实的 RAG 系统往往还会做：检索结果的重排序（rerank）、多路召回（关键词 + 向量混合检索）、给向量库做持久化存储、处理 PDF/网页等更复杂的文档格式——这些都是在这个核心链路基础上的进一步优化，理解了这里的主干流程，之后按需扩展即可。

---

## 第 10 步：流式输出 Streaming

### 做了什么

前面所有例子用的都是 `invoke()`：发送请求后，程序会一直等着，直到模型把**完整的回答**都生成完了，才拿到结果、一次性打印出来。如果让模型写一段比较长的内容，用户会盯着一个空白的屏幕等好几秒，体验并不好——而我们平时用的 ChatGPT、DeepSeek 网页版，文字都是一个字一个字蹦出来的，这就是**流式输出（Streaming）**。

新增 `10_streaming.py`，展示了两种粒度的流式调用。

**1）最基础的 `llm.stream()`：**

```python
for chunk in llm.stream("用 100 字左右描述一下秋天的景色。"):
    print(chunk.content, end="", flush=True)
```

`llm.stream(...)` 不再是一次性返回一个完整的 `AIMessage`，而是返回一个**可迭代对象**：模型每生成一小段文字（一个 token 或几个 token），就会立刻产出一个 `chunk`（类型是 `AIMessageChunk`），程序这边用 `for` 循环边收边打印。`print(..., end="", flush=True)` 里的 `end=""` 是不换行、紧接着上一段继续打印，`flush=True` 是让每次打印立刻显示在终端上，而不是攒够一批再统一刷新——这样才能看到文字连续蹦出来的效果。运行结果是一段完整的秋天景色描写，只是显示的过程是一点点出现的，而不是一次性蹦出来。

**2）整条 LCEL 链也能流式输出：**

```python
chain = prompt | llm | StrOutputParser()
for chunk in chain.stream({"language": "英文", "text": "秋天到了，树叶渐渐变黄，风也凉了。"}):
    print(chunk, end="", flush=True)
```

即使链的末尾接了 `StrOutputParser()`，`chain.stream(...)` 依然是流式的，只是这次每个 `chunk` 直接就是一小段字符串（`StrOutputParser` 把每个 `AIMessageChunk` 实时转换成了对应的文本片段），不需要再手动取 `.content`。这说明**只要链条上的每一环都支持流式处理，`|` 拼起来的整条链就依然是流式的**，不需要对 `prompt`、`StrOutputParser` 做任何额外改动。

### 为什么这样做

- **用户体验**：等待时间不变的情况下，让内容尽快开始展示，用户会感觉“响应更快”——这是所有对话式产品都做流式输出的根本原因，尤其是回答比较长的时候（比如这一步的例子），一次性等待和边生成边看的体验差异非常明显。
- **`invoke()` 和 `stream()` 该怎么选**：如果程序需要拿到完整结果做进一步处理（比如上一步 RAG 里，要先判断检索结果是否为空、要把 `AIMessage.content` 交给下一个函数处理结构化数据），那就适合用 `invoke()`；如果结果是直接展示给终端用户看的（网页聊天界面、命令行工具的最终回答），用 `stream()` 几乎总是体验更好、没有额外代价。
- **`create_agent` 的流式输出是另一回事**：第 8 步的 Agent 因为背后是一个“调用模型 → 判断要不要调用工具 → 执行工具 → 再调用模型”的多步骤循环（用 LangGraph 实现），它的 `.stream(...)` 默认按“每完成一个步骤就产出一次结果”来流式输出，而不是像这里一样按 token 级别流式输出文字。如果想要 Agent 在生成最终自然语言回答时也做到逐字流式，需要用它更细粒度的流式模式（`stream_mode="messages"`），这个留到之后有实际需要时再深入，这里先了解“流式”在“单次模型调用”和“多步骤 Agent”里是两个不同层面的概念即可。

---

## 第 11 步：持久化向量库

### 做了什么

第 9 步里，每次运行 `09_rag.py`，程序都会重新执行一遍“读文档 → 切分 → 把每一段都丢给 embedding 模型算一遍向量”，`InMemoryVectorStore` 里的数据只存在这一次进程的内存里，程序一退出就没了。文档只有 4 段的时候这不是问题，但如果是几千段的真实文档库，每次启动程序都重新计算一遍所有向量，既慢又浪费。

新增 `11_persistent_vector_store.py`，用 `InMemoryVectorStore` 自带的 `dump()` / `load()` 方法把向量库存到磁盘上：

```python
SOURCE_PATH = "data/company_faq.txt"
STORE_PATH = "vector_store.json"
HASH_PATH = "vector_store.hash"

embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")

with open(SOURCE_PATH, encoding="utf-8") as f:
    raw_text = f.read()
current_hash = hashlib.md5(raw_text.encode("utf-8")).hexdigest()

cached_hash = None
if os.path.exists(HASH_PATH):
    with open(HASH_PATH, encoding="utf-8") as f:
        cached_hash = f.read().strip()

if os.path.exists(STORE_PATH) and cached_hash == current_hash:
    print(f"源文档未变化，直接加载 {STORE_PATH}，不重新计算 embedding")
    vector_store = InMemoryVectorStore.load(STORE_PATH, embeddings)
else:
    print("源文档是新的或已发生变化，重新构建向量库")
    # ... 切分、from_texts() 构建 vector_store（和第 9 步一样）
    vector_store.dump(STORE_PATH)
    with open(HASH_PATH, "w", encoding="utf-8") as f:
        f.write(current_hash)
```

> **第一版少了什么**：最初的实现只判断了“`vector_store.json` 存不存在”——只要文件存在就直接加载，完全没检查 `data/company_faq.txt` 有没有被改过。这样一旦源文档更新了，程序会一直读到过时的向量库，检索出旧内容而不自知，是一个真实的正确性问题。修复方式是给源文档内容算一个 `md5` 哈希，和上次构建时保存的哈希（`vector_store.hash`）比较：只有“向量库文件存在”**并且**“哈希对得上”这两个条件都满足，才走加载分支；哈希对不上（文档变了）或者压根没建过，都会重新构建并把新的哈希存下来。

实测了三种场景，结果都符合预期：

1. **首次运行**（没有 `vector_store.json`/`vector_store.hash`）：重新构建并保存。
2. **文档没变，再次运行**：哈希一致，直接加载，跳过重新计算向量。
3. **手动往 `data/company_faq.txt` 里加一条新政策后运行**：哈希对不上，自动重新构建——检索结果里能看到新内容已经生效（验证完之后把这条测试内容还原了，保持和第 9 步文档描述的 4 段内容一致）。

### 为什么这样做

- **省下的是“给文档算向量”这一步，不是“加载 embedding 模型”这一步**：每次运行你都会看到 `Loading weights...` 的进度条，这是在把 `BAAI/bge-small-zh-v1.5` 这个模型加载进内存——因为不管有没有历史数据，用户新提的问题总是要重新转成向量才能去库里检索。真正被跳过的，是对 `data/company_faq.txt` 里那几段文字重新计算向量的过程；文档越多、越大，这部分省下的时间也越多。
- **为什么用内容哈希而不是文件修改时间（mtime）判断“变没变”**：mtime 容易被“无意义的改动”骗到（比如只是把文件复制到另一台机器、或者 `touch` 了一下但内容没变），也可能因为系统时钟、时区问题不可靠；直接对内容算哈希，只要文字内容一个字节都没变，哈希就不会变，是更严谨、也是缓存失效（cache invalidation）场景里更常见的做法。

---

## 第 12 步：整合成一个小应用

### 做了什么

前面 11 步分别学了 Prompt、Chain、输出解析、记忆、工具调用、Agent、RAG、流式、持久化——每个概念都单独拿一个小例子演示，彼此没有连起来。这一步作为收尾，新增 `12_chatbot_app.py`，把其中三块拼成一个真正能连续对话的命令行应用：一个“公司内部助手”。

**核心思路：把 RAG 检索包装成一个工具，交给 Agent 自己决定什么时候用**

```python
@tool
def search_company_docs(query: str) -> str:
    """在公司规章制度文档中检索和问题相关的内容，用于回答年假、报销、远程办公、试用期等制度类问题。"""
    docs = vector_store.similarity_search(query, k=2)
    return "\n".join(doc.page_content for doc in docs)


agent = create_agent(
    llm,
    tools=[search_company_docs],
    system_prompt="你是公司内部助手。遇到规章制度类问题，先调用 search_company_docs 工具查询资料，再基于查到的资料回答；资料里没有的内容就明确说不知道，不要编造。",
)
```

第 9 步的 RAG 例子里，检索这一步是我们在代码里**写死**的（先手动 `similarity_search`，再手动把结果塞进 prompt）。这里换了个思路：把“检索”本身做成第 8 步学过的那种 `@tool`，模型看到用户问题后，**自己判断**要不要调用这个工具、传什么查询词进去——这样一个助手既能回答规章制度问题（会主动查资料），也能正常闲聊或者回答其他问题（不会硬查一次用不上的资料）。

**多轮对话用的还是第 7 步的思路**，只是这次用 `create_agent` 返回的 `agent.invoke({"messages": messages})`，每轮把返回的完整消息列表（包含这一路的工具调用、工具结果、最终回答）整体赋回 `messages`，下一轮连着一起发给模型：

```python
messages = []
while True:
    user_input = input("你: ")
    if user_input.strip().lower() in {"exit", "quit"}:
        break
    messages.append(HumanMessage(content=user_input))
    result = agent.invoke({"messages": messages})
    messages = result["messages"]
    print(f"助手: {messages[-1].content}\n")
```

实测两轮对话：

```
你: 星尘科技的年假政策是怎样的？
助手: 根据查询到的星尘科技公司规章制度，年假政策如下：
1. 享受条件：入职满一年的员工可享有带薪年假。
2. 年假天数：每年 10 天 带薪年假。
3. 结转规则：年假可跨年结转，但最多结转 3 天，超出部分将自动清零。
...

你: 我刚才问的是关于哪方面的问题？
助手: 你刚才问的是关于星尘科技的年假政策，具体包括入职满一年员工可享有的年假天数（10天）以及年假跨年结转的规则（最多结转3天，超出部分清零）。
```

第二轮问题里没提“年假”两个字，模型依然准确回忆起了上一轮聊的话题——证明工具调用（第一轮准确查到并引用了年假政策原文）和多轮记忆（第二轮记住了上一轮内容）在同一个应用里同时生效了。

另外，脚本里直接复用了第 11 步的“加载或重建向量库”逻辑（`load_or_build_vector_store()` 函数），所以这个脚本可以独立运行，不要求你必须先手动跑一遍 `11_persistent_vector_store.py`。

### 为什么这样做

- **把 RAG 做成工具，而不是硬编码在每次请求里**：如果每次提问都无条件先做一次向量检索、再把结果塞进 prompt，遇到“你好”“你是谁”这种不需要查资料的问题，也会白白多消耗一次检索和一些无关的上下文。让 Agent 自己判断要不要调用工具，是更贴近真实产品的做法——这也是为什么真实的 RAG 应用，很多时候实际上是“RAG + Agent”的组合，而不是一条写死的检索链。
- **这一步没有引入任何新概念**：所有用到的组件（`@tool`、`create_agent`、消息列表维护的多轮记忆、持久化向量库）在前面的步骤里都单独学过。把它们组合在一起、能不能跑得通、组合后行为符不符合预期，本身就是对前 11 步理解程度的一次检验——如果中间任何一环没搞懂，这一步大概率会在某个地方卡住或者行为不符合预期。
- **脚本复用第 11 步的加载/构建函数，而不是要求先跑另一个脚本**：延续了这个仓库“每个脚本独立可运行”的约定（见 `CLAUDE.md`），代价是这个函数在两个文件里各写了一份、有一点重复；对于教学项目，这种重复是有意为之的取舍——比起为了不重复代码去抽出一个共享模块、让读者还要理解“文件之间怎么互相导入”，保持每个文件可以独立复制运行更符合这个仓库的教学目标。

---

# LangGraph 篇

前面 12 步用的都是 LCEL（`prompt | llm | parser` 这种用 `|` 拼起来的链）。LCEL 很适合“一条直线走到底”的流程，但如果流程本身需要**循环**（比如 Agent 反复调用工具直到任务完成）、**分支**（根据上一步的结果决定走哪条路）、或者需要**中途暂停等人工确认**，用 `|` 拼接就会变得很别扭。实际上第 8 步的 `create_agent`、包括这个项目里所有用到 Agent 的地方，底层都是用 **LangGraph** 实现的——这一篇就是要打开这个“底层”，搞清楚 `create_agent` 到底是怎么用 LangGraph 拼出来的。

## 第 13 步：LangGraph 基础概念

### 做了什么

LangGraph 把“程序的执行流程”建模成一张**图（Graph）**：图上的每个**节点（Node）**是一个处理步骤，节点之间用**边（Edge）**连接表示“做完这一步之后去做哪一步”，整张图共享同一份**状态（State）**，每个节点读取状态、做一些处理，再把更新写回状态。

为了先把这三个概念（State / Node / Edge）单独搞清楚，新增的 `13_langgraph_basics.py` **完全没有用到任何 LLM**，只是一个把数字做两次运算的最小示例：

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    count: int


def add_one(state: State) -> State:
    return {"count": state["count"] + 1}


def double(state: State) -> State:
    return {"count": state["count"] * 2}


graph_builder = StateGraph(State)
graph_builder.add_node("add_one", add_one)
graph_builder.add_node("double", double)
graph_builder.add_edge(START, "add_one")
graph_builder.add_edge("add_one", "double")
graph_builder.add_edge("double", END)

graph = graph_builder.compile()

result = graph.invoke({"count": 1})
print("最终结果：", result)
```

逐行拆解：

- **`State`**：一个 `TypedDict`，描述了在图上流动的数据长什么样——这里只有一个字段 `count`。State 相当于 LCEL 里“上一环的输出格式必须是下一环认识的输入格式”这件事的显式声明：图上所有节点共享同一个 State 类型。
- **节点（`add_one`、`double`）**：就是普通的 Python 函数，接收当前的 `state`，返回一个**要更新到 state 里的字典**（不需要返回完整的 state，只需要返回你想更新的那部分字段）。
- **`StateGraph(State)`**：创建一个“图构建器”，告诉它这张图上流动的数据类型是 `State`。
- **`add_node("add_one", add_one)`**：把函数 `add_one` 注册成图里一个叫 `"add_one"` 的节点（节点名字和函数变量名一致只是习惯，实际是两个独立的东西：一个是字符串标识符，一个是要执行的函数）。
- **`add_edge(...)`**：定义节点之间的执行顺序。`START` 和 `END` 是 LangGraph 内置的两个特殊“节点”，分别代表“图的入口”和“图的出口”。这里连出了一条直线：`START → add_one → double → END`。
- **`graph_builder.compile()`**：把搭好的图“编译”成一个可以真正运行的对象。编译后的 `graph` 和 LCEL 里的 `chain` 一样，也实现了 `invoke()`/`stream()` 这套统一接口——这不是巧合，图和链在 LangChain 的体系里都被当成同一种“可运行对象”。

运行 `graph.invoke({"count": 1})`，`count` 从 `1` 先被 `add_one` 变成 `2`，再被 `double` 变成 `4`，最终结果是 `{'count': 4}`。脚本里还打印了 `graph.get_graph().draw_ascii()`（需要额外装一个很轻量的 `grandalf` 包）画出的图结构：

```
+-----------+
| __start__ |
+-----------+
      *
 +---------+
 | add_one |
 +---------+
      *
  +--------+
  | double |
  +--------+
      *
 +---------+
 | __end__ |
 +---------+
```

> **踩坑记录**：一开始 `requirements.txt` 里没有单独列 `langgraph`，代码却能正常 `import langgraph`——因为 `langchain`（准确说是 `langchain.agents.create_agent` 这些功能）本身就依赖 `langgraph`，装 `langchain` 的时候把它顺带装上了。但“能跑”不代表“这么写是对的”：我们的代码里直接 `import langgraph`，就应该在 `requirements.txt` 里把它列为**直接依赖**并锁定版本，而不是依赖“正好被另一个包顺带装上”这种偶然性。如果以后 `langchain` 调整了自己的依赖关系（比如换了个更低的 `langgraph` 版本要求，或者把 agent 功能拆到了另一个包），这里的 `import langgraph` 可能会在没有任何警告的情况下突然出问题。修复方式很简单：把 `langgraph==1.2.9` 显式加进 `requirements.txt`。这也是判断“一个包该不该写进 requirements.txt”的通用标准——**只要代码里直接 `import` 了它，就应该显式声明**，不管它是不是恰好已经被别的依赖带进来了。

### 为什么这样做

- **先脱离 LLM 学 LangGraph**：这是这个仓库一贯的教学策略——每次只引入一个新概念。前面 12 步已经很熟悉“怎么调用 LLM”了，这一步的重点是搞懂 LangGraph 这套新的编排方式本身（State/Node/Edge/compile），如果例子里同时还带着 LLM 调用、Prompt 模板，反而会分散注意力，分不清哪部分是 LangGraph 独有的新东西。
- **为什么明明前面 12 步的 LCEL 已经能用了，还要学一套新的**：LCEL 的 `|` 本质上是“单向直线流水线”，`a | b | c` 里 `a` 只能流向 `b`。但 Agent 场景天然需要“循环”（调用工具后要回到模型再判断一次“还要不要继续调用工具”）和“分支”（不同情况走不同节点）——这些用纯 `|` 语法很难表达清楚，而图结构天然支持“任意两个节点之间连边”，包括从后面的节点连回前面的节点（形成循环）。下一步讲条件边、之后手写 Agent 循环时，会直接用到这个特性。
- **节点函数只返回“要更新的字段”而不是完整 State**：这是 LangGraph 默认的合并（reducer）行为——新返回的字典会和已有 state 做合并更新，而不是整个替换掉。等后面遇到需要“累加”而不是“覆盖”的字段（比如对话历史消息列表，新消息应该追加而不是覆盖掉旧消息），会看到 State 定义里可以给字段指定不同的合并方式，这里先了解默认行为是“覆盖同名字段”即可。

## 第 14 步：LangGraph 条件边

### 做了什么

上一步的图是一条直线：`START → add_one → double → END`，不管输入是什么，走的路径都一样。真实场景里经常需要“根据当前状态决定下一步去哪”——这就是**条件边（Conditional Edge）**。

新增 `14_langgraph_conditional_edges.py`，在上一步的基础上做了个小改动：只保留一个 `double` 节点，让它反复执行，直到 `count` 达到 100 才停下来：

```python
def double(state: State) -> State:
    print(f"double 执行前：{state['count']}")
    return {"count": state["count"] * 2}


def should_continue(state: State) -> str:
    if state["count"] < 100:
        return "double"
    return END


graph_builder = StateGraph(State)
graph_builder.add_node("double", double)
graph_builder.add_edge(START, "double")
graph_builder.add_conditional_edges("double", should_continue, {"double": "double", END: END})

graph = graph_builder.compile()
result = graph.invoke({"count": 1})
```

关键的一行是 `add_conditional_edges("double", should_continue, {...})`：

- 第一个参数 `"double"`：从哪个节点出发判断。
- 第二个参数 `should_continue`：一个“判断函数”，接收当前 state，返回一个字符串，代表接下来要去哪个节点。
- 第三个参数 `{"double": "double", END: END}`：一份“路由表”，把 `should_continue` 可能返回的每个字符串，映射到真正的目标节点——这里 `should_continue` 返回 `"double"` 时就映射回 `"double"` 节点本身（也就是自己指向自己，形成一个循环），返回 `END` 时就映射到图的出口。

运行结果：

```
double 执行前：1
double 执行前：2
double 执行前：4
double 执行前：8
double 执行前：16
double 执行前：32
double 执行前：64
最终结果： {'count': 128}
```

`count` 从 1 开始不断翻倍，每次执行完 `double` 都会调用 `should_continue` 检查一遍：小于 100 就再跑一次 `double`，直到变成 128（第一次 ≥ 100）才停下来去到 `END`。

> **踩坑记录**：一开始想顺便打印 `graph.get_graph().draw_ascii()` 看看这张图长什么样，结果 `grandalf`（上一步用来画图的库）在处理这种“节点指向自己”的自循环边时直接报错崩溃了（`ValueError: no intersection found`）。这不是我们代码写错了，是这个纯文本画图工具本身处理不了自循环这种拓扑结构，所以这一步就不追求把图画出来了——工具的能力边界也是需要在实践中发现的，遇到不支持的场景，绕开就好，不用纠结。

### 为什么这样做

- **条件边是 LangGraph 用来表达“分支”和“循环”的核心机制**：一个从 `should_continue` 出发的判断函数 + 一份路由表，既可以实现“根据情况走不同分支”（比如这里的“继续 vs 结束”），也可以实现“反复执行直到满足某个条件”（把某个分支指回自己）。第 8 步 `create_agent` 背后真正的循环逻辑——“调用模型 → 有没有工具调用请求？有就执行工具再回到模型；没有就结束”——本质上就是一个比这里复杂一点的条件边判断，下下一步手写 Agent 循环时会直接用到一模一样的机制。
- **为什么先用一个和 LLM 无关的计数器例子，而不是直接就手写 Agent 循环**：条件边本身的语法（判断函数返回什么字符串、路由表怎么写）和“循环判断的具体业务逻辑是什么”是两件独立的事。先在一个只有一两行逻辑、结果可以一眼验证对不对的例子里把语法吃透（“1 翻倍到 128 停下”，一眼就能验证对不对），再去看“判断要不要继续调用工具”这种更复杂的业务逻辑，会更容易分清楚哪部分是 LangGraph 的固定写法、哪部分是我们自己要写的业务判断。

## 第 15 步：LangGraph 接入 LLM 节点

### 做了什么

前两步的节点都是普通的数字运算，这一步让节点里真正调用一次 LLM。新增 `15_langgraph_llm_node.py`：

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State) -> State:
    return {"messages": [llm.invoke(state["messages"])]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()
```

这里的 State 定义呼应了第 13 步留下的伏笔：

```python
messages: Annotated[list, add_messages]
```

`Annotated[list, add_messages]` 的意思是：`messages` 这个字段是一个列表，并且当节点返回新的 `messages` 时，不要像第 13 步那样“覆盖”掉旧值，而是用 `add_messages` 这个 LangGraph 内置的合并函数（reducer）来处理——`add_messages` 会把新消息**追加**到旧列表后面（如果新消息和旧消息 id 相同，还会做替换/更新而不是重复追加，这里先不展开）。所以 `chatbot` 节点只需要返回“这一步新产生的那一条 AI 消息”，`{"messages": [llm.invoke(state["messages"])]}`，不用自己操心怎么拼接历史，LangGraph 会处理。

用两轮对话验证了效果：

```python
result = graph.invoke({"messages": [("human", "我叫小明，最喜欢的水果是芒果。")]})
# ... 打印 result["messages"]，此时是 [Human1, AI1] 两条

result = graph.invoke({"messages": result["messages"] + [("human", "你还记得我的名字和喜欢的水果吗？")]})
# ... 打印 result["messages"]，此时是 [Human1, AI1, Human2, AI2] 四条
```

运行结果，第二轮模型准确回答出了名字和水果：

```
Human: 我叫小明，最喜欢的水果是芒果。
Ai: 哈哈，小明你好！芒果真的是超棒的水果呢...

Human: 你还记得我的名字和喜欢的水果吗？
Ai: 当然记得啦！你是小明，最爱吃的是芒果～...
```

### 为什么这样做

- **`add_messages` 解决的正是第 13 步留下的问题**：第 13 步提到过，默认情况下节点返回的字段会“覆盖”掉 state 里的同名字段，但对话历史这种场景，我们想要的是“追加”而不是“覆盖”——`Annotated[list, add_messages]` 就是显式告诉 LangGraph：这个字段用另一套合并规则。这是 LangGraph 里非常常见的写法，`create_agent` 内部维护对话状态用的也是同一个 `add_messages`。
- **为什么每轮手动把 `result["messages"]` 拼接后再传给下一次 `invoke`，而不是让图自己记住**：`graph.invoke(...)` 每次调用都是一次完全独立、无状态的执行——这次调用不知道上次调用发生过什么，图本身不会跨越多次 `invoke()` 自动保留状态。所以要实现多轮对话，必须（和第 7 步手写 `history` 列表的思路完全一致）把上一轮的完整消息列表交给这一轮当作输入的一部分。下一步会介绍 LangGraph 官方的 **Checkpointer**，可以让图自动记住每个对话的历史，不用再手动拼接，但理解“不用它的话本质上要做什么”，能让之后用 Checkpointer 时更清楚它到底帮你省了什么。
- **`("human", "...")` 这种二元组写法**：这是 LangChain 消息的一种简写形式，等价于 `HumanMessage(content="...")`，`add_messages` 在合并时会自动把这种简写转换成正式的消息对象——这也是为什么打印 `result["messages"]` 时看到的是完整的 `HumanMessage`/`AIMessage`，而不是原始传入的元组。

## 第 16 步：LangGraph 手写工具调用循环

### 做了什么

这一步是前面几步的汇合点：把第 8 步手写过的“工具调用循环”，用第 14 步学的条件边、第 15 步学的 LLM 节点，在 LangGraph 里完整重新搭一遍——这也正是 `create_agent` 内部真正在做的事情。

新增 `16_langgraph_tool_loop.py`，工具定义和第 8 步完全一样（`get_weather`、`add`），图搭成这样：

```python
def chatbot(state: State) -> State:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


def tool_executor(state: State) -> State:
    last_message = state["messages"][-1]
    results = [tools_by_name[call["name"]].invoke(call) for call in last_message.tool_calls]
    return {"messages": results}


def should_continue(state: State) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_executor)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", should_continue, {"tools": "tools", END: END})
graph_builder.add_edge("tools", "chatbot")

graph = graph_builder.compile()
```

三个节点/边搭出的执行流程是：

```
START → chatbot → (有工具调用请求？)
                     ├─ 是 → tools → chatbot → (再判断一次)
                     └─ 否 → END
```

- **`chatbot` 节点**：把当前消息历史交给绑定了工具的模型（`llm_with_tools = llm.bind_tools(tools)`），模型这一步要么直接给出最终回答，要么在返回的消息里带上 `tool_calls`（“我想调用哪个工具、参数是什么”）。
- **`tool_executor` 节点**：读取上一条消息（一定是 `chatbot` 刚生成的）里的 `tool_calls`，真正执行对应的工具函数，把每个工具的执行结果包装成 `ToolMessage` 返回——这一步和第 8 步手写的 `for tool_call in ai_message.tool_calls: ...` 循环体几乎一模一样，只是这次是图上的一个节点。
- **`should_continue` 判断函数**：检查最新一条消息有没有 `tool_calls`。有，就说明模型还想调用工具，走向 `"tools"` 节点；没有，说明模型已经给出了不需要再查资料的最终回答，直接走向 `END`。
- **`add_edge("tools", "chatbot")`**：工具执行完，一定要回到 `chatbot`，把工具结果交给模型看一眼、生成下一步的反应（可能是最终回答，也可能是决定再调用一次别的工具）——这一条边，加上 `should_continue` 里“还有 `tool_calls` 就继续走 `tools`”，两者共同构成了一个**循环**：`chatbot ⇄ tools`，直到模型不再请求工具为止。

运行同一个问题（“上海天气怎么样？另外，3.5 加 2.7 等于多少？”），结果和第 8 步的 `create_agent` 一致：模型一次性并行发起了 `get_weather` 和 `add` 两个工具调用，两个 `ToolMessage` 都被塞回历史后，模型才给出汇总了两个结果的最终回答。

### 为什么这样做

- **这就是 `create_agent` 的真面目**：第 8 步用 `create_agent(llm, tools=tools)` 一行代码就拿到的能力，本质上就是这里手写的这几个节点、一条条件边、一条回边组成的图。理解了这张图，`create_agent` 就不再是一个“魔法黑盒”——它只是把这套标准的“模型节点 + 工具节点 + 条件边循环”模式封装成了一个函数调用，让你不用每次都手写一遍。
- **为什么值得先手写一遍，而不是一直用 `create_agent`**：`create_agent` 满足不了的场景（比如想在工具执行前后插入一个自定义的日志/审核节点、想让某些工具调用需要人工确认才能继续执行、想让图在执行到一半时可以暂停和恢复）都需要直接操作这张图。等真的遇到 `create_agent` 参数满足不了的定制需求时，回头看这个例子，就知道该怎么在图里插入自己的节点和边。
- **`tool_executor` 里用列表推导式一次处理所有 `tool_calls`，对应了模型可能“并行调用多个工具”的情况**：和第 8 步手写的 `for` 循环思路一致，只是写得更紧凑；这里也再次印证了 LangGraph 的图结构天然能表达“模型一步产生多个待办事项，一次性并行处理完再继续”这种场景，而不需要额外的特殊语法。

## 第 17 步：LangGraph Checkpointer 持久化对话

### 做了什么

第 15 步为了实现多轮对话，每一轮都要手动把“上一轮返回的完整消息列表”拼接上这一轮的新问题，再一起传给 `graph.invoke()`——本质上和第 7 步手写 `history` 列表是同一件事。LangGraph 提供了一个官方机制叫 **Checkpointer（检查点存储器）**，可以让图自动记住每个对话的历史，不用我们手动拼接。

新增 `17_langgraph_checkpointer.py`，图的结构和第 15 步一模一样（一个 `chatbot` 节点），只是编译的时候多传了一个 `checkpointer`：

```python
from langgraph.checkpoint.memory import InMemorySaver

graph = graph_builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "xiaoming-1"}}

result = graph.invoke({"messages": [("human", "我叫小明，最喜欢的水果是芒果。")]}, config=config)
result = graph.invoke({"messages": [("human", "你还记得我的名字和喜欢的水果吗？")]}, config=config)
```

关键变化：**第二轮 `invoke()` 只传了这一轮的新问题，没有像第 15 步那样手动拼接上一轮的历史**，但模型依然准确回答出了名字和水果。这是因为：

- `InMemorySaver()`：一个把每一步的 state 快照存在内存里的 Checkpointer。图每执行完一步，都会把当前的完整 state（这里就是 `messages` 列表）存一份快照。
- `config = {"configurable": {"thread_id": "xiaoming-1"}}`：调用 `invoke()` 时额外传的 `config` 参数，`thread_id` 就像是这次对话的“房间号”。图在执行前，会先根据这个 `thread_id` 去 Checkpointer 里找“这个房间之前聊到哪了”，把存好的历史 state 取出来，和这一轮新传入的消息合并（还是靠 `add_messages` 这个 reducer），再继续往下执行。

用另一个 `thread_id`（`"someone-else"`）发起新对话，问“你还记得我的名字吗”，模型的回答是：

```
抱歉，我无法记住之前的对话内容，所以不知道您的名字。...
```

证明不同 `thread_id` 之间的历史是完全隔离的，不会串到一起。

### 为什么这样做

- **Checkpointer 帮我们省下的，正是第 7/15 步里手写的“拼接历史”这一步**：不用再自己维护一个 Python 列表、每次调用前手动拼接——只要 `thread_id` 一致，图会自动把这个对话的历史续上。这在有多个用户同时使用同一个应用时尤其重要：每个用户一个独立的 `thread_id`，就能天然地把所有人的对话历史互不干扰地分开管理，不用自己写一套“按用户 ID 存取历史”的逻辑。
- **`InMemorySaver` 和 `InMemoryVectorStore` 面临同样的取舍**：数据存在进程内存里，进程一退出历史就没了，仅适合学习和本地实验。LangGraph 也提供了 `SqliteSaver`、`PostgresSaver` 等持久化到磁盘/数据库的 Checkpointer 实现，接口用法（`compile(checkpointer=...)`、靠 `thread_id` 区分会话）是完全一致的，真到生产环境按需要换掉 `InMemorySaver` 就行，不需要改动图的结构或者业务逻辑代码。
- **走到这一步，第 7 步留下的“手写 `history` 列表”这条线，和第 15 步“每轮手动拼接 `result["messages"]`”这条线，都在这里有了官方的、更省心的替代方案**——但正因为前面几步是手写的，才能一眼看出 Checkpointer 到底帮我们自动做了什么（“按 `thread_id` 存取历史 + 用 `add_messages` 合并”），而不是把它当成一个只知道“能用”却不知道原理的黑盒。

## 第 18 步：Human-in-the-loop 人工介入

### 做了什么

第 16 步手写的工具调用循环里，模型一旦决定要调用某个工具，代码会**立刻**执行它，中间没有任何人插手的机会。真实场景里，有些操作风险较高（比如转账、删除数据、发送对外邮件），我们会希望模型“先说出它想干什么，等人确认了再真正执行”。LangGraph 提供了 `interrupt()` 函数，可以让图在执行到某一行代码时**暂停下来**，把这个节点余下的执行“冻结”，返回控制权给外面的程序；外面的程序问完人类、拿到答案后，再用 `Command(resume=答案)` 把这个节点从暂停的地方**接着**执行下去。

新增 `18_langgraph_human_in_the_loop.py`，在第 16 步的图的基础上，只改了 `tool_executor` 这一个节点：

```python
def tool_executor(state: State) -> State:
    last_message = state["messages"][-1]
    results = []
    for call in last_message.tool_calls:
        approved = interrupt(
            {"question": f"模型想调用工具 {call['name']}，参数 {call['args']}，是否允许？(yes/no)"}
        )
        if approved == "yes":
            output = tools_by_name[call["name"]].invoke(call)
        else:
            output = ToolMessage(content="用户拒绝了这次工具调用。", tool_call_id=call["id"])
        results.append(output)
    return {"messages": results}
```

图编译时必须带上 `checkpointer`（这里还是用第 17 步的 `InMemorySaver`）——`interrupt()` 依赖它来保存“暂停那一刻”的完整状态，不然“恢复执行”就无从谈起。调用方这边的处理逻辑：

```python
result = graph.invoke({"messages": [("human", "北京天气怎么样？")]}, config=config)

while "__interrupt__" in result:
    question = result["__interrupt__"][0].value["question"]
    answer = input(f"[需要人工确认] {question} ")
    result = graph.invoke(Command(resume=answer), config=config)
```

分别测试了“批准”和“拒绝”两种场景：

**输入 `yes`**：

```
[需要人工确认] 模型想调用工具 get_weather，参数 {'city': '北京'}，是否允许？(yes/no)
...
Tool Message
Name: get_weather
晴，25°C
...
Ai Message
北京现在的天气是晴天，气温 25°C...
```

**输入 `no`**：

```
[需要人工确认] 模型想调用工具 get_weather，参数 {'city': '北京'}，是否允许？(yes/no)
...
Tool Message
用户拒绝了这次工具调用。
...
Ai Message
抱歉，我暂时无法获取到北京的天气信息...建议您可以通过以下方式查看北京的天气...
```

两种情况模型都表现得很自然：批准了就正常给出查到的天气；拒绝了模型也没有卡住或报错，而是礼貌地说明拿不到信息、并给出了替代建议。

### 为什么这样做

- **`interrupt()` 暂停的是“节点的执行”，不是“整个程序”**：调用 `graph.invoke(...)` 遇到 `interrupt()` 时会正常返回（不是抛异常卡死），返回结果里带一个 `"__interrupt__"` 键，程序可以用这个键判断“图是主动结束了，还是被暂停了、在等待外部输入”。这种“返回而不是阻塞”的设计，使得它同样适用于 Web 服务这种场景——请求 A 让图暂停后，服务器完全可以先处理别的请求，等用户在页面上点了“确认”按钮，再发一个新请求带着 `Command(resume=...)` 把之前那次执行接着跑完，不需要为了等一个人的操作而占着一个线程死等。
- **为什么必须要有 `checkpointer` 才能用 `interrupt()`**：图“暂停”意味着它的执行状态（这一步之前的所有消息历史、当前在哪个节点、循环执行到第几轮）需要被完整保存下来，等恢复的时候才能从暂停的地方继续，而不是从头再来一遍。这份状态到底存在哪，正是 `checkpointer` 负责的事——`interrupt()` 和 `Checkpointer` 是配套的两个机制，缺一不可。
- **用 `while "__interrupt__" in result` 循环处理，而不是假设只会暂停一次**：这一版例子里，一次提问最多触发一次工具调用、一次确认，但真实场景里模型可能连续调用好几轮不同的工具，每一轮都可能需要确认。写成循环是为了让代码对“暂停零次、一次、还是好几次”都成立，不用针对轮数写死逻辑。
- **这一步走完，从“模型决定做什么”到“真的去执行”之间，多了一道可以插入任意校验逻辑的关卡**——不仅可以是这里演示的“人工 yes/no 确认”，同样的机制也能用来接入更复杂的自动化审核（比如先检查参数是否在允许范围内，只有超出范围的高风险操作才真正弹给人确认），`interrupt()` 提供的是这个“暂停 - 恢复”的底层能力，具体审核逻辑完全由使用者决定。
- **`vector_store.json` 和 `vector_store.hash` 都不提交进 Git**：和 `.venv` 一样，它们都是可以从源头（`data/company_faq.txt` + 相同的 embedding 模型）重新生成出来的**派生产物**，不是需要手工维护的源文件，所以都加进了 `.gitignore`。真正该提交的是 `data/company_faq.txt` 这个原始数据，任何人拿到仓库、跑一次脚本，都能自己生成出一样的向量库和哈希文件。
- **为什么继续用 `InMemoryVectorStore` 而不是直接换成 Chroma/Postgres 等专业的持久化向量数据库**：教学阶段的核心是先理解“持久化”这个概念本身——省去重复计算、数据能跨进程存活。`InMemoryVectorStore.dump()/load()` 用一个 JSON 文件就做到了这一点，不需要再学一个新的数据库系统。等文档量大到一个 JSON 文件不再合适（比如要支持多用户并发读写、要做增量更新），再换成 Chroma、Postgres+pgvector 这类专业方案，那时候 `similarity_search()` 之类的检索代码基本不用改，改的只是vector store 的初始化方式。

---

## 第 19 步：LangGraph SQLite Checkpointer 持久化会话

### 做了什么

第 17 步的 `InMemorySaver` 已经让图能按 `thread_id` 自动续接对话，但它只把快照留在 Python 进程的内存里：脚本一结束，全部历史都会消失。这一步新增 `19_langgraph_sqlite_checkpointer.py`，把同一个图换成 `SqliteSaver`，将 Checkpoint 写入脚本同目录的 `checkpoints.sqlite` 文件。

由于 SQLite Checkpointer 是 LangGraph 的独立扩展包，`requirements.txt` 新增了直接依赖：

```text
langgraph-checkpoint-sqlite==3.1.0
```

核心变化只有两处：导入 `SqliteSaver`，并在编译图时把它传给 `checkpointer`：

```python
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver


database_path = Path(__file__).with_name("checkpoints.sqlite")

with SqliteSaver.from_conn_string(str(database_path)) as checkpointer:
    graph = graph_builder.compile(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "xiaoming-sqlite"}}

    result = graph.invoke(
        {"messages": [("human", "我叫小明，最喜欢的水果是芒果。")]},
        config=config,
    )
    print("助手：", result["messages"][-1].content)

    result = graph.invoke(
        {"messages": [("human", "你还记得我的名字和喜欢的水果吗？")]},
        config=config,
    )
    print("助手：", result["messages"][-1].content)
```

第一次运行时，SQLite 会创建 `checkpoints.sqlite` 及所需的表；第二次运行时会打开同一个数据库。由于两次都使用 `"xiaoming-sqlite"` 这个 `thread_id`，图会读取之前存下的 `messages`，所以即使 Python 进程已经退出，第二个问题依然可以从历史中找到“小明”和“芒果”。

`with ... as checkpointer` 是一个上下文管理器：离开缩进块后会关闭 SQLite 连接。这一点在 Windows 上特别实用，避免脚本结束后数据库文件仍被占用，导致后续程序无法打开、移动或删除它。

`checkpoints.sqlite` 已加入 `.gitignore`。它和第 11 步生成的向量库一样属于本地运行产生的数据，不应随着教程源码提交；如果想从零开始重新体验本节，只要关闭所有使用它的脚本后删除这个文件，再运行一次即可。

### 为什么这样做

- **只替换 Checkpointer，不改图的节点和边**：`InMemorySaver` 与 `SqliteSaver` 都遵守同一个 Checkpointer 接口，因此 `State`、`chatbot` 节点、`add_messages` reducer 和 `thread_id` 的用法完全不变。这说明持久化是图运行时的基础设施选择，而不是要渗透到每个业务节点里的特殊逻辑。
- **SQLite 适合单机教程和小型应用**：它是一个随 Python 一起可用的嵌入式数据库，没有独立服务要启动；一个文件就能保留多个 `thread_id` 的会话历史。多人、高并发或多台服务实例共享状态的生产场景，则更适合换成 Postgres 等服务端 Checkpointer，图的其余部分仍可保持不变。
- **数据库记录的是 Checkpoint，不只是最后一句回复**：为了让 LangGraph 能在任意节点后续跑，或从 `interrupt()` 暂停处恢复，它需要保存完整的图状态及执行元数据。正因为保存的是这些快照，第 18 步的“暂停—人工确认—恢复”机制也可以在进程重启后继续使用；本节的对话记忆只是这个能力最直观的体现。
- **`thread_id` 仍然是会话隔离边界**：SQLite 让数据跨进程存活，并不意味着所有用户共享记忆。把 `config` 改为另一个 `thread_id`，得到的仍是一个没有任何历史的新会话；实际应用通常用稳定的用户 ID、会话 ID 或其组合来生成它。
