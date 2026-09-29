# sgit-commit

版本：1.0.0 · 制作及公开文档核验日期：2026-09-23

把当前会话中的需求和实际 Git 差异归纳为一个提交主题，以及按功能编号的修改列表。调用时先展示文案和候选范围，待用户明确确认后执行本地提交；明确要求只预览时停在文案阶段。不会推送远程。

## 安装

### Codex

解压 `sgit-commit-codex.zip`，将整个 `sgit-commit` 文件夹放入以下一个位置：[1]

```text
跨项目：~/.agents/skills/sgit-commit/
单项目：<repo>/.agents/skills/sgit-commit/
```

Windows 中 `~` 是实际运行 Codex 的用户主目录，例如 `C:\Users\root\.agents\skills\sgit-commit\`；WSL 则使用其 Linux 用户目录。不要同一宿主全局和项目重复安装同名技能，也不要直接覆盖已有同名自定义版本。

通过 `$sgit-commit` 调用。包内 `agents/openai.yaml` 设置了 `policy.allow_implicit_invocation: false`，关闭隐式调用，不影响显式调用；更新未出现时重启 Codex。[1]

### Claude Code

解压 `sgit-commit-claude.zip`，将整个 `sgit-commit` 文件夹放入以下一个位置：[2]

```text
跨项目：~/.claude/skills/sgit-commit/
单项目：<repo>/.claude/skills/sgit-commit/
```

通过 `/sgit-commit` 调用。该版本只增加宿主专用的 `disable-model-invocation: true`，核心正文与 Codex 版本一致；未配置 `context: fork`，保持当前会话内执行。没有授予 `allowed-tools` 额外权限，也不覆盖宿主权限设置。[2]

这是本地技能目录包，不是 ChatGPT 插件安装包或 claude.ai 上传格式。未连接或修改你的实际 Codex／Claude Code 安装。

## 使用

以下内容是传给技能的自然语言指令，不是额外安装的命令行程序或固定参数解析器。

生成本次会话相关改动的文案，确认后提交：

```text
$sgit-commit
```

只查看已暂存内容，不混入同一文件的未暂存修改，也不提交：

```text
$sgit-commit 仅根据已暂存内容生成 message 和 description，不提交。
```

指定提交范围并在确认后执行本地提交：

```text
$sgit-commit 提交本次会话对应的修改，不包含其他任务的改动，不推送。
```

Claude Code 将上述 `$sgit-commit` 换为 `/sgit-commit`。单独调用或提出提交请求，都会先得到候选范围、`message` 和 `description`；确认这份具体内容后，技能才会暂存并提交。即使最初要求“直接提交”，也需等待这次确认；明确只预览时不会请求提交确认。修改文案或范围后，会重新展示完整候选内容并等待确认。范围不清、暂存区混有范围外内容、未通过强制门禁等情况仍需处理。

默认候选范围是当前会话相关的未提交改动，包含需要核对的已暂存、未暂存及未跟踪文件，不是默认提交整个仓库。确认后以实际索引重新核对文案；若范围或文案出现实质变化，须重新展示并等待确认。

## 输出

`message` 表示主题，`description` 表示正文。两者合并在一个文本块中展示：首行是主题，空行后是编号正文。这份文本也是提交给 Git 的完整 commit message；并不存在独立的 `git commit --description` 参数。[3]

以下仅是格式示例：**假设对应差异已实现并包含在所选快照中，不表示你的 SDK 已经完成这些修改。**

```text
重做 SDK 工具界面并统一广告模式与本地化体验

1. 参照 wzgSDK 重做环境选择与调试界面，并在同风格扩展页保留现有调试功能。
2. 复用参考本地化配置，补齐业务界面的日语支持并保留工具界面中文原文。
3. 统一 SDK 界面和弹窗的字体配置，使用允许免费商用及随包分发的字体资源。
4. 增加真实广告与模拟广告切换，开发模式及正式测试身份默认模拟广告且允许切换真实广告。
5. 正式非测试身份固定使用真实广告，广告切换不改变服务器环境或账号身份。
```

展示时不附加 `message`、`description` 标签；提交给 Git 的文本与块内内容一致，不含代码围栏。

列表没有固定条数：一项变化只写一项，多项独立功能不因追求简短而省略。没有仓库规定时默认使用中文主题，不强制 Conventional Commits 前缀。仅修改文档时应描述文档改动，不写成代码功能已实现。

## 文件分工

```text
sgit-commit/
├── SKILL.md              # 需求、证据、范围、文案与确认规则
├── references/
│   └── commit.md         # 单独调用或要求提交时读取，规定确认后的执行
├── agents/
│   └── openai.yaml       # 仅 Codex 包包含，控制显式调用
└── README.md             # 人工安装和使用说明，不作为技能必读资料
```

没有新增脚本、MCP、全局 AGENTS.md 内容或运行时技能依赖。明确只预览时无需加载提交执行分支；技能不默认触发全量测试、开发流程或额外 Agent。仓库已有的强制门禁仍须满足。

编写时参考并读取了公开上游 `writing-for-agents` 及 `SKILL-MECHANICS.md`，用于分支按需读取、明确完成条件和职责去重；未取得你本机 `writing-for-agent` 的定制版本，不声称两者一致。没有复制或重新分发其技能正文。[4][5]

## 验证范围

具体检查结果见同批交付的 `sgit-commit-validation.md`。静态结构与临时仓库中的 Git 行为测试，不等于真实 Codex／Claude Code 的技能发现、触发或端到端行为测试。未读取你的项目实时 diff，未暂存或提交你的项目。

## 核对来源

[1] OpenAI：Build skills；本地目录、显式调用、`agents/openai.yaml`。
`https://developers.openai.com/codex/skills`

[2] Anthropic：Claude Code Skills；本地目录、调用及宿主扩展字段。
`https://code.claude.com/docs/en/skills`

[3] Git 官方：git-commit；完整消息格式、`-F`、暂存区与路径参数语义。
`https://git-scm.com/docs/git-commit`

[4] Matt Pocock：writing-for-agents，公开上游。
`https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/writing-for-agents/SKILL.md`

[5] Matt Pocock：SKILL-MECHANICS.md，公开上游。
`https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/writing-for-agents/SKILL-MECHANICS.md`
