# 六份 RuleGo 规则原样同步

每 24 小时检查一次，计划北京时间每天 07:00，由统一任务依次运行；实际 GitHub 调度可能延迟。
下载六份文件并全部校验通过后才提交，任一下载或校验失败时保留上一版。
原样保留规则、注释及停用项，不添加个人补丁、不去重、不合并其他来源。

| 本仓库文件 | ConnersHua/RuleGo master 上游路径 |
|---|---|
| Ruleset/PayPal.list | Surge/Ruleset/Extra/PayPal.list |
| Ruleset/Proxy+.list | Surge/Ruleset/Proxy+.list |
| Ruleset/Proxy.list | Surge/Ruleset/Proxy.list |
| Ruleset/Telegram.list | Surge/Ruleset/Extra/Telegram.list |
| Ruleset/WeChat.list | Surge/Ruleset/Extra/WeChat.list |
| Ruleset/X.list | Surge/Ruleset/Extra/X.list |

X.list 上游标题目前为 Twitter，原样保留。PayPal 的 USER-AGENT 和 Proxy+ 的 GEOIP 规则也保留。
运行日志记录每个文件的规则数量及 SHA-256，仅内容变化时提交。
不修改 AI、Apple、Direct、Google、T-Mobile 或已有流媒体规则。

所有现有个人仓库订阅地址保持不变，沿用各规则原有的 Surge 策略组。
Surge 按自身规则集刷新设置拉取仓库新版。
不要直接编辑这些生成文件，后续同步会恢复为上游内容。
Actions → Update selected RuleGo rules → Run workflow 可手动执行。
公开仓库长期无活动导致 GitHub 停用定时任务时，需在 Actions 中重新启用。

> 更新时间统一说明：所有定时检查由 `Daily updates at 07 China time` 在北京时间每天 07:00（UTC 前一天 23:00）启动，按顺序运行；本文件对应工作流保留手动和配置变更触发，不再单独设定 cron。具体开始时间可能受 GitHub 调度延迟影响。
