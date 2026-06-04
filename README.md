# Bazaar DB 中文资料库

面向 The Bazaar 玩家的微信小程序资料库。项目会同步 Bazaar DB 的公开资料，整理为中文卡牌数据，并在小程序内提供搜索、分类、筛选和详情查看能力。

当前数据版本：`15.0 (Jun 3)`

## 功能

- 中文资料查询：物品、技能、商人、训练师、怪物、事件
- 卡牌搜索：支持名称、英雄、稀有度、标签、效果和获取来源关键词
- 高级筛选：按英雄、稀有度、尺寸和标签收窄结果
- 卡牌详情：展示图片、效果、机制标签、来源、怪物和事件详情
- 远程图片：使用 Bazaar DB 图片 URL，减少小程序代码包体
- 数据同步脚本：通过 `scripts/sync_bazaar_db.py` 更新本地数据文件

## 数据规模

| 分类 | 数量 |
| --- | ---: |
| 全部 | 1792 |
| 物品 | 1086 |
| 技能 | 448 |
| 商人 | 47 |
| 训练师 | 23 |
| 怪物 | 139 |
| 事件 | 49 |

数据文件位于：

```text
miniprogram/data/bazaarData.js
```

## 项目结构

```text
miniprogram/
  app.json
  app.js
  app.wxss
  data/bazaarData.js
  pages/index/
    index.js
    index.json
    index.wxml
    index.wxss
scripts/
  sync_bazaar_db.py
```

## 本地开发

1. 使用微信开发者工具打开本目录。
2. 确认 `project.config.json` 中的 AppID 是目标小程序 AppID。
3. 在微信开发者工具中预览或真机调试。
4. 若图片无法显示，需要在小程序后台配置服务器域名：

```text
https://s.bazaardb.gg
```

## 同步数据

同步脚本会抓取 Bazaar DB 页面、清洗字段、补充中文翻译，并更新 `miniprogram/data/bazaarData.js`。

```bash
python3 scripts/sync_bazaar_db.py
```

同步后建议检查：

```bash
node -e "const data=require('./miniprogram/data/bazaarData'); console.log(data.patch, data.cards.length)"
du -sh miniprogram
git diff --check
```

## 仓库约定

- GitHub 仓库用于对外开放协作和修改。
- 微信 Git 仓库用于受保护的发布版本。
- 提交到微信仓库前，请先确认小程序包体、真机调试和发布配置。

## 说明

本项目是社区资料查询工具，数据与图片来源于 Bazaar DB 公开页面。项目不会把远程图片下载进小程序包体，避免超过微信小程序代码包大小限制。
