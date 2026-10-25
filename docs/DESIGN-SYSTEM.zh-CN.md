# TNOLAR UI 设计规范（v0.5.5）

本文件阐述主题针对 **DeepSeek Harness Web** 的视觉规则及风险边界。所有新增外观由 `src/tnolar-theme.css` 维护，不修改 DSH 宿主源码。

## 配色与层次

- 深色基底：`#06131B`；侧栏：`#071820`；一级面板：`#0B2029`；强交互表面：`#153B45`。
- 信号色：`#6BE5DA`，用于按钮焦点、激活状态、导航条及辅助信息，不用来替代警告或危险色。
- 主文字：`#E2F1ED`；次文字：`#AFCBCA`；辅助文字：`#87ABB0`。
- 危险状态 `#EE8187`，警告 `#DFB873`，独立于信号色。
- 背景网格：42px，低不透明度；面板保留深色底，避免干扰文字。

## 几何语言

- 小工具按钮：3–5px 角半径。一般按钮：8px。面板：11–14px。
- 会话当前态：青绿左侧细条 + 淡青色轮廓 + 小范围外发光。非当前行不画光条。
- 输入框：边框厚度 1px，聚焦时增强；左上/右下微型对角定位标记；发送按钮比输入区域更亮。
- 顶部工具条：横向渐变底板、底部一条高亮校准线；确保原生导航行为与拖拽区域不变。

## 针对真实 DSH 组件

下表中的名称依据 DSH 上游源码组件（2026-10）确认：

| 源文件/组件 | 本主题使用 |
|---|---|
| `ui-layout/AppFrame.module.css` | `.centerCol`、`.sidebarCol` 背景分层 |
| `ui-sidebar/SidebarRoot.module.css` | `.logoRow`、`.newSession`、`.panelRow` / `.panelActive` |
| `ui-workspace/rows/Rows.module.css` | `.sessionRow.selected`、`.projectRow` |
| `ui-workspace/rows/WorkspaceBrowser.module.css` | `.sectionHeader`、`.sectionLabel`、`.searchExpanded` |
| `ui-conversation/skeleton/ConversationRoot.module.css` | `.titleRow`、`.headerUtilities`、`.crumbCurrent`、`.tabActive` |
| `ui-conversation/skeleton/InputBar.module.css` | `.card`、`.primary`（`InputBar` 范围） |

DSH 使用 CSS Modules；本主题的辅助规则按类名包含的稳定组件标识匹配。若未来构建工具改变命名规则，**组件级增强可能失效**，但 `--dsw-*` token 层仍然可用。推荐维护者优先检查上游 DSH 变量契约，再检查选择器。

## 兼容性原则

1. 样式必须写在 `html[data-tnolar-theme="1"]` 作用域；关闭主题时立即移除样式与标记。
2. `--dsw-*` 是主接口，组件级选择器是渐进增强。不得用通配 `* { color: ... }` 覆盖内部 Markdown、用户插件与危险状态。
3. 只改外观，不拦截输入、不覆盖会话数据、不改 Shell / Electron 的窗口拖拽代码。
4. 降低动画时保持所有功能可用；焦点必须在键盘操作中可见。
5. 动画依旧由隔离 iframe 承载，主界面状态不与动画地图互通。

## 预览性质

`docs/preview-tnolar-theme.png` 使用 `test/fixture-dsh-mock.html` 生成，为模拟 DSH 页面。具体组件结构和主题变量为真实上游 DSH 代码参考，但**不代表实机的每个交互都已验证**。

## v0.5.5：代码和输入区颜色审计

- DSH 的 Markdown 行内代码使用 `--dsw-alias-markdown-inline-code`，与页面背景 token 独立；这里将它固定为 `#173641`，文字为 `#E0F8F2`。代码块 `--dsw-alias-markdown-code-block` 固定深色 `#0A2029`。
- Shiki 高亮使用单独的 `--shiki-token-*`，在浅色 profile + 强制深色 TNOLAR 主题组合中必须显式切换为深色语法配色，否则可能出现深色背景上的深色高亮文本。
- DSH 的 `InputBar.add` 为**命令菜单加号按钮**，不是文件上传 `<input>` 本身。使用深色 `#183E49` 底板和亮色轮廓，不覆盖 SVG 内部 `fill="none"`。发送按钮启用色为 `#185462`，禁用色为 `#113441`，禁用箭头清晰但弱于启用态。
- `ConversationRoot` 激活标签的横线由 `.tab::after` 绘制；主题不修改原始布局与点击区域，仅重配颜色。
- 浏览器组件回归使用 `test/fixture-theme-contrast.html` 和 `scripts/verify-contrast.py`，在模拟 DSH Light Token 残留场景下做 CSS 计算属性测量及前景背景对比度测试，截图见 `docs/preview-tnolar-contrast.png`。此测试**不是**真实 DSH 实机验证。