# 墨鱼去开屏 2.0：原规则自动转换

Surge 远程模块：

https://raw.githubusercontent.com/syutsun/Surge/main/Module/StartUpAds.sgmodule

Surge「模块 → 安装新模块」粘贴该 URL 即可；开启 MITM 并安装、信任证书。
仅转换 https://ddgksf2013.top/rewrite/StartUpAds.conf ，保留原作者署名、规则、脚本引用和 MITM 域名，不合并其他项目的应用补丁。
转换器生成的静态辅助脚本仍由 Script Hub 官方 GitHub 提供；Surge 无需安装 Script Hub 工具模块。

## 更新

GitHub Actions 每 24 小时检查，计划时间为北京时间每天 08:23（GitHub 可能延迟）。
也可在 Actions → Update Moyu StartUpAds → Run workflow 手动运行。
只有转换结果变化时才提交；每次保留上游 SHA-256，结果不含每次变化的构建时间。
仓库生成最新模块后，Surge 仍需刷新该远程模块才能获取最新内容；仓库的定时任务不会向设备推送。

公开仓库的定时任务可能在连续 60 天没有仓库活动后被 GitHub 停用，届时需在 Actions 中重新启用。
上游返回 HTML、下载失败、出现未支持的新语法、转换规则数或 MITM 域名不完整时，任务失败并保留上一份模块。

## 转换实现

运行：Node.js 22+，执行 node scripts/build-startup-ads.mjs。
采用 Script-Hub-Org/Script-Hub 的原始 Rewrite-Parser.js（GPL-3.0）：
https://github.com/Script-Hub-Org/Script-Hub/tree/b8e405cba4e751feaacda97f2148bf3590b5c92d
固定版本并校验 SHA-256；运行时下载，不在此仓库复制其源码。
只增加 Surge 格式需要的唯一脚本名称和 binary-body-mode 标记，不增加应用去广告规则。
被上游注释的规则保持停用。上游脚本内容通过 URL 引用，不执行、不解密、不合并第三方补丁。

自动构建校验不能替代 iPhone/iPad 上的 Surge 实际功能测试。
