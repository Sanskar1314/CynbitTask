"""Reproducible ReportLab export; editable Markdown remains authoritative."""
from pathlib import Path
import re,html
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Preformatted,KeepTogether,Flowable
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
ROOT=Path(__file__).resolve().parents[1]
NAVY=colors.HexColor('#102c3a');TEAL=colors.HexColor('#087e8b');GRAY=colors.HexColor('#52636d');PALE=colors.HexColor('#edf4f5')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyCustom',fontName='Helvetica',fontSize=10,leading=15,textColor=NAVY,spaceAfter=9))
styles.add(ParagraphStyle(name='HeadCustom',fontName='Helvetica-Bold',fontSize=16,leading=21,textColor=TEAL,spaceBefore=15,spaceAfter=8,keepWithNext=True))
styles.add(ParagraphStyle(name='SubCustom',fontName='Helvetica-Bold',fontSize=11,leading=15,textColor=NAVY,spaceBefore=10,spaceAfter=5,keepWithNext=True))
styles.add(ParagraphStyle(name='CellCustom',fontName='Helvetica',fontSize=8,leading=11,textColor=NAVY))
styles.add(ParagraphStyle(name='Cover',fontName='Helvetica-Bold',fontSize=34,leading=39,textColor=NAVY,spaceAfter=20))
styles.add(ParagraphStyle(name='SubtitleCustom',fontName='Helvetica',fontSize=20,leading=27,textColor=TEAL,spaceAfter=20))
styles.add(ParagraphStyle(name='CodeCustom',fontName='Courier',fontSize=7.5,leading=11,textColor=NAVY,backColor=PALE,borderPadding=8,spaceAfter=12))

def clean(s):
    s=s.replace('₹','INR ').replace('–','-').replace('—','-').replace('−','-').replace('×',' x ').replace('’',"'").replace('“','"').replace('”','"').replace('→','->').replace('≥','>=').replace('≤','<=')
    return s

def markup(s):
    s=html.escape(clean(s));s=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',s);s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'https?://[^\s<)]+',lambda m:f'<link href="{m.group()}" color="#087e8b">{m.group()}</link>',s)
    return s

class Architecture(Flowable):
    def __init__(self):super().__init__();self.width=480;self.height=200
    def draw(self):
        c=self.canv
        def box(x,y,w,text):
            c.setFillColor(PALE);c.setStrokeColor(TEAL);c.roundRect(x,y,w,35,5,fill=1);c.setFillColor(NAVY);c.setFont('Helvetica',9);c.drawCentredString(x+w/2,y+14,text)
        def arrow(x,y,x2,y2):
            c.setStrokeColor(GRAY);c.line(x,y,x2,y2);c.line(x2,y2,x2-3,y2+5);c.line(x2,y2,x2+3,y2+5)
        box(0,155,145,'Sales + known calendar');box(165,155,145,'Batches + dated receipts');box(330,155,145,'Reviews + catalog aliases')
        box(0,95,145,'Causal baseline / ML forecast');box(165,95,145,'Daily FEFO + order constraints');box(330,95,145,'Qualitative investigation')
        arrow(72,155,72,130);arrow(237,155,237,130);arrow(402,155,402,130)
        c.line(145,112,165,112)
        box(80,20,320,'Owner dashboard: evidence, draft quantities, human review')
        arrow(72,95,140,55);arrow(237,95,237,55);arrow(402,95,340,55)

def footer(c,doc):
    c.saveState();w,h=A4;c.setStrokeColor(colors.HexColor('#dae3e8'));c.line(48,43,w-48,43)
    c.setFont('Helvetica',8);c.setFillColor(GRAY);c.drawString(48,30,'STOCKSENSE  |  Synthetic-data assessment prototype');c.drawRightString(w-48,30,str(doc.page));c.restoreState()

def parse(text):
    lines=text.splitlines();out=[];i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('```'):
            code=[];i+=1
            while i<len(lines) and not lines[i].startswith('```'):code.append(clean(lines[i]));i+=1
            # Wrap long preformatted lines so they cannot run outside the frame.
            import textwrap
            wrapped='\n'.join('\n'.join(textwrap.wrap(x,90,replace_whitespace=False,drop_whitespace=False)) or '' for x in code)
            out.append(Preformatted(wrapped,styles['CodeCustom']));i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+',x) for x in cells):rows.append(cells)
                i+=1
            n=len(rows[0]);width=499
            widths=[width/n]*n
            if n==2:widths=[width*.30,width*.70]
            if n==6:widths=[width*.29,width*.25]+[width*.115]*4
            table=Table([[Paragraph(markup(c),styles['CellCustom']) for c in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('LINEBELOW',(0,0),(-1,0),1,TEAL),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d9e3e7'))]))
            out.extend([table,Spacer(1,12)]);continue
        if line.startswith('#'):
            level=len(line)-len(line.lstrip('#'));txt=line.lstrip('# ').strip()
            out.append(Paragraph(markup(txt),styles['HeadCustom'] if level<=2 else styles['SubCustom']));i+=1;continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#','|','```')):
            # Preserve numbered list items as individual paragraphs.
            if re.match(r'\d+\. ',lines[i].strip()):break
            paragraph.append(lines[i].strip());i+=1
        out.append(Paragraph(markup(' '.join(paragraph)),styles['BodyCustom']))
    return out

def build(source,title,subtitle):
    target=source.with_suffix('.pdf');doc=SimpleDocTemplate(str(target),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=48,bottomMargin=58,title=title,author='StockSense assessment project')
    story=[Spacer(1,65),Paragraph('REVIO<br/>STOCKSENSE',styles['Cover']),Paragraph(title,styles['SubtitleCustom']),Paragraph(subtitle,styles['BodyCustom']),Spacer(1,20),Paragraph('17 October 2026<br/>Independent proposal for Cynbit AI/ML Engineer Internship',styles['BodyCustom']),Spacer(1,20),Paragraph('Research claims, simulated measurements and future proposals are distinguished throughout. No live Revio integration or real-store ROI is claimed.',styles['BodyCustom']),PageBreak(),Paragraph('System at a glance',styles['HeadCustom']),Architecture(),Spacer(1,18)]
    text=source.read_text();text=re.sub(r'^# Revio StockSense\n## [^\n]+\n','',text)
    story+=parse(text);doc.build(story,onFirstPage=footer,onLaterPages=footer);print(target)

if __name__=='__main__':
    combined='# Revio StockSense\n## Complete Project Explanation\n\nA learning companion covering architecture, model reasoning, inventory examples, decisions and interview practice. All results refer to synthetic demonstration data.\n\n'
    for title,file in [('Part I - End-to-end walkthrough','docs/Project_Walkthrough.md'),('Part II - Engineering decisions','docs/Engineering_Decision_Log.md'),('Part III - Interview preparation','docs/Interview_Preparation.md')]:
        content=(ROOT/file).read_text();content=re.sub(r'^# [^\n]+\n','',content);combined+='\n# '+title+'\n'+content+'\n'
    path=ROOT/'reports/Complete_Project_Explanation.md';path.write_text(combined)
    build(ROOT/'reports/AI_Opportunity_Report.md','AI Opportunity Report','Business fit, evidence, opportunity comparison and validation roadmap.')
    build(ROOT/'reports/Technical_Approach_Report.md','Technical Approach Report','Data, causal features, chronological evaluation and inventory mathematics.')
    build(path,'Complete Project Explanation','An accessible walkthrough with worked examples, engineering decisions and40 interview questions.')
