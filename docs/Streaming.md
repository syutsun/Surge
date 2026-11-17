# 海外流媒体规则：保留个人 Spotify

订阅地址：
https://raw.githubusercontent.com/syutsun/Surge/main/Ruleset/Streaming/!CN.list

上游来源 ConnersHua/RuleGo：
https://github.com/ConnersHua/RuleGo/blob/master/Surge/Ruleset/Extra/Streaming/!CN.list

Spotify 分段固定采用 config/Spotify-personal.list 的个人内容，包括注释。
!CN.list 的 YouTube 分段按个人设置自动注释所有规则（未来新增规则同样注释），保留原有标题和注释；独立 YouTube.list 仍原样同步上游。
其余全部内容原样同步上游，不合并额外规则，不去重，保留原有停用规则、IP-CIDR、GEOIP 和未来新增服务。
替换范围从唯一的 # > Spotify 标题开始，到下一服务或分类标题之前；不是按行号截取。
缺失或重复 Spotify/YouTube 标题、个人文件夹带其他服务、下载错误或校验失败时不提交，保留上一份规则。

每 24 小时检查一次，计划北京时间每天 09:43，GitHub 实际运行可能延迟。
有变化时才提交，和其他同步任务共用仓库写入锁。
Actions → Update personal Streaming rules → Run workflow 可手动运行。
公开仓库长期无活动导致 GitHub 停用定时任务时，需在 Actions 重新启用。

以后修改 Spotify，请编辑 config/Spotify-personal.list。提交后会自动重建。
不要直接修改生成文件 Ruleset/Streaming/!CN.list，下一次同步会覆盖。

在 Surge 分流规则中替换原上游 URL，沿用原来的海外流媒体策略组。
这是规则集，不是模块；Surge 按自己的规则集刷新设置获取仓库新版。


## 独立规则同步范围

以下现有订阅地址也在同一个每天 09:43 的任务中更新，文件名不变：

| 本仓库文件 | 更新来源 |
|---|---|
| Disney+.list | RuleGo Video/Disney+.list，原样同步 |
| HBO-Asia.list | RuleGo Video/HBO-Asia.list，原样同步 |
| HBO.list | RuleGo Video/Max.list，原样同步；保留本地 HBO.list 文件名 |
| Netflix.list | RuleGo Video/Netflix.list，原样同步 |
| TikTok.list | RuleGo Video/TikTok.list，原样同步 |
| YouTube.list | RuleGo Video/YouTube.list，原样同步 |
| Spotify.list | config/Spotify-personal.list，与 !CN.list 中的个人分段一致 |

六份上游文件不合并、不去重、不改规则和注释，保留原始字节。全部文件下载及校验通过后才写入、提交。
有一份下载或校验失败，任务不会提交，仓库保留上一版。
目录内目前共 8 个规则文件（含 !CN.list），均由该任务维护。

## !CN.list 的 YouTube 策略

自 2026-11-17 起，YouTube 分段中所有启用规则自动加上 # 注释，避免此规则集参与 YouTube 流量的策略匹配。后续上游新增 YouTube 规则也会保持注释。其他分段原样同步，Spotify 保留个人规则。
独立 Ruleset/Streaming/YouTube.list 保持原样同步。本设置只针对 !CN.list，不改变其他规则集的优先级或 Google 分流配置。
