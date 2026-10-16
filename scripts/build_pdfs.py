"""Build full Markdown reports, diagrams and PDF contact sheets reproducibly."""
from __future__ import annotations
import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, Preformatted, KeepTogether
from reportlab.pdfgen.canvas import Canvas
from pypdf import PdfReader
import pypdfium2 as pdfium
from PIL import Image as PILImage, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT/'tmp/pdfs'
TMP.mkdir(parents=True, exist_ok=True)
DIAGRAMS = {
 'architecture': ('Implemented system architecture', ['Browser / Streamlit UI','Validated CSV or review text','Cached sentiment pipeline','Support and confidence check','Explicit routing and explanations','Queue, location chart, CSV export']),
 'data_flow': ('End-to-end review data flow', ['Text or UTF-8 CSV','Schema and content validation','Partial contact redaction','Sentiment model plus policy rules','Human inspects evidence','Filtered, formula-safe CSV']),
 'preprocessing': ('Benchmark preprocessing', ['Three attributed UCI text files','Join lines until final-tab label','Unicode / whitespace / case','Contact redaction and text hashes','Remove conflicts and duplicates','Fixed source-label stratified splits']),
 'training': ('Training and evaluation workflow', ['Train / validation / test split','Fit vocabulary and model on train','Select C on validation F1','Select threshold on validation','Freeze model; score untouched test','Baselines, errors and domain stress']),
 'inference': ('Inference and review policy', ['Validate and normalize text','TF-IDF vector and logistic probability','Script / vocabulary / confidence guard','Sentiment suggestion or uncertain','Safety / uncertainty / negative / routine','Exact feature contributions']),
 'interaction': ('User interaction', ['Open local application','Choose inbox, single review or evidence','Upload CSV or enter review','See validation error or model result','Inspect reasons and filter queue','Download results for human review']),
 'deployment': ('Implemented local deployment', ['Python 3.12 virtual environment','Pinned app dependencies','Bundled public corpus and code','Local Streamlit on 127.0.0.1:8501','Browser session and cached model','No production API or database']),
 'external': ('External data boundary', ['Optional download script','Public UCI HTTPS archive','Allowlisted files and SHA-256 hashes','Attributed local raw dataset','Offline training and application','No external runtime integrations']),
}

def diagrams():
    folder=ROOT/'assets/diagrams';folder.mkdir(parents=True,exist_ok=True)
    for key,(title,nodes) in DIAGRAMS.items():
        lines=['flowchart TD']
        for i,node in enumerate(nodes):
            lines.append(f'  N{i}["{node}"]')
            if i:lines.append(f'  N{i-1} --> N{i}')
        (folder/f'{key}.mmd').write_text('\n'.join(lines)+'\n')
        path=TMP/f'{key}.pdf'
        c=Canvas(str(path),pagesize=(540,330))
        c.setFillColor(colors.HexColor('#17243b'));c.setFont('Helvetica-Bold',16);c.drawString(20,305,title)
        positions=[(20,220),(290,220),(290,130),(20,130),(20,40),(290,40)]
        for i,((x,y),node) in enumerate(zip(positions,nodes)):
            c.setFillColor(colors.HexColor('#e7f3f0'));c.setStrokeColor(colors.HexColor('#0f766e'))
            c.roundRect(x,y,230,58,8,fill=1,stroke=1)
            p=Paragraph(f'<b>{i+1:02d}</b>  {html.escape(node)}',ParagraphStyle('node',fontName='Helvetica',fontSize=11,leading=14,textColor=colors.HexColor('#17243b')))
            _,h=p.wrap(205,45);p.drawOn(c,x+12,y+(58-h)/2)
            if i<5:
                nx,ny=positions[i+1]
                if ny==y:
                    start=(x+230,y+29) if nx>x else (x,y+29)
                    end=(nx,y+29) if nx>x else (nx+230,y+29)
                else:start=(x+115,y);end=(nx+115,ny+58)
                c.setStrokeColor(colors.HexColor('#0f766e'));c.line(*start,*end)
                ex,ey=end
                if ny!=y:c.line(ex,ey,ex-4,ey+6);c.line(ex,ey,ex+4,ey+6)
                elif nx>x:c.line(ex,ey,ex-6,ey-4);c.line(ex,ey,ex-6,ey+4)
                else:c.line(ex,ey,ex+6,ey-4);c.line(ex,ey,ex+6,ey+4)
        c.save()
        doc=pdfium.PdfDocument(str(path));doc[0].render(scale=2).to_pil().save(folder/f'{key}.png');doc.close()

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyCustom',fontName='Helvetica',fontSize=10,leading=15,spaceAfter=8,textColor=colors.HexColor('#27354a'),splitLongWords=True))
styles.add(ParagraphStyle(name='TableCustom',parent=styles['BodyCustom'],fontSize=7.7,leading=10,spaceAfter=0))
styles.add(ParagraphStyle(name='CodeCustom',fontName='Courier',fontSize=7,leading=10,spaceAfter=10,backColor=colors.HexColor('#f0f3f7'),borderPadding=7))
for name,size in [('Heading1',25),('Heading2',16),('Heading3',12)]:
    styles[name].fontName='Helvetica-Bold';styles[name].fontSize=size;styles[name].leading=size*1.3
    styles[name].textColor=colors.HexColor('#0f766e' if name!='Heading1' else '#17243b')
    styles[name].spaceBefore=16;styles[name].spaceAfter=9;styles[name].keepWithNext=True

def clean(s):
    return s.replace('→',' -> ').replace('≥','>=').replace('≤','<=').replace('—',' - ').replace('–','-').replace('’',"'").replace('“','"').replace('”','"').replace('◈','')

def inline(s):
    s=html.escape(clean(s))
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',s)
    s=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<link href="\2" color="#0f766e">\1</link>',s)
    return s

def footer(canvas,doc):
    width,height=A4
    canvas.setStrokeColor(colors.HexColor('#d7dfe8'));canvas.line(45,42,width-45,42)
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#617085'))
    canvas.drawString(45,29,'CYNBIT ASSESSMENT  |  REVIO SIGNAL DESK  |  16 OCT 2026')
    canvas.drawRightString(width-45,29,str(doc.page))

def parse_markdown(path):
    lines=path.read_text().splitlines();flow=[];i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('```'):
            block=[];i+=1
            while i<len(lines) and not lines[i].startswith('```'):
                # Wrap long commands for readable PDF, originals remain exact in Markdown.
                import textwrap
                block.extend(textwrap.wrap(clean(lines[i]),width=94,replace_whitespace=False,drop_whitespace=False) or [''])
                i+=1
            flow.append(Preformatted('\n'.join(block),styles['CodeCustom']));i+=1;continue
        image=re.fullmatch(r'!\[(.*?)\]\((.*?)\)',line)
        if image:
            p=(path.parent/image.group(2)).resolve()
            if not p.exists():raise FileNotFoundError(p)
            with PILImage.open(p) as img:w,h=img.size
            width=490;flow.append(Image(str(p),width=width,height=width*h/w));flow.append(Spacer(1,10));i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+',x) for x in cells):rows.append(cells)
                i+=1
            n=len(rows[0]);weights=[1]*n
            if n==4:weights=[1.4,2.2,2.2,1]
            if n==8:weights=[2.4,1,1,1,1,1,1,1]
            if n==2:weights=[1.6,3]
            widths=[490*w/sum(weights) for w in weights]
            rows=[[Paragraph(inline(c),styles['TableCustom']) for c in row] for row in rows]
            table=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dcefe9')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#d6dfe9')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f7fa')])]))
            flow.extend([table,Spacer(1,12)]);continue
        if line.startswith('#'):
            level=len(line)-len(line.lstrip('#'));text=line[level:].strip()
            flow.append(Paragraph(inline(text),styles[f'Heading{min(level,3)}']));i+=1;continue
        if re.match(r'^\d+\. ', line):
            flow.append(Paragraph(inline(line),styles['BodyCustom']));i+=1;continue
        if line.startswith('- '):
            flow.append(Paragraph('&#8226; '+inline(line[2:]),styles['BodyCustom']));i+=1;continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','```','- ','![')) and not re.match(r'^\d+\. ',lines[i]):
            paragraph.append(lines[i].strip());i+=1
        flow.append(Paragraph(inline(' '.join(paragraph)),styles['BodyCustom']))
    return flow

def build(path):
    target=path.with_suffix('.pdf')
    doc=SimpleDocTemplate(str(target),pagesize=A4,rightMargin=45,leftMargin=45,topMargin=40,bottomMargin=55,
                          title=path.stem.replace('_',' '),author='Cynbit internship assessment project')
    doc.build(parse_markdown(path),onFirstPage=footer,onLaterPages=footer)
    reader=PdfReader(target)
    text='\n'.join(p.extract_text() or '' for p in reader.pages)
    (TMP/(path.stem+'.txt')).write_text(text)
    pdf=pdfium.PdfDocument(str(target))
    thumbs=[]
    for index in range(len(pdf)):
        page=pdf[index].render(scale=.6).to_pil().convert('RGB')
        page.thumbnail((250,355))
        tile=PILImage.new('RGB',(270,385),'#dce2e8');tile.paste(page,((270-page.width)//2,10))
        ImageDraw.Draw(tile).text((10,367),f'Page {index+1}',fill='black');thumbs.append(tile)
    for start in range(0,len(thumbs),12):
        group=thumbs[start:start+12];sheet=PILImage.new('RGB',(1080,385*((len(group)+3)//4)),'white')
        for k,tile in enumerate(group):sheet.paste(tile,((k%4)*270,(k//4)*385))
        sheet.save(TMP/f'{path.stem}_contact_{start//12+1}.png')
    pdf.close()
    print(f'{target.name}: {len(reader.pages)} pages, {len(text)} extracted characters')

if __name__=='__main__':
    diagrams()
    consolidated=['# Complete Project Explanation\n\nRevio Signal Desk | Learning and interview companion | 16 October 2026\n']
    for name in ['reports/Technical_Approach_Report.md','docs/Engineering_Decision_Log.md','docs/Project_Walkthrough.md','docs/Interview_Preparation.md','docs/Demo_Walkthrough.md']:
        consolidated.append((ROOT/name).read_text())
    path=ROOT/'reports/Complete_Project_Explanation.md';path.write_text('\n\n'.join(consolidated))
    for name in ['AI_Opportunity_Report','Technical_Approach_Report','Complete_Project_Explanation']:
        build(ROOT/'reports'/f'{name}.md')
