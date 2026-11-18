# 流媒体规则每日同步与个人设置

每日北京时间 08:00 检查一次上游，实际 GitHub 调度可能延迟。有变化才提交，下载或校验失败时保留上一版。

## Spotify 个人补充

config/Spotify-personal.list 只保存个人额外规则，目前只有：
DOMAIN-SUFFIX,spotifycdn.com

Ruleset/Streaming/Spotify.list 原始内容来自 RuleGo 的 Surge/Ruleset/Extra/Streaming/Music/Spotify.list，并补充个人规则。
Ruleset/Streaming/!CN.list 中的 Spotify 分段来自 RuleGo 的同名综合规则文件，再补充同一条个人规则。
其他 Spotify 域名、关键词以及上游新增或删除的规则都随各自上游同步，不再固定旧版七条规则。
如果上游已经包含同一条启用规则，不再重复添加。

修改个人补充请编辑 config/Spotify-personal.list（保留 # > Spotify 标题），提交后自动重建。不要直接修改生成文件。

## !CN.list 的 YouTube 设置

综合 !CN.list 的 YouTube 分段所有启用规则自动加 # 注释，未来新增规则也保持注释。其他服务原样同步上游。
独立 YouTube.list 原样同步上游，不受综合规则的注释设置影响。
Spotify 或 YouTube 标题缺失或重复时拒绝发布，防止个人设置失效。

## 独立文件来源

| 本仓库文件 | ConnersHua/RuleGo master 上游 |
|---|---|
| Disney+.list | Surge/Ruleset/Extra/Streaming/Video/Disney+.list |
| HBO-Asia.list | Surge/Ruleset/Extra/Streaming/Video/HBO-Asia.list |
| HBO.list | Surge/Ruleset/Extra/Streaming/Video/Max.list |
| Netflix.list | Surge/Ruleset/Extra/Streaming/Video/Netflix.list |
| TikTok.list | Surge/Ruleset/Extra/Streaming/Video/TikTok.list |
| YouTube.list | Surge/Ruleset/Extra/Streaming/Video/YouTube.list |

这六份规则由 Update upstream rules and modules 统一原样同步，每个文件独立校验。
现有订阅地址、文件名不变。Surge 沿用各文件的原策略组，按自身规则集刷新设置拉取新版。

Actions → Update personal Streaming rules → Run workflow 可手动触发。公开仓库长期无活动导致 GitHub 停用定时任务时，需在 Actions 重新启用。

> 更新时间统一说明：所有定时检查由 `Daily updates at 08 China time` 在北京时间每天 08:00（UTC 当天 00:00）启动，按顺序运行；本文件对应工作流保留手动和配置变更触发，不再单独设定 cron。具体开始时间可能受 GitHub 调度延迟影响。
