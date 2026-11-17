# Apple 规则原样同步

个人仓库订阅：
https://raw.githubusercontent.com/syutsun/Surge/main/Ruleset/Apple.list

上游来源 ConnersHua/RuleGo：
https://github.com/ConnersHua/RuleGo/blob/master/Surge/Ruleset/Extra/Apple/Apple.list

原样下载整个上游文件，保留注释与规则，不增删、不合并、不去重、不添加个人补丁。
下载并通过基本内容、规则格式和最小数量检查后才更新；失败时保留上一份文件。
每次运行日志记录规则数量及 SHA-256，有变化时才提交。

每 24 小时检查一次，计划北京时间每天 09:23，错开已有同步任务，GitHub 实际调度可能延迟。
Actions → Update Apple rules → Run workflow 可手动运行。
长期无仓库活动导致 GitHub 停用定时任务时，需在 Actions 重新启用。

在 Surge 分流规则中将原 Apple.list 订阅地址替换为自己的上述地址，沿用原来的 Apple 策略组。
这是规则集，不是模块；Surge 按自身规则集刷新设置拉取新版。
不要直接修改生成文件，下一次同步会恢复为上游内容。
