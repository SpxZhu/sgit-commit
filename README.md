# sgit-commit

版本：1.0.0.1 · 原公开文档核验日期：2026-09-23

依据当前会话和 Git 差异生成提交主题及编号正文。确认范围、文案与四段版本计划后提交；另经确认，以 `v<version>` tag 推送并发布 Release。只预览时保持只读。

## 安装

### Codex

解压 `sgit-commit-codex.zip`，将整个 `sgit-commit` 文件夹放入以下一个位置：[1]

```text
跨项目：~/.agents/skills/sgit-commit/
单项目：<repo>/.agents/skills/sgit-commit/
```

Windows 中 `~` 指运行 Codex 的用户主目录，WSL 使用其 Linux 主目录。避免在同一宿主全局和项目重复安装同名技能，或覆盖自定义版本。

通过 `$sgit-commit` 调用。`agents/openai.yaml` 关闭隐式调用；更新未出现时重启 Codex。[1]

### Claude Code

解压 `sgit-commit-claude.zip`，将整个 `sgit-commit` 文件夹放入以下一个位置：[2]

```text
跨项目：~/.claude/skills/sgit-commit/
单项目：<repo>/.claude/skills/sgit-commit/
```

通过 `/sgit-commit` 调用。Claude Code 包增加 `disable-model-invocation: true`，核心正文与 Codex 包一致；仍在当前会话执行，不额外授予工具权限。[2]

这是本地技能目录包，并非 ChatGPT 插件或 claude.ai 上传格式。

## 使用

以下是自然语言调用示例：

默认提交及发布流程：

```text
$sgit-commit
```

仅预览已暂存改动：

```text
$sgit-commit 仅根据已暂存内容生成 message 和 description，不提交。
```

指定范围：

```text
$sgit-commit 提交本次会话对应的修改，不包含其他任务的改动。
```

Claude Code 将 `$sgit-commit` 换为 `/sgit-commit`。技能默认选择当前会话相关改动及必要的版本更新，区分已暂存、未暂存与未跟踪内容。提交前确认具体范围、版本计划及文案；最终索引有实质变化则重新确认。提交核验后另行确认发布计划。只预览时不请求提交确认；范围不清、索引混有范围外内容或项目门禁未通过时先处理阻塞。

## 版本与发布

每次由本技能执行的提交都包含项目版本更新，沿用权威来源及同步惯例。默认递增第四段（`1.2.3.4 → 1.2.3.5`）；指定提升较高位时右侧归零（`1.2.3.4 → 1.3.0.0`）；目标须高于已提交版本。已合规更新则不重复递增。来源、同步位置或格式不明时先确认方案；仅已暂存提交若需加入版本改动，先确认扩大范围。

默认发布前核对上游远程、平台及同名 tag。提交后展示附注 tag、远程和 Release 内容；确认后才推送并发布。Release 默认用 `v<version>` 作标题、已核验提交文案作说明，类型为正式版。明确仅本地提交则跳过发布；失败时保留现场并报告进度。本技能只约束自身执行的提交。

## 输出

`message` 是主题，`description` 是编号正文；合并后作为完整 Git commit message，格式如下：[3]

```text
完善版本与发布流程

1. 提交时更新四段版本号，并将版本改动纳入同一提交。
2. 提交后单独确认 tag、推送及 Release 内容。
```

以上仅为格式示例，实际文案须对应差异。文本不含 `message`、`description` 标签或代码围栏；条数按实际改动决定。

## 文件分工

```text
sgit-commit/
├── SKILL.md              # 需求、证据、范围、文案与确认规则
├── references/
│   └── commit.md         # 单独调用或要求提交时读取，规定版本、提交和发布流程
├── agents/
│   └── openai.yaml       # 仅 Codex 包包含，控制显式调用
└── README.md             # 人工安装和使用说明，不作为技能必读资料
```

发布需目标平台可用的认证工具／接口及权限；仓库门禁仍须满足。

编写参考 `writing-for-agents` 和 `SKILL-MECHANICS.md`，用于按分支读取和职责去重。[4][5]

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
