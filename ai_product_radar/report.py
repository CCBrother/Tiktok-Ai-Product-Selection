from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date
from pathlib import Path

from .models import ProductSignal, ScoreBreakdown
from .scoring import decide_product, score_product


ScoredProduct = tuple[ProductSignal, ScoreBreakdown]


def build_rankings(products: list[ProductSignal]) -> dict[str, list[ScoredProduct]]:
    scored = [(product, score_product(product)) for product in products]
    return {
        "top_20_high_potential": sorted(scored, key=lambda item: item[1].ai_score, reverse=True)[:20],
        "blue_ocean": sorted(scored, key=lambda item: item[1].blue_ocean_score, reverse=True)[:20],
        "fast_growth": sorted(scored, key=lambda item: item[1].growth_score, reverse=True)[:20],
        "easy_to_copy": sorted(scored, key=lambda item: item[1].easy_copy_score, reverse=True)[:20],
        "high_profit": sorted(scored, key=lambda item: item[1].profit_score, reverse=True)[:20],
    }


def render_markdown(rankings: dict[str, list[ScoredProduct]], report_date: date) -> str:
    sections = [
        ("前20名高潜力产品", "top_20_high_potential", "ai_score"),
        ("蓝海产品", "blue_ocean", "blue_ocean_score"),
        ("快速增长产品", "fast_growth", "growth_score"),
        ("易复制产品", "easy_to_copy", "easy_copy_score"),
        ("高利润产品", "high_profit", "profit_score"),
    ]

    lines = [
        f"# AI产品雷达日报 - {report_date.isoformat()}",
        "",
        "目标：发现未来 7 到 30 天内可能在美国 TikTok Shop 走红的产品。",
        "",
        "说明：AI评分不是市场规模评分，而是短期病毒传播潜力评分。",
        "",
    ]

    for title, key, score_attr in sections:
        lines.extend([f"## {title}", ""])
        lines.extend(render_table(rankings[key], score_attr))
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def render_table(items: list[ScoredProduct], score_attr: str) -> list[str]:
    lines = [
        "| 排名 | 产品 | 类目 | AI评分 | 分项分 | 说明 |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for index, (product, score) in enumerate(items, start=1):
        focus_score = getattr(score, score_attr)
        score_text = f"{score.ai_score}/100"
        if score_attr != "ai_score":
            score_text = f"{focus_score}/100（总分 {score.ai_score}）"
        detail = (
            f"增长 {score.growth_score} / 趋势 {score.trend_score} / 竞争 {score.competition_score} / "
            f"利润 {score.profit_score} / 内容 {score.content_score} / 病毒 {score.viral_score}"
        )
        lines.append(
            "| {rank} | {name} | {category} | {score_text} | {detail} | {explanation} |".format(
                rank=index,
                name=escape_md(product.product_name),
                category=escape_md(product.category),
                score_text=score_text,
                detail=detail,
                explanation=escape_md(score.explanation),
            )
        )
    return lines


def rankings_to_json(rankings: dict[str, list[ScoredProduct]], report_date: date) -> str:
    payload = {
        "report_date": report_date.isoformat(),
        "principle": "Focus on 7-30 day viral potential, not complete market coverage.",
        "rankings": {
            key: [
                {
                    "product": asdict(product) | {
                        "gross_margin_pct": round(product.gross_margin_pct, 2),
                        "landed_profit_usd": round(product.landed_profit_usd, 2),
                    },
                    "score": asdict(score),
                    "decision": asdict(decide_product(product, score)),
                }
                for product, score in items
            ]
            for key, items in rankings.items()
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def write_reports(products: list[ProductSignal], output_dir: Path, report_date: date) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rankings = build_rankings(products)

    md_path = output_dir / f"radar_{report_date.isoformat()}.md"
    json_path = output_dir / f"radar_{report_date.isoformat()}.json"
    md_path.write_text(render_markdown(rankings, report_date), encoding="utf-8")
    json_path.write_text(rankings_to_json(rankings, report_date), encoding="utf-8")
    return md_path, json_path


def escape_md(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
