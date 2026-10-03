# 验证记录

[返回项目首页](../README.md)

本记录对应 **2026-10-03** 的本地检查。应用代码基线为 [`950a0c3`](https://github.com/AZ123IT/ResearchPilot/commit/950a0c3282eda07312eaff2e46ff05160375feb9)，本次更新仅调整文档与演示截图，不改变业务实现。结果是一次验证快照，不是持续集成状态。

## 环境

- macOS；Python 3.13.3；Node.js 22.16.0。
- 已安装依赖：LangGraph 1.2.7、MCP Python SDK 1.28.1、FastAPI 0.138.2、python-dotenv 1.2.2、Next.js 15.5.19。
- Python requirements 使用最低版本范围，未锁定全部依赖；其他环境重新安装可能解析出不同版本，不将本次结果扩展为所有版本的兼容保证。

## 检查结果

| 检查 | 结果 | 证明范围 |
| --- | --- | --- |
| pytest | 32 passed，1 条依赖弃用警告 | 工作流、API 结构、工具逻辑与模拟失败分支回归 |
| TypeScript typecheck | 退出码 0 | 静态类型检查，不等于浏览器运行验证 |
| Next.js production build | 构建通过 | 前端生产产物可生成，不等于线上部署 |
| 浏览器 Demo 流程 | HTTP 200；9 步、4 篇 Demo 论文、4 条引用、14 次工具调用 | 无外部密钥的本地前后端闭环 |
| 结果分页与审计 | 综述、来源、参考文献分页和 Calls 面板可访问；未捕获 pageerror | 本次桌面浏览器操作，不是完整 E2E 测试集 |
| 再次运行同一问题 | 返回 3 条历史笔记 | 同一后端进程的 local 模式笔记复用，不证明跨进程持久化 |

浏览器检查使用真实生产构建与 FastAPI 服务，不伪造响应，不调用外部模型或数据库。论文样例是虚构 fixture，来源标签为 `demo`，规则提取产生的高匹配分数不是模型准确率。

pytest 警告来自 Starlette TestClient 对 httpx 集成的弃用提示；本次没有修改依赖，也没有将警告算作测试失败。

## 复现命令

在项目根目录执行后端/MCP 测试，明确禁用本地凭据：

```bash
PYTHON_DOTENV_DISABLED=1 DEEPSEEK_API_KEY= SUPABASE_URL= SUPABASE_SERVICE_ROLE_KEY= \
SEMANTIC_SCHOLAR_API_KEY= .venv/bin/python -m pytest -q
```

前端检查：

```bash
npm --prefix frontend run typecheck -- --incremental false
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000 NEXT_TELEMETRY_DISABLED=1 npm --prefix frontend run build
```

生产构建会固化 `NEXT_PUBLIC_API_BASE_URL`，应在构建时配置。此次截图使用后端 8317 端口、前端 3000 端口；若复现上述默认命令，则使用后端 8000。前端的允许 origin 目前限定在 3000 端口。

截图对应的浏览器操作步骤见 [演示说明](DEMO_SCRIPT.md)。图像保留 Demo、告警与回退信息，没有把它们改成真实检索或模型成功的标签。

## 尚未验证的部分

- 本次没有用真实密钥调用 DeepSeek、arXiv、Semantic Scholar 或 Supabase，也没有运行真实 MCP stdio 协议实验；默认 Demo 使用本地工具函数。
- 单元测试中的模拟结果不能证明第三方服务当前可用，或所有 MCP 生命周期、并发和超时分支正确。
- 没有真实研究问题集合上的相关性、事实支持度或引用准确率评测；没有吞吐量、延迟分位数或成本基准。
- 没有用户鉴权、多租户隔离、生产安全审计或公开部署验证。
- 当前未配置 GitHub Actions CI。页面不使用虚构的 CI、覆盖率或准确率徽章。

本项目展示的是工作流编排、协议适配和可观察的回退设计；检索与结论质量需要独立评测。
