# 验证记录

[返回项目首页](../README.md)

每次推送与 Pull Request 都由 [GitHub Actions CI](../.github/workflows/ci.yml) 执行 pytest（Python 3.12 / 3.13）、TypeScript 类型检查与 Next.js 生产构建。本页记录 CI 之外的本地检查与实验。

## 2026-11-02：检索与结构化输出改进

### 检查结果

| 检查 | 结果 |
| --- | --- |
| pytest | 39 passed（新增 arXiv 查询构造与 DeepSeek 输出解析测试） |
| TypeScript typecheck | 通过 |
| Next.js production build | 通过 |

### arXiv 检索相关性对比

同一问题 `What are recent methods for improving RAG faithfulness?`，前 5 条 arXiv 结果（真实 API 调用）：

| 版本 | 查询方式 | 相关结果 |
| --- | --- | --- |
| 改进前 | `all:<整句问题>`，按提交时间降序 | 0 / 5（胸片影像、世界模型、稀疏注意力等） |
| 改进后 | `all:rag AND all:faithfulness`，按相关度排序 | 5 / 5（FAIR-RAG、RAG faithfulness 基准等） |

原因：整句问题中的疑问词与泛化词几乎能匹配所有论文，叠加按时间排序，结果退化为“最新提交”。改进后只保留主题词并要求全部命中，无结果时再放宽为 OR。这是单个问题的对照实验，不是系统性相关性评测。

## 2026-10-03：Demo 端到端检查

环境：macOS；Python 3.13.3；Node.js 22.16.0；LangGraph 1.2.7、MCP Python SDK 1.28.1、FastAPI 0.138.2、Next.js 15.5.19。

| 检查 | 结果 |
| --- | --- |
| pytest | 32 passed |
| TypeScript typecheck / production build | 通过 |
| 浏览器 Demo 流程 | HTTP 200；9 步、4 篇 Demo 论文、4 条引用、14 次工具调用 |
| 结果分页与审计 | 综述、来源、参考文献分页和 Calls 面板可访问；无未捕获页面错误 |
| 再次运行同一问题 | 返回 3 条历史笔记（同一后端进程的 local 模式笔记复用） |

浏览器检查使用真实生产构建与 FastAPI 服务，未调用外部模型或数据库；Demo 论文为虚构样例，来源标签为 `demo`。

## 复现命令

在项目根目录执行，禁用本地凭据：

```bash
PYTHON_DOTENV_DISABLED=1 DEEPSEEK_API_KEY= SUPABASE_URL= SUPABASE_SERVICE_ROLE_KEY= \
SEMANTIC_SCHOLAR_API_KEY= .venv/bin/python -m pytest -q
```

前端检查：

```bash
npm --prefix frontend run typecheck -- --incremental false
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000 NEXT_TELEMETRY_DISABLED=1 npm --prefix frontend run build
```

生产构建会固化 `NEXT_PUBLIC_API_BASE_URL`，应在构建时配置。后端 CORS 目前允许 3000 端口的前端来源。截图对应的浏览器操作步骤见 [演示说明](DEMO_SCRIPT.md)。

## 尚未覆盖的部分

- 单元测试中的外部服务（arXiv、Semantic Scholar、DeepSeek、Supabase）均为 mock，不能证明第三方服务当前可用。
- 尚无真实研究问题集上的相关性、结论支持度或引用准确率评测，也没有吞吐量、延迟分位数与成本基准。
- Python 依赖使用最低版本范围，未锁定全部传递依赖。
