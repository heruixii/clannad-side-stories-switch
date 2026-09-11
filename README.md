# CLANNAD Side Stories Nintendo Switch 简体中文汉化

《CLANNAD 光見守る坂道で / CLANNAD Side Stories / 被光守望着的坡道》Nintendo Switch 简体中文汉化移植工程。

本仓库保存可安装补丁、关键构建/验证脚本、阶段记录与质量审计资料。**不包含游戏本体、XCI/NSP/NCA、密钥、原始 RomFS 或存档。**

## 当前状态

当前公开测试版本：**v38-test**

状态标记：`V38_FULL_LOCALIZATION_READY_FOR_HARDWARE_QA`

PC 侧已完成正文、标题、主要 UI 图片、主程序 UI 字符串以及结构验证；当前剩余工作仅为 Nintendo Switch 实机验收。

| 项目 | 状态 |
| --- | --- |
| Title ID | `01007B501372C000` |
| 正文 | 4573 / 4573 已中文化 |
| 标题 | 97 / 97 已中文化 |
| 历史截断 | 336 / 336 已消除 |
| 图片 UI | 3 个确认含英文文字的资源已中文化 |
| 主程序 UI | 145 条原位中文化；`Help / No / On` 已安全重定位为“帮助 / 否 / 开” |
| 严重串行抽查 | 0 / 650；单侧 95% 上限约 0.4598% |
| 实机验收 | 待完成 |

## 安装

推荐直接从 GitHub Releases 下载 `CLANNAD_Side_Stories_CHS_v38_test.zip`。

1. 确认游戏 Title ID 为 `01007B501372C000`。
2. 解压补丁。
3. 将其中的 `atmosphere` 文件夹复制到 SD 卡根目录并合并。
4. 完全退出游戏后重新启动。

补丁目录结构：

```text
atmosphere/
├─ contents/
│  └─ 01007b501372c000/
│     └─ romfs/
│        ├─ SCRIPT.PAK
│        └─ PARTS.PAK
└─ exefs_patches/
   └─ CLANNAD_Side_Stories_CHS/
      └─ AB53346DF8D55798AB3304D1712F9966C3999D1D.ips
```

## 质量验证

正文最终版本保持 `SCRIPT.PAK` 原始文件总长度不变，并完成文本槽、标题、控制字符、UTF-16 与历史截断回归检查。

`PARTS.PAK` 重建前后均为 8,534,016 字节。全量拆包对比共 96 个子文件，仅 `CONFIG_BG_EN`、`CONFIG_TAB_EN`、`system_menu_en` 三个目标 UI 资源发生变化，其余 93 个逐字节不变。CZ3/CZ4 图片执行 PNG → CZ → PNG 往返后像素一致。

ExeFS IPS 针对未压缩 NSO 制作。v38 补丁共 154 个差分记录，应用到原始未压缩 `main` 后与目标 NSO 字节级一致；三个短字符串的旧地址引用归零，新地址引用数量与预期一致。

严重串行风险采用固定随机种子 `202609112310`，从 4573 个最终正文槽中不放回随机抽查 650 条。观察到严重串行 0/650；按单侧 95% 置信标准，零失效上限约为 0.4598%，满足 `< 0.5%` 的项目验收条件。详见 `CLANNAD外传汉化历史文件/docs/串行概率统计抽查报告_v38.md`。

## 仓库结构

```text
.
├─ README.md
├─ GITHUB_BACKUP.md
├─ 汉化补丁/
│  └─ 09_release/v38/          # 当前可安装 LayeredFS 测试补丁
└─ CLANNAD外传汉化历史文件/
   ├─ docs/                    # 项目状态、安装、贡献、复现与统计报告
   ├─ scripts/                 # 关键构建与验证脚本
   └─ audit/                   # v38 随机抽样审计数据
```

## 贡献与来源

- 原作及相关权利：Key / VisualArts 及相应权利方。
- Nintendo Switch 版本相关：Prototype 及相应权利方。
- PC 中文译文来源：本地既有《CLANNAD 被光守望着的坡道》中文补丁。现有本地材料不足以可靠恢复该补丁的汉化组/成员署名，因此本仓库不猜测或杜撰姓名。
- Switch 移植汉化、资源分析、构建与项目维护：**ALTIRKIE**。
- 工具：LuckSystem（wetor）、RLDev 相关工具链。
- AI 辅助：OpenAI ChatGPT / Codex，用于资源分析、脚本编写、验证与工程整理；PC 既有译文并非由 AI 重新翻译。

更完整说明见 `CLANNAD外传汉化历史文件/docs/03-贡献与署名.md`。

## 免责声明

本项目为非官方中文本地化研究与移植工程，与 Key、VisualArts、Prototype、Nintendo 等权利方无隶属或授权关系声明。

请自行合法持有并使用对应游戏版本。本仓库不提供游戏本体、密钥、破解材料或原始未修改游戏资源的下载。

v38-test 当前仍标记为测试版，因为尚需 Nintendo Switch 实机验收字体显示、菜单图层、按钮状态、章节推进与视觉换行。
