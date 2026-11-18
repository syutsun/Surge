# 墨鱼去开屏 2.0：原规则自动转换

Surge 远程模块：

https://raw.githubusercontent.com/syutsun/Surge/main/Module/StartUpAds.sgmodule

Surge「模块 → 安装新模块」粘贴该 URL 即可；开启 MITM 并安装、信任证书。
仅转换 https://ddgksf2013.top/rewrite/StartUpAds.conf ，保留原作者署名、规则、脚本引用和 MITM 域名，不合并其他项目的应用补丁。
转换器生成的静态辅助脚本仍由 Script Hub 官方 GitHub 提供；Surge 无需安装 Script Hub 工具模块。

## 更新

GitHub Actions 每 24 小时检查，计划时间为北京时间每天 08:00（GitHub 可能延迟）。
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
还原并逐条校验上游原始 URL 正则、处理动作、原脚本地址、替换参数，以及完整分流和 MITM 域名。
校验不只比较总数：同数量的规则被替换、脚本链接或参数被改动也会拒绝发布。
被上游注释的规则保持停用。上游脚本内容通过 URL 引用，不执行、不解密、不合并第三方补丁。

自动构建校验不能替代 iPhone/iPad 上的 Surge 实际功能测试。

> 更新时间统一说明：所有定时检查由 `Daily updates at 08 China time` 在北京时间每天 08:00（UTC 当天 00:00）启动，按顺序运行；本文件对应工作流保留手动和配置变更触发，不再单独设定 cron。具体开始时间可能受 GitHub 调度延迟影响。

## 模块头部

按用户设置，生成模块开头只保留以下两行：

```
#!name=StartUpAds
#!desc=墨鱼去开屏2.0
```

其他头部元数据、构建信息和原始脚本说明不再写入模块。规则正文保留，原始作者为 @ddgksf2013，来源仍为 https://ddgksf2013.top/rewrite/StartUpAds.conf 。
上游 SHA-256、转换器版本和规则完整性统计移到 Actions 日志，原有逐条校验继续执行。
