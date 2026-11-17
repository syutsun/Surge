# 万年历 Pro · 墨鱼原脚本

Surge 模块：https://raw.githubusercontent.com/syutsun/Surge/main/Module/Wannianli.sgmodule

原始来源：https://ddgksf2013.top/scripts/wannianli.vip.js

仅将原脚本头部的 QX 配置转换成 Surge 模块，不合并其他补丁。原始脚本原样同步到 Scripts/wannianli.vip.js，模块的脚本地址也指向本仓库。保留原作者 @ddgksf2013 署名。

在 Surge「模块 → 安装新模块」粘贴上述模块地址并启用，开启 MITM 并安装、信任证书；无需安装 Script Hub。
万年历模块与去开屏模块为两个独立模块。

GitHub Actions 每 24 小时检查一次，计划北京时间每天 08:23。与去开屏任务共用提交锁，避免同时提交导致冲突，实际运行可能排队或延迟。有变化时才提交，下载、语法或配置转换检查失败时不提交。可在 Actions → Update Moyu Wannianli 手动触发。

仓库自动更新与 Surge 设备拉取更新是两个步骤。更新模块配置和其中缓存的远程脚本时，请在 Surge 内刷新相应资源。公开仓库定时任务若长期无活动被 GitHub 停用，需在 Actions 重新启用。

已检查配置转换及脚本的 Surge 接口兼容性，并用模拟响应验证两个匹配路径；未在真实万年历 App 中验证会员功能。实际效果由原脚本、应用版本及服务端决定。
