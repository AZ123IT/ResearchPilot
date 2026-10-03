# 架构与实现取舍

[返回项目首页](../README.md)

ResearchPilot 将编排、工具执行、模型抽取和结果展示分开。目标是让一次研究整理任务可检查、可回退，而不是让模型自主决定所有操作。

## 请求与状态

```text
Next.js /research
  -> POST /api/research/run
  -> Pydantic ResearchRequest
  -> LangGraph ResearchGraphState
  -> ResearchToolClient + DeepSeekClient
  -> Pydantic ResearchResponse
  -> 综述 / 来源 / 引用 / 审计面板
```

请求包含问题、结果数量和引用格式。后端同步运行工作流，完成后一次性返回结果；前端显示的步骤记录不是实时流式事件。[请求入口](../backend/app/api/research.py) · [数据结构](../backend/app/models/schemas.py)

`ResearchGraphState` 保存论文、笔记、候选结论、引用、摘要关联、步骤和工具日志。节点返回部分状态更新，列表由节点代码显式拼接。当前每次请求构建并执行图，没有配置 checkpoint 或中断恢复。[状态定义](../backend/app/agent/state.py) · [图定义](../backend/app/agent/graph.py)

## 九节点工作流

| 顺序 | 节点 | 责任 |
| --- | --- | --- |
| 1 | `plan_research_task` | 根据配置生成固定研究计划，不调用模型规划 |
| 2 | `search_notes_node` | 关键词检索最多三条历史笔记，返回给界面展示 |
| 3 | `search_papers_node` | 搜索论文，必要时在节点内部追加一次查询 |
| 4 | `fetch_paper_details_node` | 获取元数据；详情不可用时保留搜索结果 |
| 5 | `extract_summary_node` | DeepSeek 抽取候选结论，或按规则选择摘要句子 |
| 6 | `verify_evidence_node` | 按词汇重合度关联摘要、分配匹配等级 |
| 7 | `format_citations_node` | 为选中文献生成引用文本 |
| 8 | `save_notes_node` | 保存匹配等级非 low 的结论 |
| 9 | `generate_final_review_node` | 模板化组装综述、方法、限制和运行记录 |

补搜条件为：已有论文非空、少于目标数量、包含非 Demo 来源。改写方式为在原问题后追加固定词组 `evidence coverage citation verification`，最多一轮。零结果不会触发该补搜；最终匹配等级也不会反向触发它。[具体逻辑](../backend/app/agent/nodes.py)

## MCP 会话与工具边界

使用 MCP Python SDK 中的 `FastMCP` 注册工具，通过 stdio 与客户端通信。`ResearchToolClient` 是编排层使用的 Python 接口，不等于 MCP 协议本身。

| 工具 | 输入要点 | 输出与限制 |
| --- | --- | --- |
| `search_papers` | query、max_results、source | 规范化论文、来源统计、缓存/回退标记 |
| `fetch_paper_detail` | paper_id、source | arXiv / Demo 详情；Semantic Scholar 独立详情查询尚未实现 |
| `format_citation` | paper、style | 简化的 IEEE / APA / BibTeX 文本，正式投稿前需复核 |
| `save_to_notes` | paper_id、content、title、source | Supabase 或内存存储结果 |
| `search_notes` | query、top_k | 关键词排序的笔记和存储类型 |

[工具注册](../mcp_server/server.py) · [客户端实现](../backend/app/mcp_client/client.py)

- `local`：直接执行 Python 函数，不初始化 MCP 连接。
- `mcp_single`：每次调用启动服务进程、初始化会话、调用工具后关闭。进程内笔记不能跨调用保留。
- `mcp_persistent`：后端复用服务进程和会话，后台线程中的事件循环通过 Queue 接收任务，用 Future 回传结果。当前串行执行，不是连接池；FastAPI lifespan 负责关闭。

后端与独立 MCP 服务应使用同一项目虚拟环境。在本地 `.env` 中设置：

```env
RESEARCH_TOOL_CLIENT_MODE=mcp_persistent
MCP_SERVER_COMMAND=/absolute/path/to/ResearchPilot/.venv/bin/python
MCP_SERVER_ARGS=mcp_server/server.py
MCP_SERVER_CWD=/absolute/path/to/ResearchPilot
MCP_FALLBACK_TO_LOCAL=false
```

将路径替换为实际项目路径。关闭本地回退适合验证真实协议链路；允许回退时，MCP 异常会被记录并尝试本地函数。不能把“请求最终成功”直接当成“MCP 调用成功”。写操作超时后回退还可能带来重复写入，当前没有幂等键或 exactly-once 保证。

## 检索与缓存

`auto` 模式先查 arXiv，数量不足时尝试 Semantic Scholar，随后规范化和去重。arXiv 查询使用问题文本，并按提交日期排序；没有语义重排或经过评测的相关性门控。

成功检索结果进入进程内缓存，键由规范化问题、source 和 max_results 组成，TTL 为 600 秒。它用于失败/无结果时的回退，**不是每次优先读缓存的 cache-first 方案**，也不跨进程共享。

Demo 必须显式开启，使用 [虚构论文样例](../mcp_server/data/demo_papers.json)，来源为 `demo`。真实检索失败不会自动把这些样例伪装成搜索结果。[检索工具](../mcp_server/tools/search_papers.py)

## 模型与摘要匹配

DeepSeek 输入研究问题及前五篇论文的标题、摘要，不接收全文、历史笔记或工具定义。模型输出按非空行解析成候选结论；当前尚未使用严格结构化输出，前言也可能被误计为一条结论。未配置密钥或调用异常时，使用确定性规则提取摘要句子。[模型调用](../backend/app/llm/deepseek_client.py)

摘要匹配将文本转成英文关键词集合，过滤停用词与短词后计算：

```text
score = |结论关键词 ∩ 摘要关键词| / |结论关键词|
high: score >= 0.55
medium: score >= 0.25
low: 其他情况
```

为每条结论选择最高分论文，展示其摘要前 240 字符左右的预览。该算法不能判断否定关系、因果关系或是否回答了用户的问题，阈值没有经过事实正确率校准。`supported` 是当前规则的输出标签，不是经过专家审查的事实证明。[匹配算法](../backend/app/services/verification_service.py)

## 笔记与可观测性

Supabase 配置可用时使用数据库，否则使用进程内列表并返回告警。笔记检索当前是关键词重合排序；Supabase 查询先取有限条目再在 Python 中排序，并不是全文库上的语义检索。`embedding vector(1536)` 只预留 schema，没有生成 embedding。

历史笔记通过响应返回并展示，不注入 DeepSeek 上下文。内存存储会随所属进程退出而丢失，持久 MCP 也不改变这一点。[笔记工具](../mcp_server/tools/notes.py) · [数据库 schema](../supabase/schema.sql)

响应包含步骤、工具输入/输出预览、耗时、错误、warnings、缓存标记和回退摘要。日志预览做了有限字段脱敏与截断，但没有全链路 tracing、模型 Token/成本统计或完整秘密扫描。计划列表的 `completed` 不能取代对各工具日志和 warnings 的检查。

## 取舍与下一步

1. 固定图便于检查状态与失败分支，但不具备自主多智能体规划。
2. 本地工具便于开发；MCP 提供协议边界，但增加进程、会话与超时管理成本。
3. 摘要处理降低原型复杂度，但无法支撑全文级证据核查。
4. 应优先补充真实查询相关性与结论支持度评测，再考虑全文检索、结构化抽取、流式事件与持久化任务恢复。

[验证范围与缺口](VALIDATION.md) · [运行与排查](DEMO_SCRIPT.md)
