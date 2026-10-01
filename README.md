# 南京大学物理方向 · 师资检索 / NJU Physics Faculty Directory

一个自包含的网页，收录**南京大学物理相关四个院系 643 位教师/科研人员**，支持按院系、学科、关键词搜索与筛选。数据抓取于 2026-10-01，每条记录均链接到其官方个人主页。

**在线访问 / Live:** https://SZhang0314.github.io/nju-physics-directory/

## 覆盖范围 / Scope

| 学院 | 人数 |
|---|---|
| 物理学院（现代物理系 / 物理学系 / 光电科学系 / 声科学与工程系 / 基础物理教学中心 / 院直属） | 233 |
| 现代工程与应用科学学院 | 228 |
| 电子科学与工程学院 | 120 |
| 天文与空间科学学院 | 62 |
| **合计** | **643** |

其中 **303 人** 为深度信息（`confidence: fine`：职称、研究方向、简介、可得的邮箱/主页/代表作），
其余为名录级（`confidence: coarse`：姓名、院系、官方个人主页链接）。

## 数据来源 / Sources

- 物理学院：http://physics.nju.edu.cn/szdw/qbmd/axb/index.html
- 天文与空间科学学院：https://astronomy.nju.edu.cn/szll/szgk/index.html
- 电子科学与工程学院：http://ese.nju.edu.cn/30444/list.htm
- 现代工程与应用科学学院：https://eng.nju.edu.cn/qyml2/list.htm

每位教师记录中的 `sources` 字段列出实际使用的 URL，便于审计。

## 文件结构

```
nju-physics-directory/
├── data/
│   ├── faculty.json        # 数据源（source of truth）
│   └── raw/                # 官方页面抓取的原始名单与深度信息
├── scripts/
│   ├── assemble.py         # 由 raw/ 汇总生成 faculty.json
│   └── merge_enrich.py     # 将深度信息合并进 faculty.json
├── index.html              # 单文件可搜索网页（内嵌数据+样式+脚本）
├── README.md
└── .nojekyll
```

## 重新生成 / Regenerate

```bash
python scripts/assemble.py          # 重建粗筛名录
python scripts/merge_enrich.py      # 合并深度信息
python <search_prof>/scripts/build_site.py --data data/faculty.json --out .
```

## 说明 / Notes

- 页面为单文件，双击 `index.html` 即可离线打开，也可直接部署到 GitHub Pages。
- 数据来自公开的官方师资页面；未在页面上出现的信息（邮箱、主页、代表作）一律留空，未做任何臆测。
- `generated_at`：2026-10-01。
