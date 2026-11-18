# Surge 模块每日上游同步

每天北京时间 08:00 检查以下原作者或用户指定的来源，有变化才提交。文件名和个人仓库订阅 URL 不变。
Spotify、YouTube、Zhihu、Bilibili 保留自定义显示名，其他内容跟随上游。Advertising、Script Hub、Sub-Store 原样同步。
原始脚本仍由各模块所引用的远程地址提供，本任务不重新编写或合并脚本。

| 本仓库文件 | 原作者来源 |
|---|---|
| Advertising.sgmodule | https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Module/Block/Advertising.sgmodule |
| Script Hub.sgmodule | https://raw.githubusercontent.com/Script-Hub-Org/Script-Hub/main/modules/script-hub.surge.sgmodule |
| Spotify.sgmodule | https://raw.githubusercontent.com/app2smile/rules/master/module/spotify.module |
| Sub-Store.sgmodule | https://raw.githubusercontent.com/sub-store-org/Sub-Store/master/config/Surge.sgmodule |
| YouTube.sgmodule | https://raw.githubusercontent.com/Maasea/sgmodule/master/YouTube.Enhance.sgmodule |
| Bilibili.sgmodule | https://raw.githubusercontent.com/gys619/surge-tools/main/modules/Bilibili_remove_ads.sgmodule （用户指定转换版，保留原作者 kokoryh 署名） |
| Zhihu.sgmodule | https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/script/zheye/zheye.sgmodule |

自定义显示名的来源维护在 config/Module-upstreams.json，可手动运行 Update Surge modules with personal names。
原样同步的来源维护在 config/Upstream-mirrors.json，可手动运行 Update upstream rules and modules。
两个流程均检查必要配置节和文件大小。原样同步对每个文件独立校验，失败的文件保留上一版。
公开仓库长期无活动导致 GitHub 停用定时任务时，需在 Actions 中重新启用。

## 另有任务的模块

StartUpAds.sgmodule 继续使用 scripts/build-startup-ads.mjs 的每日统一任务中的转换步骤，不由本任务覆盖。

## 哔哩哔哩来源

用户已确认使用 gys619/surge-tools 的 Bilibili_remove_ads.sgmodule，现纳入本任务每天同步。
它是现成的 Surge 转换版；直接同步该文件，不重新抓取或转换返回 403 的原始 Loon 插件，也不切换 BiliUniverse。
只保留用户本地 Bilibili 显示名称，其他内容随指定来源更新。原脚本仍使用模块内注明的远程地址。

仓库自动更新和 Surge 设备刷新是不同步骤。更新设备中的模块和远程脚本时，请在 Surge 中刷新对应资源。

> 更新时间统一说明：所有定时检查由 `Daily updates at 08 China time` 在北京时间每天 08:00（UTC 当天 00:00）启动，按顺序运行；这两类工作流均保留手动和配置变更触发，不再单独设定 cron。具体开始时间可能受 GitHub 调度延迟影响。
