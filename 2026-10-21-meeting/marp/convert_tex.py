#!/usr/bin/env python3
"""Convert this meeting's Beamer template to Marp. Requires Pillow and PyMuPDF.
Reads actual frame order, preserves math and tables; never edits TeX or scripts.
Unsupported LaTeX text commands fail explicitly. npm build consumes generated MD.
"""
from pathlib import Path
import re, shutil, json, hashlib
from PIL import Image
import pymupdf as fitz
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
(OUT/'assets').mkdir(exist_ok=True)

def group(s,i):
    while i<len(s) and s[i].isspace(): i+=1
    assert s[i]=='{',s[i:i+80]
    a=i+1; depth=1; i+=1
    while depth:
        if s[i]=='\\' and i+1<len(s) and s[i+1] in '{}': i+=2; continue
        if s[i]=='{': depth+=1
        elif s[i]=='}': depth-=1
        i+=1
    return s[a:i-1],i

def calls(s,name,n):
    out=[]; pos=0
    while m:=re.search(r'\\'+name+r'(?![a-zA-Z])',s[pos:]):
        a=pos+m.start(); i=pos+m.end(); args=[]
        for _ in range(n): v,i=group(s,i); args.append(v)
        out.append((a,i,args)); pos=i
    return out

def replace(s,name,n,fn):
    for a,b,args in reversed(calls(s,name,n)): s=s[:a]+fn(*args)+s[b:]
    return s

def div(cls,body): return f'<div class="{cls}">\n\n{body}\n\n</div>'

class Renderer:
    def __init__(self): self.tokens=[]; self.math=[]
    def token(self,value):
        self.tokens.append(value); return f'@@ZXQTOKEN{len(self.tokens)-1}QXZ@@'
    def expand(self,s):
        while re.search(r'@@ZXQTOKEN\d+QXZ@@',s):
            s=re.sub(r'@@ZXQTOKEN(\d+)QXZ@@',lambda m:self.tokens[int(m[1])],s)
        return s
    def protect(self,s):
        def math(m):
            v=m[0]; display=v.startswith('\\[')
            v='$$\n'+v[2:-2].strip()+'\n$$' if display else ('$'+v[2:-2]+'$' if v.startswith('\\(') else v)
            self.math.append(v)
            return ('\\par '+self.token(v)+' \\par ') if display else self.token(v)+(' ' if m.string[m.end():m.end()+1].isdigit() else '')
        s=re.sub(r'(?<!\\)%[^\n]*','',s)
        return re.sub(r'\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|(?<!\\)\$(?:\\.|[^$])*?(?<!\\)\$',math,s)
    def text(self,s):
        # All math is opaque before processing text/environment commands.
        for name,fmt in [('textbf','**{}**'),('emph','*{}*'),('textit','*{}*'),('texttt','`{}`'),('textsc','{}')]:
            s=replace(s,name,1,lambda a,f=fmt:self.token(f.format(self.text(a))))
        s=replace(s,'resizebox',3,lambda a,b,c:self.token(self.text(c)))
        for name,n in [('setlength',2),('renewcommand',2),('color',1),('fontsize',2),('rule',2)]:
            s=replace(s,name,n,lambda *a:' ')
        s=re.sub(r'\\vspace\*?\{[^}]*\}',' ',s)
        s=re.sub(r'\\hspace\*?\{([\d.]+)cm\}',lambda m:self.token('&emsp;'*max(1,round(float(m[1])/.33))),s)
        s=re.sub(r'\\(?:small|footnotesize|scriptsize|normalsize|large|Large|bfseries|raggedright|centering|selectfont|vfill|hfill)\b',' ',s)
        s=s.replace('\\par','\n\n').replace('\\\\','<br>').replace('\\&','&').replace('\\%','%').replace('\\$','&#36;').replace('\\_','_').replace('\\ ',' ').replace('\\quad',' ')
        s=s.replace('~',' ').replace('--','–')
        s=s.replace('{','').replace('}','').replace('*',r'\*')
        unknown=re.findall(r'\\[a-zA-Z]+',s)
        assert not unknown, (unknown,s[:700])
        return '\n\n'.join(re.sub(r'\s+',' ',p).strip() for p in re.split(r'\n\s*\n',s) if p.strip())
    def render(self,s):
        # Lists/tables/columns are recursively rendered, so no content is selected by slide number.
        while m:=re.search(r'\\begin\{(itemize|enumerate|tabularx|tabular|columns|column|center)\}(?:\[[^\]]*\])?',s):
            name=m[1]; start=m.start(); i=m.end(); args=[]
            if name=='tabularx':
                _,i=group(s,i); spec,i=group(s,i)
            elif name in ['tabular','column']:
                spec,i=group(s,i)
            else: spec=''
            # Find the matching environment, including nested columns.
            depth=1; e=i
            pattern=r'\\(begin|end)\{'+name+r'\}'
            for end in re.finditer(pattern,s[i:]):
                depth+=1 if end[1]=='begin' else -1
                if depth==0: stop=i+end.start(); e=i+end.end(); break
            assert depth==0,name
            body=s[i:stop]
            if name in ['itemize','enumerate']:
                parts=re.split(r'\\item\b',body)
                result='\n'.join((f'{j}. ' if name=='enumerate' else '- ')+self.render(t).replace('\n\n','<br>') for j,t in enumerate(parts[1:],1))
            elif name.startswith('tabular'):
                body=re.sub(r'\\(?:toprule|midrule|bottomrule)\b','',body)
                rows=[]
                for row in re.split(r'\\\\(?:\[[^\]]*\])?',body):
                    if row.strip(): rows.append([self.text(c).replace('\n\n',' ').replace('|','&#124;') for c in re.split(r'(?<!\\)&',row)])
                cols=max(map(len,rows)); assert all(len(r)==cols for r in rows),rows
                if re.match(r'\d+:',rows[0][0]): rows.insert(0,['']*cols)
                lines=['| '+' | '.join(r)+' |' for r in rows]
                lines.insert(1,'| '+' | '.join(['---']*cols)+' |')
                result='\n'.join(lines)
            elif name=='columns':
                count=len(re.findall(r'\\begin\{column\}',body))
                result=div('columns'+(' three' if count==3 else ''),self.render(body))
            elif name=='column': result=div('column',self.render(body))
            else: result=self.render(body)
            s=s[:start]+'\\par '+self.token(result)+' \\par '+s[e:]
        for name,cls in [('smalllabel','label'),('hint','source')]:
            s=replace(s,name,1,lambda a,c=cls:'\\par '+self.token(div(c,self.text(a)))+' \\par ')
        s=replace(s,'takeaway',1,lambda a:'\\par '+self.token('> '+self.text(a))+' \\par ')
        s=replace(s,'stepcard',3,lambda a,b,c:'\\par '+self.token(div('card',div('tag',self.text(a))+'\n\n## '+self.text(b)+'\n\n'+self.text(c)))+' \\par ')
        s=replace(s,'minibadge',2,lambda a,b:self.token('**'+self.text(b)+'**'))
        return self.text(s)

def figure(path):
    p=ROOT/path
    if p.suffix=='.pdf':
        with fitz.open(p) as doc:
            page=doc[0]; size=(page.rect.width,page.rect.height)
            dest=OUT/'assets'/p.with_suffix('.svg').name
            dest.write_text(page.get_svg_image(text_as_path=True))
    else:
        dest=OUT/'assets'/p.name; shutil.copy2(p,dest)
        size=Image.open(p).size
    return 'assets/'+dest.name,size

manifest={}
for deck in ['ThunderServe','Hetis']:
    source=ROOT/f'2026-10-21-{deck}.tex'; tex=source.read_text()
    frames=re.findall(r'\\begin\{frame\}(?:\[[^]]*\])?(?:\{([^\n]+)\})?(.*?)\\end\{frame\}',tex,re.S)
    slides=[]; titles=[]
    for n,(title,body) in enumerate(frames,1):
        r=Renderer(); protected=r.protect(body); cls='text-slide'
        fig=calls(protected,'paperfigure',5)
        if fig:
            path,cap,left,right,take=fig[0][2]; path=r.expand(path)
            asset,(w,h)=figure(path)
            cap=r.text(cap)
            pic=div('figure',f'![{cap}]({asset})')+'\n\n'+div('caption',cap)
            def bl(s): return '\n'.join('- '+r.text(x) for x in re.split(r'\\item\b',s)[1:])
            if w/h>=1.8:
                cls='figure-wide'; content=pic+'\n\n'+div('columns',div('column',bl(left))+'\n\n'+div('column',bl(right)))+'\n\n> '+r.text(take)
            else:
                cls='figure-side'; content=div('columns',div('column',bl(left)+'\n'+bl(right)+'\n\n> '+r.text(take))+'\n\n'+div('column',pic))
            a,b,_=fig[0]; protected=protected[:a]+r.token(content)+protected[b:]
        else:
            if '\\[' in body: cls+=' math-slide'
            if '\\begin{tabular' in body or len(body)>2200: cls+=' dense'
            if '\\textsc{TabuSearch}' in body or '\\textsc{GenerateConfigs}' in body: cls='algorithm'
            if title.startswith('Algorithm 2:'): cls='algorithm full-algorithm'
            if title=='Full Deployment Plans from Table 3': cls='long-table'
        content=r.expand(r.render(protected))
        if n==1:
            cls='cover'; parts=content.split('\n\n')
            # Cover title is the resizebox content after the label div.
            k=parts.index('</div>')+1
            title=parts[k].strip(); content='\n\n'.join(parts[:k]+['# '+title,'## '+parts[k+1],div('author','\n\n'.join(parts[k+2:]))])
        elif not title:
            cls='closing'; parts=content.split('\n\n'); title=parts[0]; content='# '+title+'\n\n## '+parts[1]+'\n\n'+'\n\n'.join(parts[2:])
        else: content='# '+title+'\n\n'+content
        title=r.expand(r.text(title))
        titles.append(title)
        slides.append(f'<!-- _class: {cls} -->\n<!-- SLIDE {n:02} -->\n\n'+content)
    css=(OUT/'theme.css').read_text()
    header='---\nmarp: true\ntheme: default\nsize: 16:9\npaginate: true\nmath: mathjax\ntitle: '+json.dumps(deck)+'\nauthor: Yu-Jui Liang\nstyle: |\n'+''.join('  '+line+'\n' for line in css.splitlines())+'---\n\n'
    (OUT/f'2026-10-21-{deck}.md').write_text(header+'\n\n---\n\n'.join(slides)+'\n')
    manifest[deck]={'source':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'frames':len(frames),'titles':titles}
    print(deck,len(slides),'slides')
(OUT/'conversion-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
