import json, subprocess, struct, os, itertools, sys
TS=os.path.expanduser("~/Library/Application Support/Tesseract/bin/tsrct")
K="/Users/hanifbot/Documents/_0WORK/AI VIDEO/HYPERFRAME/AI UGC PRODUCTION/_editing/fonts/Font"
FACES={
 "ms-black":K+"/Sans-Serif/Montserrat/static/Montserrat-Black.ttf",
 "ms-xbold":K+"/Sans-Serif/Montserrat/static/Montserrat-ExtraBold.ttf",
 "ms-bold":K+"/Sans-Serif/Montserrat/static/Montserrat-Bold.ttf",
 "ms-semi":K+"/Sans-Serif/Montserrat/static/Montserrat-SemiBold.ttf",
 "ms-med":K+"/Sans-Serif/Montserrat/static/Montserrat-Medium.ttf",
 "in-reg":K+"/Sans-Serif/Inter/static/Inter_28pt-Regular.ttf",
 "in-med":K+"/Sans-Serif/Inter/static/Inter_28pt-Medium.ttf",
 "in-semi":K+"/Sans-Serif/Inter/static/Inter_28pt-SemiBold.ttf",
 "in-bold":K+"/Sans-Serif/Inter/static/Inter_28pt-Bold.ttf",
 "in-xbold":K+"/Sans-Serif/Inter/static/Inter_28pt-ExtraBold.ttf",
 "in-ital":K+"/Sans-Serif/Inter/static/Inter_28pt-Italic.ttf",
 "in-boldital":K+"/Sans-Serif/Inter/static/Inter_28pt-BoldItalic.ttf",
 "in-xboldital":K+"/Sans-Serif/Inter/static/Inter_28pt-ExtraBoldItalic.ttf",
 "lato-black":K+"/Sans-Serif/Lato/Lato-Black.ttf",
 "pts-boldital":K+"/Serif/PT_Serif/PTSerif-BoldItalic.ttf",
 "pf-ital":K+"/Serif/Playfair_Display/static/PlayfairDisplay-Italic.ttf",
 "pf-bold":K+"/Serif/Playfair_Display/static/PlayfairDisplay-Bold.ttf",
}
def names(p):
    b=open(p,'rb').read(); n=struct.unpack('>H',b[4:6])[0]; off=None
    for i in range(n):
        e=12+16*i
        if b[e:e+4]==b'name': off=struct.unpack('>I',b[e+8:e+12])[0]
    fmt,cnt,so=struct.unpack('>HHH',b[off:off+6]); out={}
    for i in range(cnt):
        r=off+6+12*i; pid,eid,lid,nid,l,o=struct.unpack('>HHHHHH',b[r:r+12])
        if pid==3 and nid in (1,2,4,6,16,17):
            out.setdefault(nid, b[off+so+o:off+so+o+l].decode('utf-16-be'))
    return out
subprocess.run([TS,"project","create","-p","p.tsrct"],capture_output=True)
info={}
for k,p in FACES.items():
    r=subprocess.run([TS,"project","import-font","-p","p.tsrct","--file",p],capture_output=True,text=True)
    d=json.loads(r.stdout); info[k]=(d,names(p))
def renders(fam,sty):
    doc={"$schema":"https://jerboa.dev/schemas/fx-composition/editable/v1/document.schema.json",
     "composition":{"id":"main","name":"Main","layers":[{"type":"Text","id":1,"name":"t","blendMode":"normal",
      "activeRange":{"start":0,"duration":1000},
      "transform":{"anchorPoint":[540,960],"position":[540,960],"scale":[100,100],"rotation":0,"opacity":100},
      "sourceText":{"text":"Test 30 AI","fontFamily":fam,"fontStyle":sty,"fontSize":80,"fillColor":[1,1,1,1],
       "strokeWidth":0.0,"justification":"center","boxText":True,"boxPosition":[90,800],"boxSize":[900,300]}}]},
     "dimensions":{"width":1080,"height":1920},"duration":1.0,"formatVersion":1}
    json.dump(doc,open("q.json","w"))
    subprocess.run([TS,"project","commit","-p","p.tsrct","--file","q.json"],capture_output=True)
    if os.path.exists("q.png"): os.remove("q.png")
    subprocess.run([TS,"preview","--project","p.tsrct","--time","0.5","--output","q.png"],capture_output=True)
    return os.path.exists("q.png")
res={}
for k,(d,n) in info.items():
    ps=d["font"]; suf=ps.split("-")[-1] if "-" in ps else ""
    spaced="".join((" "+c if c.isupper() and i>0 else c) for i,c in enumerate(suf))
    fams=[ps, d["fontFamily"], n.get(16,""), n.get(1,"")]
    stys=[suf, spaced, n.get(17,""), n.get(2,""), d["fontStyle"]]
    hit=None
    for f,s in itertools.product(dict.fromkeys(fams), dict.fromkeys(stys)):
        if f and s and renders(f,s): hit=(f,s); break
    res[k]=hit; print("%-13s %-28s -> %s"%(k,ps,hit), flush=True)
json.dump(res,open("fontmap.json","w"),indent=1)
