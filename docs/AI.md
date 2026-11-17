# AI 分流：上游同步与个人规则

Surge 规则集订阅：

https://raw.githubusercontent.com/syutsun/Surge/main/Ruleset/AI.list

上游来源（ConnersHua/RuleGo）：

https://github.com/ConnersHua/RuleGo/blob/master/Surge/Ruleset/Extra/AI.list

## 自动更新范围

每天检查上游一次，计划北京时间 08:23，可能因 GitHub 调度或仓库写入锁排队而延迟。

- OpenAI、OpenRouter 两个一级分段固定使用 config/AI-personal.list 中的个人内容，含注释停用规则。
- 其他分段原样同步上游，包括 Meta 等现有服务及将来新增的一级分段。
- 上游在 OpenAI 和 OpenRouter 之间新增的其他服务会保留，不按固定行号截取。
- 上游改变或删除所需标题、返回错误页面、下载不完整或校验不通过时，构建失败并保留上一份文件。
- 仅结果变化时提交，不写入不断变化的构建时间。
- 每次运行日志记录上游 SHA-256。

修改个人内容请编辑 config/AI-personal.list（保留 # OpenAI 和 # OpenRouter 两个标题），提交后会自动重建。请不要直接修改生成文件 Ruleset/AI.list，否则后续同步会覆盖。
可在 Actions → Update personal AI rules → Run workflow 手动运行。

这是分流规则集，不是 .sgmodule 模块。请在 Surge 中将原 RuleGo AI.list 规则集 URL 替换为自己的上述地址，并沿用原来的策略组。
仓库同步和 Surge 下载规则集是不同步骤；Surge 端依其规则集刷新设置取新内容。

公开仓库长期无活动时，GitHub 可能停用定时任务，需在 Actions 中重新启用。
