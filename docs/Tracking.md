# Tracking 规则原样同步

个人仓库订阅：
https://raw.githubusercontent.com/syutsun/Surge/main/Ruleset/Reject/Tracking.list

上游来源 ConnersHua/RuleGo：
https://github.com/ConnersHua/RuleGo/blob/master/Surge/Ruleset/Extra/Reject/Tracking.list

MI 分段的启用规则按个人设置自动加 # 注释；原有注释、停用规则和行内说明保持不变。
其他分段原样同步上游，不添加其他补丁。
上游此文件的首行标题为 # Privacy，保持原样。
下载成功、通过基本格式/规则类型/最小数量检查，并成功定位唯一 MI 分段后才更新，失败保留上一份规则。
每次运行日志记录规则数量及 SHA-256。

每 24 小时检查一次，计划北京时间每天 09:03，错开已有同步任务，GitHub 实际运行可能延迟。
有变化时才提交。Actions → Update Tracking rules → Run workflow 可手动触发。
公开仓库长期无活动导致 GitHub 停用定时任务时，需在 Actions 中重新启用。

在 Surge 分流规则中将原 Tracking.list 的地址替换为自己的上述订阅地址，沿用 REJECT 策略。
这是规则集，不是模块。Surge 按规则集刷新设置拉取仓库的新内容。
不要直接编辑生成文件，下一次同步会恢复为上游内容。

## MI 个人设置

每次同步自动注释从唯一 # > MI 标题开始，到下一服务或分类标题之前的所有启用规则。当前共注释 6 条，api.miwifi.com 原本已注释，保持原样。未来上游新增到该分段的规则同样自动注释。
MI 标题缺失或重复时任务失败，不发布未应用个人设置的上游版本。订阅地址和每天 09:03 的更新计划保持不变。
