# Direct+：去除 Google 分段，其余同步上游

订阅地址：
https://raw.githubusercontent.com/syutsun/Surge/main/Ruleset/Direct+.list

上游来源：
https://github.com/ConnersHua/RuleGo/blob/master/Surge/Ruleset/Direct%2B.list

每次同步去除从 # ---(Alphabet)--- 到下一行 # ------ 之前的整段内容（包括 Google Flights）。
当前该分段包含用户指定的 9 条 Google 规则；未来添加到此分段的规则同样排除。
其余内容完全保留上游原文，不增加个人规则、不去重。
根据用户明确选择，旧文件中的 Emby 个人直连规则也不保留。

每 24 小时检查一次，计划北京时间每天 07:00，实际 GitHub 调度可能延迟。
缺失或重复分段边界、下载错误或格式校验失败时不提交，保留上一份文件。有变化才提交。
可在 Actions → Update personal Direct Plus rules → Run workflow 手动触发。
公开仓库长期无活动导致定时任务停用时，需在 Actions 重新启用。

现有订阅地址保持不变，Surge 沿用原策略组并按自身规则集刷新设置取新版。

> 更新时间统一说明：所有定时检查由 `Daily updates at 07 China time` 在北京时间每天 07:00（UTC 前一天 23:00）启动，按顺序运行；本文件对应工作流保留手动和配置变更触发，不再单独设定 cron。具体开始时间可能受 GitHub 调度延迟影响。
