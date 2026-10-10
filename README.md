# Repo 体检 · Repo Checkup

给任意 GitHub 仓库打一个总分，告诉你**哪里烂、怎么改**。

纯本地运行，不联网上传你的代码，只读公开仓库元数据。

```
Score 100/100  ·  A  ·  psf/requests
六维：活跃度 / 社区热度 / 文档完善 / 工程规范 / Issue 健康度 / 许可证风险
```

免费本地版已上架 SkillHub，可直接安装：
<https://skillhub.cn/skills/@user_2dd60efe/repo-checkup-free>

---

## 六个维度怎么打分

| 维度 | 看什么 | 权重 |
|---|---|---|
| 活跃度 | 近 90 天提交频率、最近一次提交距今 | 25 |
| 社区热度 | star / fork / watcher、贡献者数量 | 25 |
| 文档完善 | README 长度、是否含安装与示例 | 20 |
| 工程规范 | LICENSE、CI 配置、贡献指南 | 20 |
| Issue 健康度 | 关闭率、未处理积压 | 10 |
| 许可证风险 | OSI 许可分级 + 与项目类型的适配提示 | 附加项 |

许可证单独分级是因为它不是「减分项」而是「风险项」——GPL-3.0 用在闭源商业项目里、
AGPL-3.0 触发网络开源义务，这两种情况对团队是实质风险，但仓库本身不该因此拿低分。

---

## 免费版怎么用（本地跑）

```bash
git clone https://github.com/shaimoon8800-ai/repo-checkup-free
cd repo-checkup-free
python3 scripts/repo_checkup_cli.py psf/requests      # 人读格式
python3 scripts/repo_checkup_cli.py psf/requests --json  # JSON 输出
```

只依赖 Python 标准库，无第三方依赖。

---

## 进阶能力（按量计费）

免费版覆盖的是**单仓库、纯本地、给人看**的场景。如果你的用法命中下面任一条，
有一个按调用次数计费的托管版本：

- 需要**批量**体检（一次扫几十上百个仓库）
- 需要 **API 化**，接进 CI / 定时任务 / 内部看板
- 需要**结构化报告**（JSON / 报告文件导出），而不是终端文本
- 需要**更长文本分析**与定制化评分权重

**付费版入口**

- 我的公开货架（9 个在售，一次逛完）：<https://skillpay.alipay.com/public/shaiyueliang>
- 直达本商品：<https://skillpay.alipay.com/shelf/product?productId=P0806000208825323&merchantCode=shaiyueliang>

| 商品 | 平台 | 价格 | 购买 |
|---|---|---|---|
| Repo 体检 · 买断制 | 支付宝 SkillPay | ¥0.05 / 次 | 上方链接 |
| Repo 体检 · 按次付费 | SkillHub Pay Skill | 平台内计费 | SkillHub 站内 |

SkillHub 内的按次付费版本同步在架，交易走平台内支付。

> 本地版与付费版的能力边界、评分口径完全一致，付费版只是把「批量 / API / 导出」
> 这三件事挪到服务端，评分逻辑不缩水。

---

## 数据与隐私

- 只读取 GitHub **公开**仓库元数据（commit / issues / license / README 等）
- 不上传、不克隆、不存储你的代码内容
- 不需要 GitHub Token 即可运行

---

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE)。