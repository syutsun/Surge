# Tracking 规则原样同步

个人仓库订阅：
https://raw.githubusercontent.com/syutsun/Surge/main/Ruleset/Reject/Tracking.list

上游来源 ConnersHua/RuleGo：
https://github.com/ConnersHua/RuleGo/blob/master/Surge/Ruleset/Extra/Reject/Tracking.list

整个文件原样同步，包含原有注释、停用规则和行内注释；不删改规则、不添加补丁。
上游此文件的首行标题为 # Privacy，保持原样。
下载成功并通过基本格式、IP/域名规则类型和最小数量检查后才更新，失败保留上一份规则。
每次运行日志记录规则数量及 SHA-256。

每 24 小时检查一次，计划北京时间每天 09:03，错开已有同步任务，GitHub 实际运行可能延迟。
有变化时才提交。Actions → Update Tracking rules → Run workflow 可手动触发。
公开仓库长期无活动导致 GitHub 停用定时任务时，需在 Actions 中重新启用。

在 Surge 分流规则中将原 Tracking.list 的地址替换为自己的上述订阅地址，沿用 REJECT 策略。
这是规则集，不是模块。Surge 按规则集刷新设置拉取仓库的新内容。
不要直接编辑生成文件，下一次同步会恢复为上游内容。
