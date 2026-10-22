# academic-less-ai-tone

中文学术润色技能，适用于论文、研究报告、学术讲座逐字稿及配套幻灯片。当前版本为 **V24（2026-10-22）**。

一次调用完成事实与论证核对、完整句群改写、语气审读和交付核验。默认交付可直接使用的正文或实际修改的文件。规则和示例随包提供，写作润色无需另行调用风格技能。

## 使用

提供原稿、用途与可核实资料，指定`$academic-less-ai-tone`。已有读者、人称、篇幅、提纲和讲者样稿直接采用。

> 请使用 $academic-less-ai-tone 润色这份面向社科研究生的讲座逐字稿及配套slides。核对数字、方法和结论，沿用现有提纲，采用自然、专业的讲述语气，实际更新两份文件并核验对应关系。

> 请使用 $academic-less-ai-tone 润色论文讨论段。所附事实卡为本次依据；保留引文、作者解释、比较基准与必要限定，交付完整修订正文。

清楚自然的原句少改。专业术语、真实争论、操作定义、自然设问和直接引语按其功能保留。用户指定的禁用句式与编辑范围优先执行。

## V24更新

- 明确连续编辑流程：核内容、改句群、审语气、核交付。正文反查与核验说明分别校对。
- 增加讲述与幻灯片规则，处理理解顺序、刻意口语、无据经历、方法衔接、页间对应及时间估算。
- 增加成稿表达审读，逐处处理提示壳、虚设反转、重复骨架、抽象总结和拟人夸饰，同时保留有效表达。
- V23事实保全细则随包保留，增加完整无据主张的删除与系数尺度核验要求。
- 入口按任务引导读取细则，增加Codex显示名称和默认提示；调用名保持`academic-less-ai-tone`。

## 安装与升级

从[GitHub Releases](https://github.com/LeoAndJellyfish/academic-less-ai-tone/releases)下载对应版本ZIP，校验SHA-256后，将其中`academic-less-ai-tone`目录安装到助手的技能目录。升级前备份现有同名目录。一个发现路径保留一份当前版本，历史备份另存。

Codex可使用`~/.agents/skills/academic-less-ai-tone`或其配置的`$CODEX_HOME/skills/academic-less-ai-tone`。入口为[SKILL.md](SKILL.md)。新安装的技能通常在下一轮对话加载。

## 文件与核验

- [主张核对与信息保全](references/evidence-and-preservation.md)：对象、数值、比较方向、范围与引文。
- [讲述与幻灯片](references/lecture-and-slides.md)：口头语气、技术解释、配套文件与时长。
- [成稿表达审读](references/final-style-review.md)：第二遍完整段落审读及保留条件。
- [句群示例](references/retained-rewrite-examples.md)、[任务适配示例](references/task-fit-style-examples.md)：具体删改与保留情境。
- [研究与验证记录](references/research-basis.md)：版本、方法、已完成检查及适用范围。

两个Python辅助脚本沿用V23，使用标准库。`scripts/claim_preflight.py`帮助定位来源外候选和信息遗漏；编辑者根据完整语句与资料裁决。`scripts/measure_body.py`按明确区间统计修订正文汉字数。

```json
{
  "source": "研究记录：甲组20人，乙组18人；两组分别完成同一任务。",
  "draft": "研究比较了两组受试者。",
  "revision": "研究比较了甲组20人与乙组18人在同一任务中的表现。"
}
```

```bash
python scripts/claim_preflight.py --input input.json --strict
python scripts/measure_body.py --input input.json --min 10 --max 80
```

脚本输出候选信息。程序检查、完整正文审读、模型试写和真人评价分别报告。本轮开发包含本地小模型试写，其残留错误已登记；评价范围见研究记录。

## 历史开发结果

以下保留V21开发记录，各项结果按对应版本解释。

## V21 开发评估

最终多领域复测采用六个来源，每个来源重复两次，比较 V21、无技能、lieflat 与 humanizer 四种条件，共 48 份终稿。两名独立 AI 辅助评审按预设量表评分。主要终点要求信息保真、保留句群改写、推断边界、格式及实测篇幅均达标；严格终点增加段落连贯性和具体表达评分。

| 条件 | 两评审共同主要通过 | 两评审共同严格通过 |
| --- | ---: | ---: |
| V21 | 10/12 | 10/12 |
| 无技能 | 8/12 | 6/12 |
| lieflat | 8/12 | 8/12 |
| humanizer | 4/12 | 4/12 |

解盲后的较宽指代恢复口径下，无技能组主要通过为 10/12，与 V21 相同；严格通过为 8/12。此项为事后敏感性分析。测试使用构造稿和固定事实卡，独立来源数为六，实际真人评分为零；结果用于说明开发过程中的具体表现。原始受限材料与本地评分包未收入仓库。

## 版本与文件

当前技能文件的 SHA-256 见 [`SHA256SUMS`](SHA256SUMS)，安装包按 GitHub Releases 的版本标签提供。V23、V22与V21封存版本保留在 [v22 标签](https://github.com/LeoAndJellyfish/academic-less-ai-tone/tree/v22)、[v21 标签](https://github.com/LeoAndJellyfish/academic-less-ai-tone/tree/v21)及各自的发布附件中。`references/research-basis.md` 的历史记录按当时版本解释，外部技能的研究记录按文档名称索引。

代码和原创文档按 [MIT License](LICENSE) 发布。引用或复用外部研究资料时，遵守其各自的许可与引文要求。
