# Advertising 规则原样同步

个人仓库订阅：
https://raw.githubusercontent.com/syutsun/Surge/main/Ruleset/Reject/Advertising.list

上游来源 ConnersHua/RuleGo：
https://github.com/ConnersHua/RuleGo/blob/master/Surge/Ruleset/Extra/Reject/Advertising.list

原样下载整个上游文件，不合并、不删减、不去重、不改规则，不添加个人补丁。
文件下载成功并通过基本内容、规则格式和最小数量检查后才更新；保留原始字节与注释。
失败时任务报错，仓库保留上一份规则。每次运行日志记录规则数量和 SHA-256。

每 24 小时检查一次，计划北京时间每天 07:00，由统一任务依次运行，实际执行可能排队或延迟。
有变化时才提交。Actions → Update upstream rules and modules → Run workflow 可手动触发。
长期无仓库活动导致 GitHub 停用定时任务时，需在 Actions 重新启用。

在 Surge 分流规则中将原订阅 URL 替换成自己的订阅地址，沿用 REJECT 策略。
此文件是规则集，不是模块。仓库更新后，Surge 端按规则集的刷新设置拉取新版。
不要直接修改生成文件，否则下一次同步会恢复为上游内容。

参考引用行（合并到现有配置时，修改原有规则集地址即可）：
RULE-SET,https://raw.githubusercontent.com/syutsun/Surge/main/Ruleset/Reject/Advertising.list,REJECT

> 更新时间统一说明：所有定时检查由 `Daily updates at 07 China time` 在北京时间每天 07:00（UTC 前一天 23:00）启动，按顺序运行；统一原样同步流程保留手动和配置变更触发，不再单独设定 cron。具体开始时间可能受 GitHub 调度延迟影响。
