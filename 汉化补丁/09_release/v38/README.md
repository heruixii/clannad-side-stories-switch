# CLANNAD Side Stories NS 简体中文补丁 v38 测试版

适用 Title ID：01007b501372c000
适用 main NSO Build ID：AB53346DF8D55798AB3304D1712F9966C3999D1D（完整 Build ID 后续为 0）

## 内容
- SCRIPT.PAK：4573/4573 正文中文覆盖，97/97 标题中文覆盖，历史 336 条截断已全部消除。
- PARTS.PAK：中文化 CONFIG_BG_EN、CONFIG_TAB_EN、system_menu_en 三个确认含英文文字的 UI 图片资源。
- ExeFS IPS：145 条菜单/系统提示原位中文化；另将 Help / No / On 通过 4 组标准 ADRP+ADD 引用安全重定位到现有字符串槽零填充区，显示为“帮助 / 否 / 开”。

## 安装
将本目录中的 atmosphere 文件夹复制到 SD 卡根目录并合并。

## PC 侧验证
- SCRIPT.PAK 等长、结构与全部正文槽验证通过。
- PARTS.PAK 总大小与原版一致；96 个子文件中只有 3 个目标 UI 资源变化，其余 93 个逐字节不变。
- CZ3/CZ4 中文图片 PNG→CZ→PNG 往返像素一致。
- ExeFS IPS 从原始未压缩 main 应用后与目标 NSO 字节级一致；三个短字符串 4 组 xref 均解码到新中文地址。
- FONT.PAK 未替换；原版字库已验证包含所需 CJK 覆盖。

## 下一步
仅剩 Switch 实机验收：检查字体、菜单图层、按钮状态、章节推进和换行视觉效果。

## 校验
见 SHA256SUMS.txt。
