# GitHub 备份说明

仓库：`heruixii/clannad-side-stories-switch`

## 克隆备份

```powershell
git clone https://github.com/heruixii/clannad-side-stories-switch.git
```

## 更新仓库

```powershell
git add -A
git commit -m "update localization"
git push origin main
```

## Release 资产

Git 仓库保存工程快照与 `汉化补丁/09_release/`；GitHub Release 另外附带可直接复制到 SD 卡的 ZIP 和 SHA256 校验文件。

当前测试版资产：

- `CLANNAD_Side_Stories_CHS_v38_test.zip`
- `CLANNAD_Side_Stories_CHS_v38_test.zip.sha256.txt`

## 不应备份到公开仓库的内容

不要提交：

- `prod.keys` / `title.keys`
- XCI / NSP / NCA / ticket / certificate
- 原始 RomFS / ExeFS
- PC 游戏完整目录和可执行文件
- 用户存档
- GitHub token、ngrok token 或其他认证信息

公开仓库只保留本项目需要的补丁、脚本、文档和质量审计资料。
