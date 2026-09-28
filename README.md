# academic-less-ai-tone

面向中文学术论文、研究报告、学术讲座及技术论坛稿的写作编辑技能。V21 版本先核对主张和证据，再修订有据但程式化的句群，最后检查对象、比较方向、限定、数值归属、引文和完整段落的衔接。

该技能适用于新稿审查和已有稿件改写。用户提出改写要求时，主要交付物为可直接使用的修订正文；需要作者核实的事实另列。

## 安装

将仓库克隆到 Codex 的技能目录：

```bash
git clone https://github.com/LeoAndJellyfish/academic-less-ai-tone.git ~/.codex/skills/academic-less-ai-tone
```

Windows PowerShell 示例：

```powershell
git clone https://github.com/LeoAndJellyfish/academic-less-ai-tone.git "$env:USERPROFILE\.codex\skills\academic-less-ai-tone"
```

现有同名目录应先自行保留，再安装本仓库。技能入口为 [`SKILL.md`](SKILL.md)；补充示例与研究依据位于 `references/`。两个辅助脚本使用 Python 标准库。

## 使用

向写作助手提供原稿、目标体裁、篇幅及可核实的事实卡或文献摘录，并指定使用 `academic-less-ai-tone`。例如：

> 请按 academic-less-ai-tone 修订以下讨论段。事实卡是本次改写的依据。保留比较方向、统计口径、作者解释和引用；交付完整修订段落，待核事实另列。

技能按段落处理证据和表达。它审查空泛的转向、重复提示语、归属提示连用、生硬名词化及跨句指代，同时保留真实争论、操作定义和必要的统计限定。

### 辅助脚本

`scripts/claim_preflight.py` 接受 UTF-8 JSON 文件，其中 `source`、`draft` 和 `revision` 均为字符串，`revision` 仅填写修订正文：

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

预检输出定位需要核查的主张和表达；编辑者依据原资料裁决。篇幅脚本统计 `revision` 字段中的汉字。`--strict` 遇到部分来源外候选时返回状态码 2；篇幅超出指定区间时，篇幅脚本也返回状态码 2。

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

本仓库的五个技能文件逐字节保留最终封存的 V21 内容。各文件 SHA-256 见 [`SHA256SUMS`](SHA256SUMS)。`references/research-basis.md` 保留开发时的历史记录，其中一个本地路径仅作为来源线索，外部安装无需访问该路径。

代码和原创文档按 [MIT License](LICENSE) 发布。引用或复用外部研究资料时，遵守其各自的许可与引文要求。
