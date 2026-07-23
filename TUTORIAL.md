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
