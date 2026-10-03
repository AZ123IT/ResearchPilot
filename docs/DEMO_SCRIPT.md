# 演示与故障排查

[返回项目首页](../README.md)

## 无外部服务演示

先完成 README 中的依赖安装。在项目根目录开启终端一：

```bash
PYTHON_DOTENV_DISABLED=1 DEEPSEEK_API_KEY= SUPABASE_URL= SUPABASE_SERVICE_ROLE_KEY= \
RESEARCH_TOOL_CLIENT_MODE=local RESEARCHPILOT_DEMO_MODE=true scripts/run_backend.sh
```

终端二：

```bash
scripts/run_frontend.sh
```

打开 `http://127.0.0.1:3000/research`，输入：

```text
What are recent methods for improving RAG faithfulness?
```

保留 Results 为 5、Style 为 IEEE，点击 **Run workflow**。内置样例共有四篇，返回四篇是正常行为；Demo 不触发追加检索。

截图中论文、作者、摘要来自虚构 fixture，不是可用于学术引用的真实文献。未配置模型时，结论为规则式摘要句子提取。`high` 匹配也可能只是因为结论直接取自摘要，不能作为模型质量成绩。

## 建议查看顺序

1. 顶部 `Demo` 标签：确认数据模式，避免把样例当实时检索。
2. Research strategy and audit：查看九步计划、补搜报告与结论关联。
3. 向下滚动结果区，查看 Literature review 的来源摘要、Methods 和 Limitations。
4. 底部分页切换 Sources 和 Bibliography，检查来源与格式化引用。
5. 打开右下角 Audit，检查 Workflow、Calls、Memory 和 Notes。Calls 可以展开输入/输出预览；Notes 包含告警，不是笔记库。
6. 再次运行同一问题，观察进程内历史笔记命中。历史笔记展示不代表模型已使用这些笔记推理。

## 为什么会有 warning

| 现象 | 如何理解与排查 |
| --- | --- |
| `search_notes` 找到笔记仍显示 warning | 未配置 Supabase 时使用内存存储，警告的是存储回退，不是一定没有找到笔记 |
| `extract_summary` 使用 fallback | 检查是否未配置 DeepSeek 或模型调用失败；不要公开原始密钥 |
| `mcp_persistent` 最后仍有结果 | 检查 `fallback_used`；允许本地回退时，结果成功不能证明 MCP 成功 |
| 返回论文但明显不相关 | 核对查询、来源和论文摘要；数量与词汇匹配不等于相关性，当前排序仍有局限 |
| 显示 `completed` 但有错误 | 计划完成标记不代表每个工具都成功，应结合 Calls 与 Notes 排查 |
| 重启后笔记消失 | 内存是进程级存储；需要持久保存时配置 Supabase |

## API 示例

服务存活检查不验证外部 API 或模型是否可用：

```bash
curl -sS http://127.0.0.1:8000/health
```

```bash
curl -sS -X POST http://127.0.0.1:8000/api/research/run \
  -H 'Content-Type: application/json' \
  -d '{"question":"What are recent methods for improving RAG faithfulness?","max_results":5,"citation_style":"IEEE"}'
```

## 切换真实服务

停止 Demo 后端，用本地 `.env` 配置 `RESEARCHPILOT_DEMO_MODE=false` 及所需密钥，再运行 `scripts/run_backend.sh`。不要继续沿用上面强制清空凭据的启动命令。

模型接收问题、论文标题及摘要；Supabase 保存研究笔记。只使用有权发送到对应服务的数据。不要为了截图隐藏真实警告或伪造检索结果。

## 端口冲突

后端端口可以调整，例如在对应终端使用：

```bash
PORT=8001 scripts/run_backend.sh
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8001 scripts/run_frontend.sh
```

前端仍访问 `http://127.0.0.1:3000/research`。当前 [CORS 白名单](../backend/app/main.py) 只允许 localhost / 127.0.0.1 的 3000 端口；若必须更换前端端口，应同时明确更新后端允许的 origin，不能只改 `PORT`。前端启动脚本从终端环境获取 API 地址，不会自动读取项目根目录 `.env` 中的该变量。
