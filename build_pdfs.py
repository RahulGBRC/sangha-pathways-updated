from pathlib import Path
import json,re,html,math
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from PIL import Image
SITE=Path(__file__).parent
OUT=SITE/'dist/itineraries/downloads'
OUT.mkdir(parents=True,exist_ok=True)
for name,file in [('Sans','DejaVuSans.ttf'),('SansBold','DejaVuSans-Bold.ttf'),('Serif','DejaVuSerif.ttf')]:
 pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
W,H=A4;M=43;CW=W-2*M
GREEN=HexColor('#203e35');GOLD=HexColor('#c49b55');MUTED=HexColor('#657064');PAPER=HexColor('#f8f7f2');LINE=HexColor('#dce0d3')
ST={
 'body':ParagraphStyle('body',fontName='Sans',fontSize=9.5,leading=14,textColor=GREEN),
 'day':ParagraphStyle('day',fontName='Serif',fontSize=17,leading=21,textColor=GREEN),
 'small':ParagraphStyle('small',fontName='Sans',fontSize=8,leading=12,textColor=MUTED),
 'cover':ParagraphStyle('cover',fontName='Serif',fontSize=34,leading=39,textColor=GREEN),
 'intro':ParagraphStyle('intro',fontName='Sans',fontSize=10.5,leading=16,textColor=MUTED),
 'route':ParagraphStyle('route',fontName='Sans',fontSize=8.5,leading=13,textColor=GREEN),
}
def clean(s):return re.sub('[\u2010-\u2015]','-',s).replace('\u00a0',' ')
def para(c,text,x,y,width,style='body'):
 p=Paragraph(html.escape(clean(text)),ST[style]);pw,ph=p.wrap(width,H)
 if c:p.drawOn(c,x,y-ph)
 return ph

def label(c,text,x,y,color=GOLD,size=8):
 c.setFillColor(color);c.setFont('SansBold',size);c.drawString(x,y,text)
def line(c,y):c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,y,W-M,y)
def photo(c,path,x,y,w,h):
 im=Image.open(path);iw,ih=im.size
 ratio=max(w/iw,h/ih);dw,dh=iw*ratio,ih*ratio
 c.saveState();p=c.beginPath();p.rect(x,y,w,h);c.clipPath(p,stroke=0,fill=0)
 c.drawImage(ImageReader(im),x-(dw-w)/2,y-(dh-h),width=dw,height=dh);c.restoreState()
def header(c,t):
 c.setFillColor(PAPER);c.rect(0,0,W,H,fill=1,stroke=0)
 c.drawImage(str(SITE/'dist/images/sanghapathways-logo.jpeg'),M,H-86,54,55,preserveAspectRatio=True,mask='auto')
 label(c,'SANGHAPATHWAYS TOUR INDIA',M+69,H-49,GREEN,10)
 c.setFont('Sans',8);c.setFillColor(MUTED);c.drawString(M+69,H-66,'BUDDHIST SACRED PILGRIMAGE')
 label(c,f'{t["nights"]} NIGHTS / {t["duration"]} DAYS',W-M-109,H-89,GOLD,8)
 line(c,H-101)
def footer(c,num,total):
 line(c,66)
 label(c,'SANGHAPATHWAYS TOUR INDIA',M,51,GREEN,7.8)
 c.setFont('Sans',7.6);c.setFillColor(MUTED);c.drawString(M,37,'+91 91555 11029  |  +91 87458 41029  |  Rajapur, Bodh Gaya, India')
 c.drawRightString(W-M,51,f'{num:02d} / {total:02d}')
 c.linkURL('tel:+919155511029',(M,30,M+105,45),relative=0)
 c.linkURL('tel:+918745841029',(M+110,30,M+210,45),relative=0)
 c.setFillColor(GOLD);c.drawRightString(W-M,22,'Walk gently. Travel thoughtfully.')
def blockheight(d):
 height=para(None,d['title'],0,0,CW-66,'day')+15
 for a in d['activities']:height+=para(None,a,0,0,CW-79)+5
 height+=12+max(24,para(None,'Meals: '+d['meals'],0,0,CW-90,'small')+12)+23
 return height

def drawday(c,d,y):
 x=M+66
 label(c,'DAY',M,y-5,GOLD,8);c.setFont('Serif',27);c.setFillColor(GREEN);c.drawString(M,y-35,f'{d["number"]:02d}')
 h=para(c,d['title'],x,y,CW-66,'day');y-=h+15
 for a in d['activities']:
  c.setFillColor(GOLD);c.circle(x+2,y-5,1.7,fill=1,stroke=0)
  h=para(c,a,x+13,y,CW-79);y-=h+5
 y-=12
 mealheight=max(24,para(None,'Meals: '+d['meals'],0,0,CW-90,'small')+12)
 c.setFillColor(HexColor('#ecf0e5'));c.roundRect(x,y-mealheight,CW-66,mealheight,3,fill=1,stroke=0)
 para(c,'Meals: '+d['meals'],x+10,y-6,CW-86,'small')
 return y-mealheight-23

data=json.loads((SITE/'itineraries.json').read_text())
for t in data:
 # Pack whole days so that a daily schedule never runs over a page.
 groups=[];group=[];used=0;available=H-235
 for d in t['days']:
  h=blockheight(d)
  if group and (used+h>available or len(group)==3):groups.append(group);group=[];used=0
  group.append(d);used+=h
 if group:groups.append(group)
 if len(groups)>1 and len(groups[-1])==1 and len(groups[-2])>=3:
  groups[-1].insert(0,groups[-2].pop())
 total=1+len(groups)
 path=OUT/f'Sanghapathways_Tour_India_{t["code"]}.pdf'
 c=canvas.Canvas(str(path),pagesize=A4);c.setTitle(f'Sanghapathways Tour India | {t["nights"]} Nights / {t["duration"]} Days Buddhist Pilgrimage');c.setAuthor('Sanghapathways Tour India');c.setSubject(t['title'])
 header(c,t)
 photo(c,SITE/f'dist/images/{t["image"]}.jpg',M,H-354,CW,234)
 c.setFillColor(GREEN);c.rect(M,H-354,205,30,fill=1,stroke=0);label(c,t['region'].upper()+'  /  PILGRIMAGE',M+13,H-343,white,8)
 credits={'bodhgaya':('Rohit Sharma','4.0','https://commons.wikimedia.org/wiki/File:Mahabodhi_temple_complex,_Bodhgaya_23.jpg'),'sarnath':('Ken Wieland','2.0','https://commons.wikimedia.org/wiki/File:Dhamekh_Stupa,_where_the_Buddha_gave_the_first_sermon_on_the_Four_Noble_Truths_and_the_Eightfold_Path_to_his_five_disciples,_Sarnath.jpg'),'lumbini':('Sashank.gaudel','4.0','https://commons.wikimedia.org/wiki/File:MayaDevi_Temple,_Lumbini.jpg')}
 who,license,source=credits[t['image']]
 c.setFont('Sans',6.5);c.setFillColor(MUTED);c.drawString(M,H-365,f'Photo: {who} / CC BY-SA {license}. Resized and cropped; image retains its license.')
 c.linkURL(source,(M,H-369,M+180,H-358),relative=0)
 c.linkURL('https://creativecommons.org/licenses/by-sa/'+license+'/',(M+181,H-369,W-M,H-358),relative=0)
 y=H-387
 titleheight=para(c,t['title'],M,y,CW,'cover');y-=titleheight+15
 y-=para(c,t['intro'],M,y,CW,'intro')+19
 label(c,'YOUR ROUTE',M,y,GOLD,8);y-=13
 y-=para(c,'  >  '.join(t['route']),M,y,CW,'route')+17
 line(c,y);y-=20
 c.setFont('Sans',9);c.setFillColor(GREEN);c.drawString(M,y,'Start: '+t['start']);c.drawRightString(W-M,y,'Finish: '+t['end']);y-=28
 # Contact details are part of every cover, with active links.
 c.setFillColor(GREEN);c.roundRect(M,y-46,CW,46,3,fill=1,stroke=0)
 label(c,'PLAN THIS JOURNEY WITH US',M+13,y-17,white,8)
 c.setFont('Sans',9.5);c.setFillColor(HexColor('#f2d39e'));c.drawString(M+13,y-34,'+91 91555 11029  |  +91 87458 41029')
 c.linkURL('https://wa.me/919155511029',(M,y-46,W-M,y),relative=0)
 footer(c,1,total);c.showPage()
 for i,g in enumerate(groups):
  header(c,t);y=H-124
  label(c,'THE JOURNEY / DAY BY DAY',M,y,GOLD,8);y-=26
  for d in g:y=drawday(c,d,y)
  assert y>82,(t['code'],i,y)
  if i==len(groups)-1:
   note='Please confirm dates, accommodation, meal arrangements, inclusions, pricing and booking terms with our team. Your itinerary is subject to local conditions and the final agreed programme.'
   nh=para(None,note,0,0,CW,'small')
   if y-nh>245:para(c,note,M,y-9,CW,'small')
   else:para(c,note,M,y-9,CW,'small')
   if y-nh>240:
    c.setFillColor(HexColor('#e9ede1'));c.roundRect(M,97,CW,112,4,fill=1,stroke=0)
    label(c,'YOUR NEXT STEP',M+17,189,GOLD,8)
    para(c,'Let us plan the details.',M+17,173,CW-34,'day')
    para(c,'Share your travel dates, group size and preferred arrangements.',M+17,142,CW-34,'small')
    c.setFont('SansBold',9);c.setFillColor(GREEN);c.drawString(M+17,112,'WhatsApp: +91 91555 11029   |   Call: +91 87458 41029')
    c.linkURL('https://wa.me/919155511029',(M,97,W-M,135),relative=0)
  footer(c,i+2,total);c.showPage()
 c.save()
 print(path.name, 'pages:',total,'days:',len(t['days']))
