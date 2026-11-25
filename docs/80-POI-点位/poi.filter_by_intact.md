# `poi.filter_by_intact`

> 可用资源点

| | |
|---|---|
| 模块 | `poi` · `src/dora/tools/poi.py:722`（5 行） |
| 相关性 | ★ |
| 可迁移性 | A |
| 依赖 | none |
| 异常处理 | 有 `_tool_guard`：输入文件缺失时返回空结果，其他异常转成 `{"error": ...}` 返回 |

## 源码中的原话

> Filter POI results to only include those located in intact buildings. Takes the output from tool.loop and keeps items where damage_class == 1.

## 输入

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|:-:|---|---|
| `data` | list[dict] | 是 | — | 输入数据（数组或字典，结构见源码） |

## 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `total_input` | int | Total number of input items |
| `total_intact` | int | Number of intact items found |
| `filtered_results` | list | Filtered results with damage_class == 1 |

## 依赖与运行

- 依赖：none
- 硬件：纯算法，CPU 毫秒级；无需 GPU
- 输入：栅格 GeoTIFF/PNG；矢量 GeoJSON

## 调用

```python
from dora.tools.poi import poi_filter_by_intact_tool
import json

res = json.loads(poi_filter_by_intact_tool(data="input.tif"))
print(res)
```

```json
{
  "name": "poi.filter_by_intact",
  "arguments": {
    "data": "input.tif"
  }
}
```

## 示例

> 下面这组是**真跑出来的**：输入取自 DORA 数据根里的真实影像，输出是工具原样返回。路径用 `<DORA_DATA>` / `<temp_dir>` 占位，换机器照抄即可。

### 示例输入

数据：images/disasterm3/noto_earthquake_agent2/…_poi.geojson（307 个点）

```json
{
  "data": [
    {
      "name": "Kuwagumi",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "キッチン道",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Minokoh",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Kadochō Syokudō",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Ju Ju",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "山小屋",
      "types": "meal_takeaway, restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Kanayama",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Shinkoma",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Yabu Shimbashi",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "やぶかぶれ",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Kabulet",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Ueno Sushi",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "L'Atelier de NOTO",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Ikka",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Mariners Cafe & Restaurant",
      "types": "cafe, restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Étranger",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Domburako",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Azuma Sushi",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Aiuto!",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Suke Sushi",
      "types": "meal_takeaway, restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Go Go Curry Wajima Shop",
      "types": "meal_takeaway, restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Jin",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Kinomi Cafe",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Portulacea",
      "types": "restaurant, food, bar, point_of_interest, establishment"
    },
    {
      "name": "狸",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Seikaisho",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "炭火焼肉ライクイット",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Notokichi",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Tokushin",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Izakaya Warashibe",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Orizzonte",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "わいちストアNAKAURAYA",
      "types": "cafe, bakery, restaurant, food, point_of_interest, store, establishment"
    },
    {
      "name": "Chihara",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "スナック ボン・リ・ブラン",
      "types": "meal_takeaway, restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Shimpuku",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "大ちょうちん",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Ramen Ibuki",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Ren",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "コミセン鳳至BASE",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "一口柚餅子本舗 良澤本店",
      "types": "store, restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Warashow",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Nakauraya",
      "types": "tourist_attraction, cafe, travel_agency, restaurant, food, point_of_interest, store, establishment"
    },
    {
      "name": "輪島朝市むすび",
      "types": "meal_takeaway, restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Zuru Zuru",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Toku",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Miki Sushi",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "美喜寿司 焼肉部",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Enka",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Mebuki",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "居酒屋 いち富",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Junsai",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "焼肉みらい YAKINIKU",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Wajimon",
      "types": "restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Furatto",
      "types": "meal_takeaway, restaurant, food, point_of_interest, establishment"
    },
    {
      "name": "Wajima Midori Nursery",
      "types": "point_of_interest, school, establishment"
    },
    {
      "name": "Kurokawaryoko Piano Lessons",
      "types": "point_of_interest, school, store, establishment"
    },
    {
      "name": "Wako Kindergarten",
      "types": "school, point_of_interest, establishment"
    },
    {
      "name": "Kawai Elementary School",
      "types": "primary_school, school, point_of_interest, establishment"
    },
    {
      "name": "Wajima High School",
      "types": "school, point_of_interest, establishment"
    },
    {
      "name": "hapi hapy",
      "types": "school, point_of_interest, establishment"
    },
    {
      "name": "東進中学NET輪島校",
      "types": "school, point_of_interest, establishment"
    },
    {
      "name": "Hokkokujukuwa Center Youshitsu",
      "types": "school, point_of_interest, establishment"
    },
    {
      "name": "塾 輪島 志学舎",
      "types": "school, point_of_interest, establishment"
    },
    {
      "name": "Kawai Nursery",
      "types": "school, point_of_interest, establishment"
    },
    {
      "name": "Fugeshi Elementary School",
      "types": "primary_school, school, point_of_interest, establishment"
    },
    {
      "name": "Horai Nursery School",
      "types": "school, point_of_interest, establishment"
    },
    {
      "name": "Kono Shinkin Bank Wajima",
      "types": "bank, atm, finance, point_of_interest, establishment"
    },
    {
      "name": "ＪＡのと 輪島支店 信用共済課",
      "types": "bank, atm, finance, point_of_interest, establishment"
    },
    {
      "name": "Hokkoku Bank Wajima",
      "types": "bank, atm, finance, point_of_interest, establishment"
    },
    {
      "name": "Hokuriku Bank Wajima Branch",
      "types": "bank, atm, finance, point_of_interest, establishment"
    },
    {
      "name": "Noto Kyoei Shinkin Bank Wajima",
      "types": "bank, atm, finance, point_of_interest, establishment"
    },
    {
      "name": "輪島商工復興センター",
      "types": "shopping_mall, point_of_interest, establishment"
    },
    {
      "name": "輪島市観音町復興通り地区仮設商店街",
      "types": "shopping_mall, point_of_interest, establishment"
    },
    {
      "name": "Power City",
      "types": "shopping_mall, atm, supermarket, grocery_or_supermarket, finance, food, point_of_interest, store, establishment"
    },
    {
      "name": "六銘館 海の駅",
      "types": "shopping_mall, point_of_interest, establishment"
    },
    {
      "name": "輪島市観音町子ども広場前地区仮設商店街",
      "types": "shopping_mall, point_of_interest, establishment"
    },
    {
      "name": "JA-SS /ＪＡのと 大屋SS",
      "types": "gas_station, point_of_interest, establishment"
    },
    {
      "name": "COSMO Futatsuya SS",
      "types": "gas_station, car_wash, car_repair, point_of_interest, store, establishment"
    },
    {
      "name": "Wajima Nanohana Pharmacy",
      "types": "pharmacy, health, point_of_interest, store, establishment"
    },
    {
      "name": "坂久錦生堂",
      "types": "pharmacy, health, point_of_interest, store, establishment"
    },
    {
      "name": "Miyawaki Pharmacy",
      "types": "pharmacy, health, point_of_interest, store, establishment"
    },
    {
      "name": "Shimeno Drug Wajima Pharmacy",
      "types": "pharmacy, store, health, point_of_interest, establishment"
    },
    {
      "name": "Matsumotokiyoshi Wajimaten Pharmacy",
      "types": "drugstore, pharmacy, store, health, point_of_interest, establishment"
    },
    {
      "name": "Marco Grocery Store",
      "types": "supermarket, grocery_or_supermarket, food, point_of_interest, store, establishment"
    },
    {
      "name": "Minamimachiko Park",
      "types": "park, point_of_interest, establishment"
    },
    {
      "name": "鳳至めっこ広場",
      "types": "park, point_of_interest, establishment"
    },
    {
      "name": "Azumaya",
      "types": "park, point_of_interest, establishment"
    },
    {
      "name": "健康ふれあい広場",
      "types": "park, point_of_interest, establishment"
    },
    {
      "name": "Ipponmatsu Park",
      "types": "park, point_of_interest, establishment"
    },
    {
      "name": "Fujidana",
      "types": "park, point_of_interest, establishment"
    },
    {
      "name": "宅田桜堤",
      "types": "park, point_of_interest, establishment"
    },
    {
      "name": "観音町子どもの広場",
      "types": "park, point_of_interest, establishment"
    },
    {
      "name": "Wajima Museum of Lacquer (Urushi) Art",
      "types": "tourist_attraction, museum, point_of_interest, establishment"
    },
    {
      "name": "Wajima Lacquerware Museum",
      "types": "museum, point_of_interest, store, establishment"
    },
    {
      "name": "輪島塗の稲忠",
      "types": "museum, point_of_interest, establishment"
    },
    {
      "name": "Wajima Kiriko Art Museum",
      "types": "tourist_attraction, museum, point_of_interest, establishment"
    },
    {
      "name": "Hatakeda",
      "types": "sublocality_level_3, sublocality, political"
    },
    {
      "name": "Kamiyu Hair Salon",
      "types": "hair_care, point_of_interest, establishment"
    },
    {
      "name": "Anju",
      "types": "hair_care, point_of_interest, establishment"
    },
    {
      "name": "HAIR-J",
      "types": "hair_care, point_of_interest, establishment"
    },
    {
      "name": "Kanazawachihohomukyoku Wajimashikyoku",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "石川県立輪島漆芸技術研修所",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Funaki Clinic",
      "types": "doctor, health, point_of_interest, establishment"
    },
    {
      "name": "谷川醸造㈱",
      "types": "food, point_of_interest, establishment"
    },
    {
      "name": "Wajima Shonanmachi Post Office",
      "types": "post_office, atm, finance, point_of_interest, establishment"
    },
    {
      "name": "日吉商店",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "四十沢木材工芸 Factory's Gallery",
      "types": "home_goods_store, store, point_of_interest, establishment"
    },
    {
      "name": "Yamagi Lumber Co",
      "types": "point_of_interest, general_contractor, establishment"
    },
    {
      "name": "姿勢専科・ＫＣＳセンターのと",
      "types": "health, point_of_interest, establishment"
    },
    {
      "name": "津田漆器店",
      "types": "home_goods_store, store, point_of_interest, establishment"
    },
    {
      "name": "石川勤労者医療協会輪島診療所",
      "types": "health, point_of_interest, establishment"
    },
    {
      "name": "（株）大向カーオート",
      "types": "car_dealer, store, point_of_interest, establishment"
    },
    {
      "name": "Inarimachi",
      "types": "sublocality_level_3, sublocality, political"
    },
    {
      "name": "Wajima",
      "types": "locality, political"
    },
    {
      "name": "Fugeshimachi",
      "types": "sublocality_level_2, sublocality, political"
    },
    {
      "name": "池端漆香堂",
      "types": "home_goods_store, store, point_of_interest, establishment"
    },
    {
      "name": "Ishikawaken Notohokubu Public Health Center",
      "types": "local_government_office, health, point_of_interest, establishment"
    },
    {
      "name": "輪島食品衛生協会",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Wajimaya Zenni Lacquer Shop",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "さかしたペットセンター",
      "types": "pet_store, store, point_of_interest, establishment"
    },
    {
      "name": "輪島屋善仁デザイン室",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Care Home Minnanouta",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "五島屋 二勢工場",
      "types": "home_goods_store, store, point_of_interest, establishment"
    },
    {
      "name": "Okemoto Eye Clinic",
      "types": "health, point_of_interest, establishment"
    },
    {
      "name": "輪島塗 坂本漆器店",
      "types": "home_goods_store, store, point_of_interest, establishment"
    },
    {
      "name": "塩山エレクトーン教室",
      "types": "general_contractor, point_of_interest, establishment"
    },
    {
      "name": "カモン看板",
      "types": "store, point_of_interest, establishment"
    },
    {
      "name": "Minoru Shinbo Store",
      "types": "food, point_of_interest, establishment"
    },
    {
      "name": "Itō Clinic",
      "types": "health, point_of_interest, establishment"
    },
    {
      "name": "蔵田木工所",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "尚古堂",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Mitomori Inari Shrine",
      "types": "place_of_worship, point_of_interest, establishment"
    },
    {
      "name": "Kamayadani",
      "types": "transit_station, point_of_interest, establishment"
    },
    {
      "name": "坂長",
      "types": "food, point_of_interest, store, establishment"
    },
    {
      "name": "Situgeibijutukan",
      "types": "transit_station, point_of_interest, establishment"
    },
    {
      "name": "石川輪島漆芸桜並木",
      "types": "tourist_attraction, point_of_interest, establishment"
    },
    {
      "name": "Fresh Land Marcoux Parking Lot",
      "types": "parking, point_of_interest, establishment"
    },
    {
      "name": "ZABOON Fugeshimise Coin Laundry",
      "types": "laundry, point_of_interest, establishment"
    },
    {
      "name": "Marble",
      "types": "night_club, bar, point_of_interest, establishment"
    },
    {
      "name": "輪島市水守町堂端地区仮設工房",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "輪島荘川桜・荘川七郎",
      "types": "tourist_attraction, point_of_interest, establishment"
    },
    {
      "name": "輪島漆器商工業協同組合 精漆工場",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "県立漆芸研修所前（バス）",
      "types": "transit_station, point_of_interest, establishment"
    },
    {
      "name": "EV充電スポット",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "天野木材（株）",
      "types": "point_of_interest, store, establishment"
    },
    {
      "name": "Kenritusitugeikensyujomae",
      "types": "transit_station, point_of_interest, establishment"
    },
    {
      "name": "天理教 大輪布教所",
      "types": "church, place_of_worship, point_of_interest, establishment"
    },
    {
      "name": "輪島市移住促進住宅",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "グリーンマーケットMOA輪島店",
      "types": "point_of_interest, store, establishment"
    },
    {
      "name": "Japan Post Bank ATM",
      "types": "atm, point_of_interest, finance, establishment"
    },
    {
      "name": "畑中塗箸店",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "蒔絵師 五代 清石 川谷内（かわやち）準之助",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Sakae Hair Salon",
      "types": "hair_care, point_of_interest, establishment"
    },
    {
      "name": "Kotobuki",
      "types": "lodging, point_of_interest, establishment"
    },
    {
      "name": "Honda",
      "types": "car_repair, car_dealer, point_of_interest, store, establishment"
    },
    {
      "name": "JA Ozo Rawajima",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Wajima City Council Secretariat",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Takada Photography",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "アミューズ・ワジマ",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "酒ブティックおくだ",
      "types": "liquor_store, point_of_interest, store, establishment"
    },
    {
      "name": "石川県奥能登土木総合事務所 庶務課",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "室金物店",
      "types": "hardware_store, general_contractor, furniture_store, home_goods_store, point_of_interest, store, establishment"
    },
    {
      "name": "輪島・穴水地域ライフ・サポートセンター",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "qiu きう",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "（有）久岡保険事務所",
      "types": "insurance_agency, point_of_interest, establishment"
    },
    {
      "name": "ＡＦＬＡＣ専属 の 保険代理店",
      "types": "insurance_agency, point_of_interest, establishment"
    },
    {
      "name": "Shinsetsu",
      "types": "lodging, point_of_interest, establishment"
    },
    {
      "name": "市中漆器工房",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "輪島訪問看護ステーション",
      "types": "health, point_of_interest, establishment"
    },
    {
      "name": "Osaka Acupuncture",
      "types": "health, point_of_interest, establishment"
    },
    {
      "name": "FamilyMart; Wajima Central",
      "types": "convenience_store, food, point_of_interest, store, establishment"
    },
    {
      "name": "酒のたかた 高田本店",
      "types": "liquor_store, point_of_interest, store, establishment"
    },
    {
      "name": "東洋警備保障㈱輪島営業所",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "セレモニー会館 おおぞら天翔輪島 ＪＡのと",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "石川印刷 輪島営業所",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Nakagishi Orthopedic Clinic",
      "types": "health, point_of_interest, establishment"
    },
    {
      "name": "輪島漆器商工業協同組合",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "北陸電力(株) 輪島営業所 総務担当",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "輪島市 福祉環境部子育て支援センター・児童センター",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "輪島市まんなか商店街振興組合",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "輪島市 福祉環境部健康推進課",
      "types": "city_hall, local_government_office, point_of_interest, establishment"
    },
    {
      "name": "Nagai Dental Clinic",
      "types": "dentist, health, point_of_interest, establishment"
    },
    {
      "name": "鳳輪建設業協会",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Mitsue Hair Salon",
      "types": "hair_care, point_of_interest, establishment"
    },
    {
      "name": "Beauty Salon Otani",
      "types": "hair_care, point_of_interest, establishment"
    },
    {
      "name": "垣地椀木地所",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "シロー",
      "types": "hair_care, point_of_interest, establishment"
    },
    {
      "name": "中濱与吉屋",
      "types": "food, point_of_interest, establishment"
    },
    {
      "name": "Yashiki Inn",
      "types": "lodging, point_of_interest, establishment"
    },
    {
      "name": "A STORE WAJIMA",
      "types": "store, point_of_interest, establishment"
    },
    {
      "name": "Wajima Branch, Kanazawa District Public Prosecutor Office",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Kanazawa District Court Wajima Branch",
      "types": "courthouse, point_of_interest, establishment"
    },
    {
      "name": "Sakashita",
      "types": "lodging, point_of_interest, establishment"
    },
    {
      "name": "Hanayoshi Flowers",
      "types": "florist, store, point_of_interest, establishment"
    },
    {
      "name": "花屋 卯さぎ",
      "types": "florist, store, point_of_interest, establishment"
    },
    {
      "name": "Wajima Tax Collector",
      "types": "accounting, local_government_office, finance, point_of_interest, establishment"
    },
    {
      "name": "Taya",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Wajimaseisho Church",
      "types": "church, place_of_worship, point_of_interest, establishment"
    },
    {
      "name": "浅見漆器店",
      "types": "home_goods_store, store, point_of_interest, establishment"
    },
    {
      "name": "シメノ仏壇 輪島工場",
      "types": "store, point_of_interest, establishment"
    },
    {
      "name": "Nobuta Orthopedic Clinic",
      "types": "health, point_of_interest, establishment"
    },
    {
      "name": "わじまおみやげ館",
      "types": "store, point_of_interest, establishment"
    },
    {
      "name": "北國新聞社奥能登支社",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "輪島市シルバー人材センター",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "吉田漆器工房",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Wajimakanisaibansho",
      "types": "courthouse, point_of_interest, establishment"
    },
    {
      "name": "Post Office Pickup",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Honke Kamadoya Wajima",
      "types": "store, food, point_of_interest, establishment"
    },
    {
      "name": "千舟堂(岡垣漆器店)",
      "types": "home_goods_store, store, point_of_interest, establishment"
    },
    {
      "name": "藏口屋",
      "types": "store, food, point_of_interest, establishment"
    },
    {
      "name": "Wajimashi Shakaifukushikyogikai",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "輪島ライオンズクラブ",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Nakatani Carpentry",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "鳳珠酒造組合",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Wajima Taxis",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Junior chamber international Wajima",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "うるしの匠",
      "types": "store, point_of_interest, establishment"
    },
    {
      "name": "輪島労働基準協会",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Wajimajoshitabi | Sight Seeing Information Center",
      "types": "travel_agency, point_of_interest, establishment"
    },
    {
      "name": "Wajima Post Office Chokin",
      "types": "post_office, finance, point_of_interest, establishment"
    },
    {
      "name": "安心代行運転",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "あての木園 ふげしデイサービスセンター",
      "types": "health, point_of_interest, establishment"
    },
    {
      "name": "輪島塗 中島忠平漆器店",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "新谷産業 輪島工場",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "輪島海房やまぐち",
      "types": "store, food, point_of_interest, establishment"
    },
    {
      "name": "加藤漆器店",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "坂口漆器店",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "四十沢漆店",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "前田漆器工房",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "輪島・うみ（海美味）工房",
      "types": "food, point_of_interest, establishment"
    },
    {
      "name": "山崖松花堂 芯漆",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Yamashohei Dental Clinic",
      "types": "dentist, health, point_of_interest, establishment"
    },
    {
      "name": "Wajimaso",
      "types": "health, point_of_interest, establishment"
    },
    {
      "name": "Minami Dental Clinic",
      "types": "dentist, health, point_of_interest, establishment"
    },
    {
      "name": "藤沢一二幸瓦店",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Hori Hakusan Shrine",
      "types": "place_of_worship, point_of_interest, establishment"
    },
    {
      "name": "Horimati",
      "types": "transit_station, point_of_interest, establishment"
    },
    {
      "name": "さかみず不動産",
      "types": "real_estate_agency, point_of_interest, establishment"
    },
    {
      "name": "Kishida Flowers",
      "types": "florist, store, point_of_interest, establishment"
    },
    {
      "name": "米谷木工所",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "喜多組 社員寮",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Yuhigaokajutaku",
      "types": "transit_station, point_of_interest, establishment"
    },
    {
      "name": "トキワ塗装店",
      "types": "painter, point_of_interest, establishment"
    },
    {
      "name": "板谷商店",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "石川 勤労 者 医療 協会",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "社会福祉 海と虹",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Umitosora Group Home",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "地域生活支援 ウミュードゥソラ",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Matsushita Construction",
      "types": "general_contractor, point_of_interest, establishment"
    },
    {
      "name": "Jinza",
      "types": "lodging, point_of_interest, establishment"
    },
    {
      "name": "若島漆器店",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "エホバの証人の王国会館",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "集古堂",
      "types": "store, point_of_interest, establishment"
    },
    {
      "name": "Bosho",
      "types": "place_of_worship, point_of_interest, establishment"
    },
    {
      "name": "クボタ クリーン 精米屋",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "輪島市 鳳至児童クラブ",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Inarimatinisi",
      "types": "transit_station, point_of_interest, establishment"
    },
    {
      "name": "萬砂漆器店",
      "types": "home_goods_store, point_of_interest, store, establishment"
    },
    {
      "name": "輪島市応急仮設住宅 鳳至町第1団地(鳳⾄⼩学校グラウンド)",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Beauty Salon Koharu",
      "types": "hair_care, point_of_interest, establishment"
    },
    {
      "name": "Croissant Budget Japanese inn",
      "types": "lodging, point_of_interest, establishment"
    },
    {
      "name": "遠島美容院",
      "types": "hair_care, point_of_interest, establishment"
    },
    {
      "name": "Wajima Fugeshi Post Office",
      "types": "post_office, atm, finance, point_of_interest, establishment"
    },
    {
      "name": "釣船凪紗丸",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "清水酒造店",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "東洋電建（株） 輪島営業所",
      "types": "electrician, point_of_interest, establishment"
    },
    {
      "name": "Kawaimachi",
      "types": "sublocality_level_2, sublocality, political"
    },
    {
      "name": "わらびの写真館 /フォトわらびの",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Sumiyoshi Shrine",
      "types": "tourist_attraction, place_of_worship, point_of_interest, establishment"
    },
    {
      "name": "Wajima Police Station Asaichi Police Box",
      "types": "police, point_of_interest, establishment"
    },
    {
      "name": "工房和美紗美",
      "types": "point_of_interest, store, establishment"
    },
    {
      "name": "（有）大家漆器店",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "（株）リベルテ（Ｌｉｂｅｒｔｅ） 能登営業所",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "和洋菓子 島崎",
      "types": "food, point_of_interest, store, establishment"
    },
    {
      "name": "角知漆器店",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Wajimashi Josei Center",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Kyo Construction",
      "types": "general_contractor, point_of_interest, establishment"
    },
    {
      "name": "（有）畝田屋",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Kaigan-Dōri",
      "types": "lodging, point_of_interest, establishment"
    },
    {
      "name": "㈱まちづくり輪島",
      "types": "home_goods_store, store, point_of_interest, establishment"
    },
    {
      "name": "Iwasaka",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "㈱ケイユーオ",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Secom Wajima",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "（株）高出建築設計事務所",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "washirosa/たたみ靴店",
      "types": "shoe_store, clothing_store, store, point_of_interest, establishment"
    },
    {
      "name": "能登ひばファクトリー（まんぷく丸）",
      "types": "food, point_of_interest, establishment"
    },
    {
      "name": "Nihon Christ Kyodan Wajima Church",
      "types": "church, place_of_worship, point_of_interest, establishment"
    },
    {
      "name": "惣領漆器店",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "大角武志税理士事務所",
      "types": "accounting, lawyer, finance, point_of_interest, establishment"
    },
    {
      "name": "北陸綜合警備保障（株） 輪島事務所",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "金沢港湾空港工事事務所 輪島事務所",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Wajima City Marine Town Arena",
      "types": "point_of_interest, establishment"
    },
    {
      "name": "Shokakuji",
      "types": "place_of_worship, point_of_interest, establishment"
    },
    {
      "name": "zawa coffee",
      "types": "cafe, food, point_of_interest, establishment"
    },
    {
      "name": "カフェ丹 輪島",
      "types": "cafe, food, point_of_interest, establishment"
    },
    {
      "name": "Cafe KABULET",
      "types": "cafe, food, point_of_interest, establishment"
    },
    {
      "name": "Okina",
      "types": "cafe, food, store, point_of_interest, establishment"
    },
    {
      "name": "cafe S",
      "types": "cafe, food, point_of_interest, establishment"
    },
    {
      "name": "Hosi bosi coffee",
      "types": "cafe, food, store, point_of_interest, establishment"
    },
    {
      "name": "中浦屋 輪島わいち本店",
      "types": "tourist_attraction, travel_agency, cafe, food, store, point_of_interest, establishment"
    },
    {
      "name": "Kalpa",
      "types": "cafe, food, store, point_of_interest, establishment"
    },
    {
      "name": "Moco Moco",
      "types": "cafe, food, point_of_interest, store, establishment"
    },
    {
      "name": "海山えがくＣａｆｅ",
      "types": "cafe, food, point_of_interest, establishment"
    },
    {
      "name": "Snack Luce Hostess Bar",
      "types": "bar, point_of_interest, establishment"
    },
    {
      "name": "スナック ボンリブラン",
      "types": "bar, point_of_interest, establishment"
    },
    {
      "name": "Wajima Post Office",
      "types": "post_office, atm, point_of_interest, finance, establishment"
    },
    {
      "name": "丸型ポスト",
      "types": "post_office, point_of_interest, finance, establishment"
    }
  ]
}
```

### 示例输出

```json
{
  "tool": "poi.filter_by_intact",
  "total_input": 307,
  "total_intact": 0,
  "filtered_results": []
}
```

## 适用边界

- **相关性**：★ —— 可用资源点
- **可迁移性**：A
- 纯算法，无权重；换数据直接可用，结果只取决于输入数值本身。

---

[← 返回 80-POI-点位](README.md)　·　[工具总表](../../index/INDEX.md)
