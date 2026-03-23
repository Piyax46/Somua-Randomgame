import json, urllib.request

url = "https://ddragon.leagueoflegends.com/cdn/15.6.1/data/en_US/champion.json"
data = json.loads(urllib.request.urlopen(url).read())

champions = []
for cid, cdata in sorted(data["data"].items(), key=lambda x: x[1]["name"]):
    champ_id = cdata["id"]
    champions.append({
        "name": cdata["name"],
        "key": champ_id,
        "img": "https://ddragon.leagueoflegends.com/cdn/15.6.1/img/champion/" + champ_id + ".png"
    })

print("Total LoL champions:", len(champions))

with open("d:/backup/random/data/lol.json", "w", encoding="utf-8") as f:
    json.dump({
        "champions": champions,
        "lanes": [
            {"id": "top", "name": "Top", "icon": "\U0001F6E1\uFE0F", "color": "#22c55e"},
            {"id": "jungle", "name": "Jungle", "icon": "\U0001F33F", "color": "#16a34a"},
            {"id": "mid", "name": "Mid", "icon": "\U0001F3AF", "color": "#f59e0b"},
            {"id": "adc", "name": "ADC", "icon": "\U0001F3F9", "color": "#ef4444"},
            {"id": "support", "name": "Support", "icon": "\U0001F496", "color": "#8b5cf6"}
        ]
    }, f, indent=2, ensure_ascii=False)
print("Done!")
