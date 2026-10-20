import json, re, io, os, sys, pypdf
SRC=sys.argv[1] if len(sys.argv)>1 else '.'  # 第 1–5 批 PDF 所在目录
from reportlab.pdfgen import canvas
from reportlab.lib.colors import white, black
plan=json.load(open('plan.json'))
W,H=595.28,841.89
def overlay(num):
    buf=io.BytesIO(); c=canvas.Canvas(buf,pagesize=(W,H))
    c.setFillColor(white); c.setStrokeColor(white)
    c.rect(250,H-818,95,36,fill=1,stroke=0)    # cover old footer number
    c.setFillColor(black); c.setFont('Times-Roman',10)
    c.drawCentredString(W/2,H-805.5,str(num))
    c.save(); buf.seek(0); return pypdf.PdfReader(buf).pages[0]
w=pypdf.PdfWriter()
front=pypdf.PdfReader('front.pdf')
for p in front.pages: w.add_page(p)
nf=len(front.pages)
k=0
for b in plan:
    # 第 1–5 批：上传的 PDF 放在 SRC 目录；第 6 批：本仓库 ch7/main.pdf
    fp=os.path.join('..',b['file']) if b['file'].startswith('ch7/') else os.path.join(SRC,b['file']); r=pypdf.PdfReader(fp)
    for i in range(b['start'],b['n']):
        k+=1
        pg=r.pages[i]; pg.merge_page(overlay(k)); w.add_page(pg)
# 目录跳转：front.links 每行 = 目录所在页(abspage) 左端x 基线y 右端x 目标页码(sp 单位)
from pypdf.generic import ArrayObject, NumberObject, NameObject, DictionaryObject, FloatObject, NullObject
nlink=0
for line in open('front.links'):
    pg,xl,y,xr,tgt=line.split()
    xl,y,xr=(int(v)/65536 for v in (xl,y,xr))
    ann=DictionaryObject({NameObject('/Type'):NameObject('/Annot'),NameObject('/Subtype'):NameObject('/Link'),
        NameObject('/Rect'):ArrayObject([FloatObject(v) for v in (xl-1,y-3,xr+1,y+10)]),
        NameObject('/Border'):ArrayObject([NumberObject(0)]*3),
        NameObject('/Dest'):ArrayObject([w.pages[nf+int(tgt)-1].indirect_reference,NameObject('/XYZ'),NullObject(),NullObject(),NullObject()])})
    page=w.pages[int(pg)-1]
    if '/Annots' not in page: page[NameObject('/Annots')]=ArrayObject()
    page['/Annots'].append(w._add_object(ann)); nlink+=1
print('toc links',nlink)
# page labels: front roman, content arabic
w.set_page_label(0,nf-1,style='/r')
w.set_page_label(nf,nf+k-1,style='/D',start=1)
# bookmarks
def norm(t):
    t=re.sub(r'^第(\d+)章\s*',r'\1 ',t); t=re.sub(r'^§',r'',t); return t.strip()
w.add_outline_item('封面',0); w.add_outline_item('目录',1)
for b in plan:
    parent=None
    for d,t,p in b['outline']:
        if d==0: parent=w.add_outline_item(norm(t),nf+p)
        else: w.add_outline_item(norm(t),nf+p,parent=parent)
w.add_metadata({'/Title':'丘维声《解析几何》知识点讲解与习题详解（合订本）'})
w.page_mode='/UseOutlines'
w.compress_identical_objects(remove_identicals=True, remove_orphans=True)
with open('raw.pdf','wb') as f: w.write(f)
import subprocess; subprocess.run(['qpdf','--object-streams=generate','--compress-streams=y','--recompress-flate','raw.pdf','丘维声解析几何讲解_合订本.pdf'],check=True); os.remove('raw.pdf')
print('pages',nf+k)
