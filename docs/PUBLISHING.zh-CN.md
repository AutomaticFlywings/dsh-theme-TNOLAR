# GitHub 公开发布操作

## 仓库元信息

- **Owner**：`AutomaticFlywings`
- **仓库名称（大小写按要求）**：`dsh-theme-TNOLAR`
- **可见性**：Public
- **描述建议**：`DSH Web 战略指挥终端完整主题 + 世界网络启动动画（9 首都 / 14 条线路），支持 GitHub Bundle 安装。`
- **Topics 建议**：`dsh`、`dsh-plugin`、`deepseek-harness`、`theme`、`tnolar`、`startup-animation`、`web-ui`

## 方式一：先在 GitHub 建仓库，再上传

1. 打开 <https://github.com/new>，登录 `AutomaticFlywings`。
2. 输入 `dsh-theme-TNOLAR`，Visibility 选 **Public**。
3. 新建时建议不要勾选自动生成 README / License / .gitignore，因为本源码已包含这些文件。
4. 创建完成后，可以把仓库 URL 发给已连接 GitHub 的助理，让其上传文件；也可以在本地上传：

```bash
cd dsh-theme-TNOLAR
git init
git branch -M main
git add .
git commit -m "feat: publish TNOLAR DSH theme and startup bundle"
git remote add origin https://github.com/AutomaticFlywings/dsh-theme-TNOLAR.git
git push -u origin main
```

GitHub 不会自动解压作为单个文件上传的 ZIP，请解压后提交仓库根目录中的 `package.json`、`cordis.patch.yml`、`lib/`、`README.md` 等文件。

## 方式二：若本地已安装 gh CLI

登录：

```bash
gh auth login
```

在源码根目录运行：

```bash
git init
git branch -M main
git add .
git commit -m "feat: publish TNOLAR DSH theme and startup bundle"
gh repo create AutomaticFlywings/dsh-theme-TNOLAR --public --source=. --remote=origin --push --description "DSH Web 冷战终端风格主题与全球首都网络启动动画"
```

## 发布后验证

打开 <https://github.com/AutomaticFlywings/dsh-theme-TNOLAR>，确认 README、`package.json`、`cordis.patch.yml` 和 `lib/client.js` 均可见。然后运行：

```bash
dsh plugin --profile web add "github:AutomaticFlywings/dsh-theme-TNOLAR#main"
dsh --profile web --dump-config
```

完成后重启 DSH Web，并在测试 profile 中检查：动画可以跳过、页面恢复可交互、主题不会破坏聊天输入和会话列表。

## 维护建议

1. 每次修改 `assets/world-startup.html`、`src/tnolar-theme.css` 或 `src/client.template.js` 后，执行 `npm run build && npm run check && npm test`。
2. `lib/client.js` 必须一起提交（Git 安装不会自动运行 build）。
3. 发布新版本时修改 `package.json` 中 `version`，并标记 Git tag，例如 `v0.4.0`。
4. 为其他用户提供固定 commit 的安装命令，避免未经核对的分支更新影响运行环境。