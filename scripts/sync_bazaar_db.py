#!/usr/bin/env python3

import json
import math
import re
import warnings
from copy import deepcopy
from pathlib import Path

import cloudscraper

warnings.filterwarnings("ignore", category=Warning)

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "miniprogram/data/bazaarData.js"

CATEGORY_LABELS = {
    "items": "物品",
    "skills": "技能",
    "merchants": "商人",
    "trainers": "训练师",
    "monsters": "怪物",
    "events": "事件",
}

HERO_CODES = {
    "Common": "通用",
    "Vanessa": "VAN",
    "Pygmalien": "PYG",
    "Dooley": "DOO",
    "Mak": "MAK",
    "Stelle": "STE",
    "Jules": "JUL",
    "Karnok": "KAR",
}

TIER_LABELS = {
    "Bronze": "青铜",
    "Silver": "白银",
    "Gold": "黄金",
    "Diamond": "钻石",
    "Legendary": "传奇",
}

TIER_CLASSES = {
    "Bronze": "bronze",
    "Silver": "silver",
    "Gold": "gold",
    "Diamond": "diamond",
    "Legendary": "legendary",
}

TIER_ORDER = ["Bronze", "Silver", "Gold", "Diamond", "Legendary"]

TAG_TRANSLATIONS = {
    "Aquatic": "水系",
    "Apparel": "服饰",
    "Burn": "灼烧",
    "Core": "核心",
    "Crit": "暴击",
    "Dinosaur": "恐龙",
    "Dragon": "巨龙",
    "Drone": "无人机（雄蜂）",
    "Food": "食物",
    "Friend": "伙伴",
    "Loot": "战利品",
    "Potion": "药水",
    "Property": "地产",
    "Ray": "射线（鳐）",
    "Reagent": "原料",
    "Relic": "遗物",
    "Shield": "护盾",
    "Slow": "减速",
    "Small": "小型",
    "Tech": "科技",
    "Toy": "玩具",
    "Trap": "陷阱",
    "Tool": "工具",
    "Vehicle": "载具",
    "Weapon": "武器",
    "Damage": "伤害",
    "Heal": "治疗",
    "Haste": "加速",
    "Poison": "剧毒",
    "Regen": "再生",
    "Freeze": "冻结",
    "Ammo": "弹药",
    "Merchant": "商人",
}

EXTRA_TITLE_TRANSLATIONS = {
    "Drone Crusher": "无人机粉碎机",
}

MECHANIC_MAP = {
    "ammo": "弹药",
    "burn": "灼烧",
    "charge": "充能",
    "crit": "暴击",
    "damage": "伤害",
    "flying": "飞行",
    "freeze": "冻结",
    "gold": "金币",
    "haste": "加速",
    "heal": "治疗",
    "health": "生命",
    "poison": "剧毒",
    "regen": "再生",
    "shield": "护盾",
    "slow": "减速",
}

ACCENTS = {
    "bronze": "#d8aa63",
    "silver": "#c7d3df",
    "gold": "#e2c15e",
    "diamond": "#6bc7ff",
    "legendary": "#ff9468",
}

NEW_CARD_TRANSLATIONS = {
    "qfg1929872wkv794199zd6mz44": {
        "name": "灼梭鱼",
        "effect": "灼烧 2 » 4 » 6 » 8 使一件相邻物品加速 1 秒",
    },
    "13jj00p8141sgwf9798tyt3lp8z": {
        "name": "狞猫",
        "effect": "按此物品拥有的类型数造成 5 » 10 » 20 » 40 伤害 使一件小型物品加速 1 秒 每天开始时，此物品获得一个随机类型",
    },
    "1653p2vxsd3st6sxdmzx681vmbm": {
        "name": "喷泉",
        "effect": "减速 1 » 2 » 3 件物品 2 秒 使你的治疗和再生物品充能 1 秒",
    },
    "gn8j12pp3qxxsbq3pjbcxv2b40": {
        "name": "劳蕾尔的弹力球",
        "effect": "使另外 2 件物品加速 1 » 2 秒 当此物品使相邻物品加速时，使此物品充能 1 秒",
    },
    "19dy50448vlbm3w80dpxzq7021": {
        "name": "内存分页模块",
        "effect": "当你触发减速、剧毒或冻结时，相邻物品获得 8 » 16 » 24 和 1 » 2 » 3",
    },
    "8kn50s4vyycdkwddc18x0j7cqz": {
        "name": "风龙",
        "effect": "一件物品开始飞行 当你使用巨龙或飞行物品时，使其加速 1 秒并造成 10 » 15 » 20 伤害",
    },
    "b02wz5y2yc8295c412lcpwyv": {
        "name": "疫怒",
        "effect": "当你进入暴怒时，你的物品在本场战斗中获得 +3 » +6 » +9 » +12",
    },
    "jd0xp11kjply36cslx24pdz3yb": {
        "name": "燃刃",
        "effect": "每场战斗中，你前 4 » 8 次使用武器时，使一件灼烧物品充能 1 秒",
    },
    "plv4bqmbbvnq7qmm7gg8gsssmw": {
        "name": "燃怒",
        "effect": "当你进入暴怒时，你的物品在本场战斗中获得 +3 » +6 » +9 » +12",
    },
    "zbsblfw9wpxq3w6pswybdpj3qq": {
        "name": "数据传输",
        "effect": "当你使用科技物品时，相邻物品获得 +3 » +6 » +9、+3 » +6 » +9 和 +3 » +6 » +9",
    },
    "1d24hzkcbshz40n7ghwgkwyzgk": {
        "name": "规避机动",
        "effect": "当你使用载具或无人机时，你的物品获得 +3 » +6 » +9",
    },
    "8jvg57h0n4qfl9cd9bkqphx6j7": {
        "name": "处决",
        "effect": "每场战斗中，敌人第一次跌到 20% 最大生命以下时，造成 9999 伤害",
    },
    "gzq5nvlb3j83v0mq0k151dx1fc": {
        "name": "热轮",
        "effect": "当你使用载具或无人机时，你的物品获得 +1 » +2 » +3",
    },
    "8dc26bhd4gc0nl8c9nzwlf2fk2": {
        "name": "商人俱乐部",
        "effect": "商人向你提供的 1 件物品价格降低 1 » 2 » 4 » 8 金币",
    },
    "gd65tf61fk4jbd1ghbxyt8lx77": {
        "name": "穿刺暴怒",
        "effect": "当你进入暴怒时，你的物品在本场战斗中获得 +10 » +20 » +30 » +40",
    },
    "5mz2wqxwm7k3py792gqzcb7s5s": {
        "name": "顽皮纵火狂",
        "effect": "每场战斗中，你前 4 » 8 次使用玩具时，使一件灼烧物品充能 1 秒",
    },
    "18lfg4hm2nhjcgqy5zzhmncdx1p": {
        "name": "毒焰",
        "effect": "当你施加剧毒时，你的物品在本场战斗中获得 +1 » +2 » +3 灼烧",
    },
    "188jh9dhb4vsxllvx8dg6dt8m3g": {
        "name": "毒锻",
        "effect": "当你施加剧毒时，你的物品在本场战斗中获得 +2 » +4 » +6 伤害",
    },
    "12f1ptcmk8zjtd4cvggbwbz0n6t": {
        "name": "打雪仗",
        "effect": "每场战斗中，你前 4 » 8 次使用玩具时，使一件冻结物品充能 1 秒",
    },
    "f2t0wd7vzqccsd9zgfdv8k6zkx": {
        "name": "副厨师长",
        "effect": "每场战斗中，你第一次使用食物时，使 1 » 2 » 3 件工具加速 2 秒",
    },
    "12y7fmpc7hdfdykfm56gw634skx": {
        "name": "精通科技",
        "effect": "你的科技物品冷却时间减少 5 » 10%",
    },
    "11ncvq0pjfkp7ptv1xfzjb2jbj6": {
        "name": "向量指令",
        "effect": "当你使用载具或无人机时，你的物品获得 +3 » +6 » +9",
    },
    "2qztvjctmtjwtm5cmpsnwf31cd": {
        "name": "图书馆纵火狂",
        "effect": "火就是你放的",
    },
    "q9yj47xg4w371mhkq3vzlkd12h": {
        "name": "意外之喜",
        "effect": "每场战斗开始时，为你一件未附魔的无人机和一件未附魔的载具附魔",
    },
    "k0q27svqj7yk9qlpcs98psmz8f": {
        "name": "无人机操作员",
        "effect": "",
    },
}


def load_old_data():
    text = DATA_FILE.read_text(encoding="utf-8")
    match = re.search(r"const data = (.*);\n\nmodule\.exports = data;\s*$", text, re.S)
    if not match:
        raise RuntimeError("Unable to parse bazaarData.js")
    return json.loads(match.group(1))


def create_scraper():
    return cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "darwin", "mobile": False}
    )


def fetch_joined(scraper, category, page=1):
    url = f"https://bazaardb.gg/search?c={category}"
    if page > 1:
        url += f"&page={page}"
    html = scraper.get(url, timeout=30).text
    title_match = re.search(r"<title>.*? - (\d+) Results - Bazaar DB</title>", html)
    if not title_match:
        raise RuntimeError(f"Unable to find title count for {category} page {page}")
    total = int(title_match.group(1))
    parts = [
        m.group(1).encode("utf-8").decode("unicode_escape")
        for m in re.finditer(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', html)
    ]
    return "".join(parts), total


def bracket_slice(text, anchor):
    in_str = False
    escaped = False
    level = 0
    start = None
    for i in range(anchor, -1, -1):
        ch = text[i]
        if in_str:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "]":
                level += 1
            elif ch == "[":
                level -= 1
                if level == 0:
                    start = i
                    break
    if start is None:
        raise RuntimeError("Unable to locate array start")
    return text[start : anchor + 1]


def parse_search_page(scraper, category, page=1):
    joined, total = fetch_joined(scraper, category, page)
    if category == "monsters":
        idx = joined.find('{"cards":[')
        if idx == -1:
            raise RuntimeError("Unable to locate monster cards array")
        segment = joined[idx + 9 :]
        in_str = False
        escaped = False
        level = 0
        end = None
        for i, ch in enumerate(segment):
            if in_str:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "[":
                    level += 1
                elif ch == "]":
                    level -= 1
                    if level == 0:
                        end = i + 1
                        break
        if end is None:
            raise RuntimeError("Unable to locate monster array end")
        return json.loads(segment[:end]), total

    markers = [f'],"total":{total}', f'],"results":{total}']
    for marker in markers:
        anchor = joined.find(marker)
        if anchor != -1:
            return json.loads(bracket_slice(joined, anchor)), total
    raise RuntimeError(f"Unable to parse {category} page {page}")


def scrape_all_cards(scraper):
    cards_by_category = {}
    totals = {}
    for category in CATEGORY_LABELS:
        first_page, total = parse_search_page(scraper, category, page=1)
        page_count = math.ceil(total / 10)
        seen = {}
        for obj in first_page:
            seen[obj["Uri"].split("/")[2]] = obj
        for page in range(2, page_count + 1):
            page_cards, _ = parse_search_page(scraper, category, page=page)
            for obj in page_cards:
                seen[obj["Uri"].split("/")[2]] = obj
        cards_by_category[category] = list(seen.values())
        totals[category] = total
    return cards_by_category, totals


def hero_codes(heroes):
    codes = [HERO_CODES[h] for h in heroes if h != "Common" and h in HERO_CODES]
    return codes


def hero_string(heroes):
    codes = hero_codes(heroes)
    return " / ".join(codes) if codes else "通用"


def tier_label(category, obj):
    base = obj.get("BaseTier", "Bronze")
    label = TIER_LABELS.get(base, "未知")
    tiers = obj.get("Tiers") or {}
    if category in {"items", "skills"} and len(tiers) > 1 and base != "Legendary":
        return f"{label}+"
    return label


def render_value(value):
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return str(value).rstrip("0").rstrip(".")
    return str(value)


def render_tooltips(obj):
    tiers_present = [tier for tier in TIER_ORDER if tier in (obj.get("Tiers") or {})]
    if not tiers_present:
        tiers_present = [obj.get("BaseTier", "Bronze")]
    rendered = []
    replacements = obj.get("TooltipReplacements") or {}
    for tooltip in obj.get("Tooltips") or []:
        text = tooltip["Content"]["Text"]
        for key in sorted(replacements.keys(), key=len, reverse=True):
            spec = replacements[key]
            if isinstance(spec, dict):
                if "Fixed" in spec:
                    replacement = render_value(spec["Fixed"])
                else:
                    values = [
                        render_value(spec[tier])
                        for tier in TIER_ORDER
                        if tier in tiers_present and tier in spec
                    ]
                    replacement = " » ".join(values)
            else:
                replacement = render_value(spec)
            text = text.replace(key, replacement)
        rendered.append(re.sub(r"\s+", " ", text).strip())
    return " ".join(rendered).strip()


NUMBER_TOKEN_RE = re.compile(r"\d+(?:\.\d+)?%?")


def sync_numbers(chinese_text, english_text):
    if not chinese_text or not english_text:
        return chinese_text
    english_tokens = NUMBER_TOKEN_RE.findall(english_text)
    chinese_tokens = NUMBER_TOKEN_RE.findall(chinese_text)
    if not english_tokens or len(english_tokens) != len(chinese_tokens):
        return chinese_text
    result = chinese_text
    for old, new in zip(chinese_tokens, english_tokens):
        result = result.replace(old, new, 1)
    return result


def translate_name(card_id, english_name, old_card):
    if old_card:
        return old_card["name"]
    manual = NEW_CARD_TRANSLATIONS.get(card_id)
    if manual:
        return manual["name"]
    return english_name


def translate_effect(card_id, english_effect, old_card):
    if old_card:
        return sync_numbers(old_card.get("effect", ""), english_effect)
    manual = NEW_CARD_TRANSLATIONS.get(card_id)
    if manual:
        return manual["effect"]
    return english_effect


def translate_tag(tag):
    return TAG_TRANSLATIONS.get(tag, tag)


def card_id_from_uri(uri):
    return uri.split("/")[2]


def card_url(uri):
    return f"https://bazaardb.gg{uri}"


def mechanic_list(obj, old_card):
    if old_card and old_card.get("mechanics"):
        return old_card["mechanics"]
    tags = [str(t).lower() for t in obj.get("Tags", []) + obj.get("HiddenTags", [])]
    found = []
    for key, label in MECHANIC_MAP.items():
        if any(key in tag for tag in tags):
            found.append({"key": key, "label": label})
    return found


def source_list(obj, old_card, translated_name_by_id):
    dropped = obj.get("DroppedBy") or []
    if not dropped:
        return []
    old_source_list = old_card.get("sourceList", []) if old_card else []
    result = []
    for index, source in enumerate(dropped):
        source_id = card_id_from_uri(source["href"])
        day = source.get("available", "")
        name = translated_name_by_id.get(source_id) or EXTRA_TITLE_TRANSLATIONS.get(source["title"]) or (
            old_source_list[index]["name"] if index < len(old_source_list) else source["title"]
        )
        result.append({"name": name, "day": day.replace("Day ", "D")})
    return result


def monster_detail_lines(obj, translated_name_by_id):
    meta = obj.get("MonsterMetadata") or {}
    lines = []
    if meta.get("available"):
        lines.append(f"出现：{meta['available'].replace('Day ', '第 ')} 天")
    if meta.get("health") is not None:
        lines.append(f"生命：{meta['health']}")
    for item in meta.get("board", []):
        tier = item.get("tierOverride", "")
        tier_label_zh = TIER_LABELS.get(tier, tier)
        title = translated_name_by_id.get(card_id_from_uri(item["url"])) or EXTRA_TITLE_TRANSLATIONS.get(item["title"], item["title"])
        lines.append(f"棋盘：{tier_label_zh} {title}")
    for skill in meta.get("skills", []):
        tier = skill.get("tierOverride", "")
        tier_label_zh = TIER_LABELS.get(tier, tier)
        title = translated_name_by_id.get(card_id_from_uri(skill["url"])) or EXTRA_TITLE_TRANSLATIONS.get(skill["title"], skill["title"])
        lines.append(f"技能：{tier_label_zh} {title}")
    return lines


def event_detail_lines(old_card):
    return deepcopy(old_card.get("detailLines", [])) if old_card else []


def category_tags(obj):
    return [translate_tag(tag) for tag in obj.get("DisplayTags", [])]


def size_value(obj):
    return ""


def cooldown_value(obj, old_card):
    base = obj.get("BaseAttributes") or {}
    cooldown = base.get("CooldownMax")
    if cooldown is None:
        return (old_card or {}).get("cooldown", "")
    seconds = cooldown / 1000
    if float(seconds).is_integer():
        return f"{int(seconds)} 秒"
    return f"{seconds:g} 秒"


def build_card(category, obj, old_card, translated_name_by_id):
    card_id = card_id_from_uri(obj["Uri"])
    zh_name = translate_name(card_id, obj["Title"]["Text"], old_card)
    effect_en = render_tooltips(obj)
    tags = category_tags(obj)
    heroes = hero_codes(obj.get("Heroes", []))
    hero = hero_string(obj.get("Heroes", []))
    tier_class = TIER_CLASSES.get(obj.get("BaseTier", "Bronze"), "bronze")

    if category == "monsters":
        detail_lines = monster_detail_lines(obj, translated_name_by_id)
    elif category == "events":
        detail_lines = event_detail_lines(old_card)
    else:
        detail_lines = deepcopy(old_card.get("detailLines", [])) if old_card else []

    if old_card and category != "monsters":
        detail_lines = [sync_numbers(line, effect_en) for line in detail_lines]

    return {
        "id": card_id,
        "category": category,
        "categoryLabel": CATEGORY_LABELS[category],
        "name": zh_name,
        "url": card_url(obj["Uri"]),
        "image": obj.get("Art", ""),
        "detailImage": obj.get("Art", ""),
        "imageAlt": zh_name,
        "heroes": heroes,
        "hero": hero,
        "tier": tier_label(category, obj),
        "tierClass": tier_class,
        "tags": tags,
        "allTags": heroes + tags,
        "cooldown": cooldown_value(obj, old_card),
        "effect": translate_effect(card_id, effect_en, old_card),
        "sourceList": source_list(obj, old_card, translated_name_by_id),
        "mechanics": mechanic_list(obj, old_card),
        "source": "Bazaar DB 中文数据",
        "accent": ACCENTS[tier_class],
        "initial": zh_name[:1],
        "detailLines": detail_lines,
    }


def main():
    old_data = load_old_data()
    old_by_id = {card["id"]: card for card in old_data["cards"]}

    scraper = create_scraper()
    cards_by_category, totals = scrape_all_cards(scraper)

    translated_name_by_id = {}
    for category, objects in cards_by_category.items():
        for obj in objects:
            cid = card_id_from_uri(obj["Uri"])
            old_card = old_by_id.get(cid)
            translated_name_by_id[cid] = translate_name(cid, obj["Title"]["Text"], old_card)

    cards = []
    for category in CATEGORY_LABELS:
        for obj in cards_by_category[category]:
            cid = card_id_from_uri(obj["Uri"])
            cards.append(build_card(category, obj, old_by_id.get(cid), translated_name_by_id))

    cards.sort(key=lambda card: (
        list(CATEGORY_LABELS.keys()).index(card["category"]),
        card["name"],
        card["id"],
    ))

    tag_order = []
    for card in cards:
        for tag in card["tags"]:
            if tag and tag not in tag_order:
                tag_order.append(tag)

    data = {
        "patch": "15.0 (Jun 3)",
        "source": "https://bazaardb.gg/",
        "categories": [
            {"id": "all", "label": "全部", "count": len(cards)},
            *[
                {"id": category, "label": CATEGORY_LABELS[category], "count": totals[category]}
                for category in CATEGORY_LABELS
            ],
        ],
        "heroes": ["通用", "VAN", "PYG", "DOO", "MAK", "STE", "JUL", "KAR"],
        "tiers": ["青铜+", "白银+", "黄金+", "钻石+", "传奇+", "青铜", "白银", "黄金", "钻石", "传奇", "未知"],
        "sizes": [],
        "tags": tag_order,
        "cards": cards,
    }

    output = "const data = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n\nmodule.exports = data;\n"
    DATA_FILE.write_text(output, encoding="utf-8")

    summary = {
        "patch": data["patch"],
        "counts": {category: totals[category] for category in CATEGORY_LABELS},
        "total": len(cards),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
