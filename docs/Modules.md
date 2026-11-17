# Surge 模块每日上游同步

每天北京时间 11:03 检查以下原作者或用户指定的来源，有变化才提交。文件名和个人仓库订阅 URL 不变。
保留用户现有 #!name 显示名称，其他配置、参数默认值、作者署名、脚本地址及说明跟随上游。
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

来源映射在 config/Module-upstreams.json。
下载后检查模块名称、必要配置节和文件大小。所有文件校验通过后才写入，CI 全部成功才提交。
任何来源下载或校验失败，不提交，保留上一版；不会用 HTML、错误页或其他作者的模块替换。
运行日志记录上游和输出 SHA-256。GitHub 调度可能延迟。Actions → Update original Surge modules 可手动触发。
公开仓库长期无活动导致 GitHub 停用定时任务时，需在 Actions 中重新启用。

## 另有任务的模块

StartUpAds.sgmodule 继续使用 scripts/build-startup-ads.mjs 的独立每日 08:23 转换任务，不由本任务覆盖。

## 哔哩哔哩来源

用户已确认使用 gys619/surge-tools 的 Bilibili_remove_ads.sgmodule，现纳入本任务每天同步。
它是现成的 Surge 转换版；直接同步该文件，不重新抓取或转换返回 403 的原始 Loon 插件，也不切换 BiliUniverse。
只保留用户本地 Bilibili 显示名称，其他内容随指定来源更新。原脚本仍使用模块内注明的远程地址。

仓库自动更新和 Surge 设备刷新是不同步骤。更新设备中的模块和远程脚本时，请在 Surge 中刷新对应资源。
