# CLANNAD Side Stories Nintendo Switch 简体中文汉化

《CLANNAD 光見守る坂道で / CLANNAD Side Stories / 被光守望着的坡道》Nintendo Switch 简体中文汉化移植工程。

本仓库保存可安装补丁、关键构建/验证脚本、阶段记录与质量审计资料。**不包含游戏本体、XCI/NSP/NCA、密钥、原始 RomFS 或存档。**

## 当前状态

当前公开测试版本：**v39-test（字形修复版）**

状态标记：`V39_GLYPH_FALLBACK_SUBSTITUTION_READY`

| 项目 | 状态 |
| --- | --- |
| Title ID | `01007B501372C000`（**外传 Side Stories**；`0100A3A00CC7E000` 是正传 CLANNAD，勿混用） |
| 正文 | 4573 / 4573 已中文化 |
| 标题 | 97 / 97 已中文化 |
| 历史截断 | 336 / 336 已消除 |
| 图片 UI | 3 个确认含英文文字的资源已中文化（v38 起） |
| 主程序 UI | 145 条原位中文化（v38 起） |
| **实机缺字（空白字）** | **v39 修复：782 个缺字形 → 0** |
| 实机验收 | 正文显示已通过；菜单图层/换行仍待继续观察 |

## v39 修的是什么

v38 的正文虽然全部汉化，但游戏自带 `FONT.PAK` 每个字体面只有 **7188 个字形**，字符集是日文 JIS X 0208。简体专用字（这、说、时、们、你、她、吧、吗、嗯……）没有字形，实机渲染为**空白**，表现为句子中间一个个空洞。v38 文档里「原游戏字库具备所需 CJK 覆盖」的结论与实机不符。

实测（v38 的 `SCRIPT.PAK`，5118 个文本块 / 2272 个字符 / 59120 个字次）：

| 指标 | 数值 |
| --- | --- |
| 不在 JIS X 0208 的字符 | **782 个** |
| 出现次数 | **12,993 次（21.98%）** |
| 至少缺一个字形的行 | **4288 / 5118（83.8%）** |

v39 的做法：不改字库、不改主程序、不改容器结构，只做**等长 1:1 字形替换**——把字库没有的字，换成字库里确实存在、语义/形体尽量等价的字（手工表 248 字 + 繁体/JIS 自动映射 355 字 + 兜底 80 字），共替换 **11,121** 字，`SCRIPT.PAK` 仍是 **791,212 字节**，容器头/条目表/字节码全部未动。替换后正文 **100% 落在 JIS 内**，实机不再出现空白字。

代价：文体变成「繁体 + 日式汉字」，语气词被替换成顿号，少量词级别扭（`办公室 → 弁公室`）。详见 `汉化补丁/10_release/v39_glyphfix/README.md`。

## 安装（全新）

推荐直接从 GitHub Releases 下载 `CLANNAD_Side_Stories_CHS_v39_glyphfix.zip`。

1. 确认游戏 Title ID 为 `01007B501372C000`。
2. 解压补丁。
3. 把其中的 `atmosphere` 文件夹复制到 SD 卡根目录并合并。
4. **完全退出游戏**后重新启动（Home → X → 关闭，或重启机器）。

v39 的目录结构：

```text
atmosphere/
└─ contents/
   └─ 01007B501372C000/
      └─ romfs/
         └─ SCRIPT.PAK        # 791,212 B，d8e47bf1…2ec973a
```

## 从 v38 升级：卸载旧补丁 → 安装新补丁

v38 和 v39 覆盖的是同一个文件 `SCRIPT.PAK`，**不要直接把 v39 的文件丢进 v38 的目录了事**，按下面顺序做，能保证回到干净状态：

### 第一步：卸载旧补丁（v38）

在 PC 上打开 SD 卡根目录，删除下面这些 v38 的东西：

```text
SD:/atmosphere/contents/01007b501372c000/          ← 整个目录删掉（v38 的 SCRIPT.PAK + PARTS.PAK）
SD:/atmosphere/exefs_patches/CLANNAD_Side_Stories_CHS/   ← 整个目录删掉（v38 的 ExeFS IPS）
```

只想保留 v38 的 UI 图片汉化、只换正文的话，可以**只删一个文件**：

```text
SD:/atmosphere/contents/01007b501372c000/romfs/SCRIPT.PAK    ← 只删这个
```

（`PARTS.PAK` 与 v39 的 `SCRIPT.PAK` 可以共存，互不冲突。）

### 第二步：安装新补丁（v39）

```text
1) 解压 CLANNAD_Side_Stories_CHS_v39_glyphfix.zip
2) 把里面 atmosphere 文件夹整体复制到 SD 卡根目录，选择「合并/覆盖」
3) 确认最终路径存在且大小正确：
   SD:/atmosphere/contents/01007B501372C000/romfs/SCRIPT.PAK      791,212 字节
4) 完全退出游戏（Home → 光标停在游戏上 → X → 关闭），或直接重启机器
5) 启动 CLANNAD Side Stories，首句应为「今早，我成為了一名三年級学生。」
```

### 第三步：验收

- 首句出现 `今早，我成為了一名三年級学生。` → v39 生效
- 仍是日文假名 → 没读到补丁（Title ID 不对 / 目录层级错了 / 游戏没完全退出），对照上面的路径重来
- 出现空白字 → 装回去的还是 v38 的 `SCRIPT.PAK`，核对第 3 步的字节数

### 想退回 v38

删掉 `SD:/atmosphere/contents/01007B501372C000/romfs/SCRIPT.PAK`，把 v38 包里的同名文件复制回原位即可（v38 的 `SHA256SUMS.txt` 可用于核对）。

## 卸载 / 回滚（完全移除）

```text
删除 SD:/atmosphere/contents/01007B501372C000/                 （正文 + UI 图片）
删除 SD:/atmosphere/exefs_patches/CLANNAD_Side_Stories_CHS/    （主程序字符串补丁，如装过）
```

游戏本体不会被修改，删完即恢复原版。

## 质量验证

v39 正文：`SCRIPT.PAK` 长度保持 791,212 字节；容器头、230/452 条目表、名字表、字节码逐字节未变；替换后正文的 JIS 覆盖率 100%（`missing 0`）。校验值：

```text
SCRIPT.PAK  791,212 B
SHA256      d8e47bf110ed81fbbca52fb6ca9c3cbaef858e66bedd2ba2719189a9b2ec973a
```

v38 阶段的质量数据（正文槽、标题、截断、串行抽查、PARTS.PAK 重建、ExeFS IPS 差分）保持不变，详见下文与 `CLANNAD外传汉化历史文件/docs/`。

历史截断、串行抽查等结论：

- `PARTS.PAK` 重建前后均为 8,534,016 字节，96 个子文件中仅 `CONFIG_BG_EN`、`CONFIG_TAB_EN`、`system_menu_en` 三处变化。
- ExeFS IPS 共 154 个差分记录，应用到原始未压缩 `main` 后与目标 NSO 字节级一致。
- 串行风险抽查 0/650，单侧 95% 上限约 0.4598%。详见 `CLANNAD外传汉化历史文件/docs/串行概率统计抽查报告_v38.md`。

## 仓库结构

```text
.
├─ README.md
├─ GITHUB_BACKUP.md
├─ 汉化补丁/
│  ├─ 09_release/v38/          # v38 LayeredFS 测试补丁（历史版本）
│  └─ 10_release/v39_glyphfix/ # 当前可安装补丁（字形修复）
└─ CLANNAD外传汉化历史文件/
   ├─ docs/                    # 项目状态、安装、字形修复说明、贡献、复现与统计报告
   ├─ scripts/                 # 关键构建与验证脚本（含 build_glyph_subst.py）
   └─ audit/                   # v38 随机抽样审计数据
```

## 贡献与来源

- 原作及相关权利：Key / VisualArts 及相应权利方。
- Nintendo Switch 版本相关：Prototype 及相应权利方。
- PC 中文译文来源：本地既有《CLANNAD 被光守望着的坡道》中文补丁。现有本地材料不足以可靠恢复该补丁的汉化组/成员署名，因此本仓库不猜测或杜撰姓名。
- Switch 移植汉化、资源分析、构建与项目维护：**ALTIRKIE**。
- 工具：LuckSystem（wetor）、RLDev 相关工具链、opencc（v39 字形映射）。
- AI 辅助：OpenAI ChatGPT / Codex，用于资源分析、脚本编写、验证与工程整理；PC 既有译文并非由 AI 重新翻译。

更完整说明见 `CLANNAD外传汉化历史文件/docs/03-贡献与署名.md`。

## 免责声明

本项目为非官方中文本地化研究与移植工程，与 Key、VisualArts、Prototype、Nintendo 等权利方无隶属或授权关系声明。

请自行合法持有并使用对应游戏版本。本仓库不提供游戏本体、密钥、破解材料或原始未修改游戏资源的下载。

v39-test 已解决实机缺字问题，但「繁体/日式汉字」的文风与个别词级别扭仍属已知代价，后续可通过词级映射继续打磨。
