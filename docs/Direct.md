# Direct：排除 PayPal，其余同步上游

订阅地址：
https://raw.githubusercontent.com/syutsun/Surge/main/Ruleset/Direct.list

上游来源：
https://github.com/ConnersHua/RuleGo/blob/master/Surge/Ruleset/Direct.list

每次同步删除 # > PayPal 分段，直到下一个服务或分类标题之前。当前删除用户指定的四条 PayPal 规则，后续添加到此分段的规则也会删除。
其余内容原样同步，包含 Microsoft、Steam 的子标题及 Tencent IP 规则；不增加其他规则或补丁。
独立 Ruleset/PayPal.list 不受影响，继续按已配置的任务原样同步上游。

每 24 小时检查一次，计划北京时间每天 10:43，实际 GitHub 调度可能延迟。
下载、规则格式或分段边界校验失败时不提交，保留上一版；有变化才提交。
Actions → Update personal Direct rules → Run workflow 可手动执行。
公开仓库长期无活动导致 GitHub 停用定时任务时，需在 Actions 重新启用。

现有订阅地址不变，Surge 沿用原策略组，并按自身规则集刷新设置取新版。
