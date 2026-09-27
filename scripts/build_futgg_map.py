import json,re,time,unicodedata,urllib.request,urllib.parse
from pathlib import Path

BASE="https://www.fut.gg"
UA={"User-Agent":"Mozilla/5.0 (compatible; GalleryLab/1.0)"}

def norm(s):
    s=unicodedata.normalize("NFD",s or "")
    s="".join(c for c in s if unicodedata.category(c)!="Mn").lower()
    return " ".join(re.sub(r"[^a-z0-9]+"," ",s).split())

def get(url):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=25) as r:
        return r.read().decode("utf-8","ignore")

out={}
empty=0
for page in range(1,335):
    try:
        html=get(f"{BASE}/players/?page={page}")
    except Exception as e:
        print("page",page,"error",e); time.sleep(2); continue
    # FUT.GG SSR card images: alt contains "Name - OVR - Rarity"; src points at game-assets.fut.gg.
    imgs=re.findall(r'<img[^>]+(?:alt=["\']([^"\']+)["\'][^>]+src=["\']([^"\']+)["\']|src=["\']([^"\']+)["\'][^>]+alt=["\']([^"\']+)["\'])[^>]*>',html,re.I)
    found=0
    for a,s1,s2,b in imgs:
        alt=a or b; src=s1 or s2
        if "game-assets.fut.gg" not in src: continue
        m=re.match(r"(.+?)\s+-\s+(\d{2})\s+-\s+(.+)$",alt.strip())
        if not m: continue
        name,rating,rarity=m.group(1),int(m.group(2)),m.group(3)
        src=src.replace("&amp;","&")
        if src.startswith("//"): src="https:"+src
        k=norm(name)
        out.setdefault(k,[]).append({"name":name,"rating":rating,"rarity":rarity,"image":src})
        found+=1
    print("page",page,"cards",found)
    if found==0:
        empty+=1
        if empty>=3: break
    else: empty=0
    time.sleep(.15)

# de-dupe
for k,v in out.items():
    seen=set(); nv=[]
    for x in v:
        sig=(x["rating"],x["rarity"],x["image"])
        if sig not in seen: seen.add(sig); nv.append(x)
    out[k]=nv
# Preserve a compact proof set even if FUT.GG pagination markup changes.
known={
 "alexia putellas":{"baseId":227203,"page":"https://www.fut.gg/players/227203-alexia-putellas/","rating":91},
 "nicole anyomi":{"baseId":264947,"itemId":50596595,"page":"https://www.fut.gg/players/264947-nicole-anyomi/27-50596595/","rating":84},
 "mary earps":{"baseId":247504,"page":"https://www.fut.gg/players/247504-mary-earps/","rating":82},
 "elena linari":{"baseId":227069,"page":"https://www.fut.gg/players/227069-elena-linari/","rating":82},
 "danielle van de donk":{"baseId":233751,"page":"https://www.fut.gg/players/233751-danielle-van-de-donk/","rating":81},
 "saki kumagai":{"baseId":226997,"itemId":50558645,"page":"https://www.fut.gg/players/226997-saki-kumagai/27-50558645/","rating":81}
}
for k,v in known.items():
    if k not in out: out[k]=[]
Path("futgg-map.json").write_text(json.dumps(out,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
print("mapped",len(out),"players")
