# -*- coding: utf-8 -*-
"""户型图.png 的 HouseSpec 生成脚本。
像素->毫米按四周标注刻度建立分段轴（axismap.Axis），墙厚：外墙/厚墙240承重，隔墙120非承重。"""
import json, sys
sys.path.insert(0, "/Users/bytedance/Library/Application Support/Doubao/Profile 1/.doubao/agent_mode/workspace/.skills/house-plan-designer/scripts")
from axismap import Axis, chain

# ---- X 轴：顶部 5 段标注 852/1150/2994/1774/2096，底部补充西墙中线 792、x759 墙 4996 ----
top = chain([142, 247.5, 389.5, 758.5, 977.5, 1237], [852, 1150, 2994, 1774, 2096])
bot = [(240.5, 792.0), (759.5, 4996.0), (1237.0, 8866.0)]
X = Axis(top, bot)
# ---- Y 轴：左侧 4 段 1773/1040/1703/3368，右侧补充卫生间南墙 2140 ----
left = chain([168.5, 412, 553.5, 788, 1249.5], [1773, 1040, 1703, 3368])
right = [(461.5, 2140.0), (1249.5, 7884.0)]
Y = Axis(left, right)
if "--report" in sys.argv:
    X.report(); Y.report(); sys.exit()

r5 = lambda v: round(v / 5) * 5
def P(x, y): return [r5(X(x)), r5(Y(y))]

def H(y, x0, x1, t, bearing=False, ops=()):
    o = []
    for d in ops:
        d = dict(d); d["from"] = X(d.pop("f")); d["to"] = X(d.pop("e")); o.append(d)
    return dict(a=P(x0, y), b=P(x1, y), t=t, bearing=bearing, openings=o)

def V(x, y0, y1, t, bearing=False, ops=()):
    o = []
    for d in ops:
        d = dict(d); d["from"] = Y(d.pop("f")); d["to"] = Y(d.pop("e")); o.append(d)
    return dict(a=P(x, y0), b=P(x, y1), t=t, bearing=bearing, openings=o)

E, G = 240, 120  # 承重厚墙 / 非承重隔墙
walls = [
    # 北外墙（入户双开门 815-923）
    H(168.5, 225, 1252, E, True, [dict(type="double", f=815, e=923, entry=True, into=P(870, 320))]),
    # 东外墙（整面实墙，卫生间暗卫无窗）
    V(1237, 152, 1266, E, True),
    # 南外墙（主卧推拉窗 368-588、客餐厅大推拉窗 858-1181）
    H(1249.5, 225, 1252, E, True, [
        dict(type="slideWindow", f=368, e=588),
        dict(type="slideWindow", f=858, e=1181),
    ]),
    # 西外墙（阳台西窗 200-349、次卧飘窗 bay 569-772，凸出部分由设计器自动生成并归入次卧）
    V(240.5, 152, 1266, E, True, [
        dict(type="window", f=200, e=349),
        dict(type="bay", f=569, e=772),
    ]),
    # 阳台/厨房隔墙（推拉门 276-381）
    V(389.5, 152, 419, G, False, [dict(type="sliding", f=276, e=381, hinge="from", into=P(330, 330))]),
    # 厨房南墙（次卧北墙）
    H(412, 225, 774, G, False),
    # 厨房东墙（厚墙，厨房门 280-380，门轴南端、开入厨房）
    V(759.5, 152, 653, E, True, [dict(type="door", f=280, e=380, hinge="to", into=P(700, 330))]),
    # 主卧东墙（厚墙，过道敞口 653-798 以南起）
    V(759.5, 798, 1266, E, True),
    # 卫生间西墙（门 347-446，门轴南端、开入卫生间）
    V(978, 152, 470, G, False, [dict(type="door", f=347, e=446, hinge="to", into=P(1060, 400))]),
    # 卫生间南墙
    H(462, 971, 1252, G, False),
    # 次卧南墙东段
    H(653, 610, 774, G, False),
    # 次卧门墙（门 682-790，门轴南端、开入次卧）
    V(617, 645, 808, G, False, [dict(type="door", f=682, e=790, hinge="to", into=P(560, 740))]),
    # 主卧北墙（主卧门 639-739，门轴东端、开入主卧）
    H(801, 225, 774, G, False, [dict(type="door", f=639, e=739, hinge="to", into=P(690, 900))]),
]
for w in walls:
    if not w["openings"]:
        del w["openings"]

rooms = [
    (310, 290, "阳台", "deck"),
    (520, 290, "厨房", "bath"),
    (460, 520, "次卧", "oak"),
    (500, 1050, "主卧", "walnut"),
    (1120, 300, "卫生间", "terrazzo"),
    (1050, 750, "客餐厅", "tile"),
]

# 家具直接用毫米世界坐标（房间净边界已按墙内皮推算）
def F(key, x, y, rot=0, **kw):
    d = dict(key=key, at=[r5(x), r5(y)], rot=rot)
    d.update(kw)
    return d

furniture = [
    # ---- 主卧（净 3964×3094，床头靠北墙，床西移让出东侧 ≥700 进门通道）----
    F("bed18", 2600, 5720),
    F("nightstand", 1450, 5720), F("nightstand", 3750, 5720),
    F("cabWardrobe", 4576, 6500, 90, w=2000),
    F("acWall", 1450, 4750, 0),
    F("curtain", 2710, 7684, 180, w=2000),
    # ---- 次卧（净 3964×2717，含西侧 bay 飘窗，床西移让开门洞）----
    F("bed15", 2150, 2858),
    F("wardrobe", 4576, 2600, 90, w=1500),
    F("acWall", 4300, 1900, 0),
    F("curtain", 992, 3668, 270, w=1400),
    # ---- 客餐厅 ----
    F("shoeCabinet", 6475, 700, 270, w=1000),         # 入户右手、卫生间西墙玄关侧
    F("sideboard", 6600, 2400, 0, w=1000),            # 靠卫生间南墙东段，西侧留 700+ 通道
    F("waterDispenser", 7400, 2400, 0),               # 餐边柜东侧
    F("diningTable", 6600, 3550, 0),
    F("chair", 6300, 2840, 0), F("chair", 6900, 2840, 0),
    F("chair", 6300, 4260, 180), F("chair", 6900, 4260, 180),
    F("sofa", 8271, 6000, 90),
    F("coffeeTable", 7296, 6000, 90),
    F("rug", 7300, 6000, 90, w=2000, d=1700),
    F("wallTV", 5150, 6000, 270),
    F("acFloor", 5400, 7504, 270),
    F("curtain", 7110, 7684, 180, w=2800),
    F("floorLamp", 8350, 4700, 0),
    F("plant", 8500, 2500, 0, w=400, d=400),
    # ---- 厨房（净 2814×1593）----
    F("counter", 3112, 420, 0, w=2100),
    F("fridge", 4526, 470, 90),
    F("gasHeater", 2120, 500, 270),
    # ---- 卫生间（净 1916×1960，门在西南角）----
    F("vanity", 7230, 370, 0),
    F("shower", 8296, 570, 0),
    F("toilet", 8396, 1500, 90),
    F("waterHeater", 8396, 1500, 90),
    F("bathHeater", 7800, 1000, 0),
    # ---- 阳台（净 1030×1593）----
    F("laundrySink", 1427, 420, 0),
    F("washer", 1427, 1413, 180),
    F("clothesRack", 1427, 900, 90, w=1400),
    F("curtain", 950, 900, 270, w=1100),
]

structs = [
    dict(kind="sewer", at=[8446, 1500]),    # 马桶下水
    dict(kind="drain", at=[8296, 600]),     # 淋浴地漏
    dict(kind="drain", at=[1427, 1450]),    # 阳台地漏
]

spec = dict(
    name="两室一厅 · 户型还原方案",
    height=2800,
    phase="renovate",
    north=0,
    site=dict(city="北京"),
    walls=walls,
    rooms=[dict(at=P(x, y), name=n, mat=m) for x, y, n, m in rooms],
    furniture=furniture,
    structs=structs,
    autoElec=True,
    underlay=dict(
        image="户型图.png",
        mmPerPx=round((X.scale + Y.scale) / 2, 4),
        x=r5(X(0, None)),
        y=r5(Y(0, None)),
    ),
)
json.dump(spec, open(sys.argv[1] if len(sys.argv) > 1 else "spec.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("walls:", len(walls), "X.scale=%.3f Y.scale=%.3f" % (X.scale, Y.scale))
