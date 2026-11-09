"""Visualizador del árbol de derivación de Jacaranda.

Muestra el árbol que genera el parser, sin volver a analizar la entrada.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import tkinter.font as tkfont
from xml.sax.saxutils import escape


BG = '#FAF7FD'
PURPLE = '#7553A6'
DARK = '#51356F'
LEAF = '#287A62'
EDGE = '#B49ACA'


def tree_layout(root, char_width=9.5, pad=44, row_height=92,
                measure_text=None, sibling_gap=54):
    """Calcula el espacio que necesita cada rama para que los textos no se encimen.

    Si se puede, usa el ancho real de las letras que muestra Tkinter.
    """
    def visible_children(node):
        return [c for c in getattr(node, 'children', [])
                if str(c.symbol) != 'EOF']

    def text_width(label):
        if measure_text is not None:
            return float(measure_text(label))
        return len(label) * char_width

    widths = {}

    def measure(node):
        children = visible_children(node)
        own_width = max(76.0, text_width(str(node.symbol)) + pad)
        children_width = (sum(measure(c) for c in children)
                          + max(0, len(children) - 1) * sibling_gap)
        widths[id(node)] = max(own_width, children_width)
        return widths[id(node)]

    measure(root)
    vertices, connections = [], []

    def place(node, left, depth, parent=None):
        children = visible_children(node)
        available = widths[id(node)]
        cx = left + available / 2
        cy = 58 + depth * row_height
        index = len(vertices)
        vertices.append((cx, cy, str(node.symbol), not children))
        
        if parent is not None:
            connections.append((parent, index))
        children_width = (sum(widths[id(c)] for c in children)

                          + max(0, len(children) - 1) * sibling_gap)
        cursor = left + (available - children_width) / 2

        for child in children:
            place(child, cursor, depth + 1, index)
            cursor += widths[id(child)] + sibling_gap

    place(root, 48, 0)

    content_width = widths[id(root)] + 96
    content_height = max((v[1] for v in vertices), default=60) + 68

    return vertices, connections, int(content_width), int(content_height)


def export_svg(filename, layout):
    vertices, connections, width, height = layout
    def xml(s): return escape(s, {'"': '&quot;', "'": '&apos;'})
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             f'<rect width="100%" height="100%" fill="{BG}"/>']

    for p,c in connections:
        x1,y1,_,_ = vertices[p]; x2,y2,_,_ = vertices[c]
        lines.append(f'<path d="M{x1:.1f},{y1+12:.1f} C{x1:.1f},{(y1+y2)/2:.1f} {x2:.1f},{(y1+y2)/2:.1f} {x2:.1f},{y2-12:.1f}" fill="none" stroke="{EDGE}" stroke-width="1.6"/>')

    for x,y,label,leaf in vertices:
        lines.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="middle" fill="{LEAF if leaf else DARK}" font-family="Arial,sans-serif" font-size="13" font-weight="{400 if leaf else 600}">{xml(label)}</text>')

    lines.append('</svg>')

    with open(filename,'w',encoding='utf-8') as out:
        out.write('\n'.join(lines))


def export_raster(filename, layout, image_format='PNG', scale=2):
    """Guarda el árbol completo como PNG o JPG, usando Pillow.
    Se exporta todo el árbol, no solo la parte visible en la ventana.
    """
    from PIL import Image, ImageDraw, ImageFont

    vertices, connections, width, height = layout
    pixel_width, pixel_height = int(width * scale), int(height * scale)

    if pixel_width * pixel_height > 80_000_000:
        raise ValueError('The tree is too large to export at this resolution.')

    img = Image.new('RGB', (pixel_width, pixel_height), BG)
    draw = ImageDraw.Draw(img)

    font_candidates = [
        Path('C:/Windows/Fonts/segoeui.ttf'),
        Path('C:/Windows/Fonts/arial.ttf'),
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
    ]

    bold_candidates = [
        Path('C:/Windows/Fonts/segoeuib.ttf'),
        Path('C:/Windows/Fonts/arialbd.ttf'),
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
    ]

    def load_font(candidates):
        for candidate in candidates:
            if candidate.is_file():
                try:
                    return ImageFont.truetype(str(candidate), 13 * scale)

                except OSError:
                    continue

        return ImageFont.load_default()
    
    normal_font = load_font(font_candidates)
    bold_font = load_font(bold_candidates)

    def bezier(start, control1, control2, end):
        coords = []
        for i in range(31):
            t = i / 30
            u = 1 - t
            x = u**3*start[0] + 3*u*u*t*control1[0] + 3*u*t*t*control2[0] + t**3*end[0]
            y = u**3*start[1] + 3*u*u*t*control1[1] + 3*u*t*t*control2[1] + t**3*end[1]
            coords.append((round(x*scale),round(y*scale)))
        return coords

    for parent, child in connections:
        x1,y1,_,_ = vertices[parent]
        x2,y2,_,_ = vertices[child]
        mid=(y1+y2)/2

        draw.line(bezier((x1,y1+12),(x1,mid),(x2,mid),(x2,y2-12)),
                  fill=EDGE,width=max(2,int(1.6*scale)),joint='curve')

    for x,y,label,leaf in vertices:

        draw.text((x*scale,y*scale),label,anchor='mm',
                  fill=LEAF if leaf else DARK,font=normal_font if leaf else bold_font)

    if image_format == 'JPEG':
        img.save(filename, format='JPEG', quality=95, subsampling=0)

    else:
        img.save(filename, format='PNG')


class ParseTreeViewer(tk.Toplevel):
    """Ventana para explorar el árbol y guardarlo en distintos formatos."""
    def __init__(self, master, parse_tree):
        super().__init__(master)
        self.title('Jacaranda | Parse Tree')
        self.geometry('1120x690')
        self.minsize(650,400)
        self.configure(bg=BG)
        self.tree = parse_tree
        self.zoom = 1.0

        self.node_font = tkfont.Font(family='Segoe UI', size=12, weight='bold')
        self.leaf_font = tkfont.Font(family='Segoe UI', size=12)
        self.layout = tree_layout(self.tree, measure_text=lambda text: max(
            self.node_font.measure(text), self.leaf_font.measure(text)))

        header = tk.Frame(self,bg=PURPLE,padx=22,pady=15)
        header.pack(fill='x')

        tk.Label(header,text='Jacaranda  ·  Parse Tree',font=('Segoe UI',19,'bold'),fg='white',bg=PURPLE).pack(anchor='w')
        tk.Label(header,text='Parse tree generated by Jacaranda',font=('Segoe UI',10),fg='#EEE4FA',bg=PURPLE).pack(anchor='w')

        controls = tk.Frame(self,bg=BG,padx=14,pady=10)
        controls.pack(fill='x')

        for text,fn in [('−',lambda:self.set_zoom(self.zoom/1.2)),('100%',lambda:self.set_zoom(1.0)),('+',lambda:self.set_zoom(self.zoom*1.2)),('Center root',self.center_root),('Export PNG',lambda:self.save_raster('PNG')),('Export JPG',lambda:self.save_raster('JPEG')),('Export SVG',self.save_svg)]:
            ttk.Button(controls,text=text,command=fn).pack(side='left',padx=(0,8))

        self.scale_label=tk.Label(controls,text='100%',font=('Segoe UI',10),bg=BG,fg=DARK)
        self.scale_label.pack(side='right')

        host=tk.Frame(self,bg=BG)
        host.pack(fill='both',expand=True,padx=12,pady=(0,12))
        
        self.canvas=tk.Canvas(host,bg=BG,highlightthickness=0)

        xs=ttk.Scrollbar(host,orient='horizontal',command=self.canvas.xview)
        ys=ttk.Scrollbar(host,orient='vertical',command=self.canvas.yview)

        self.canvas.configure(xscrollcommand=xs.set,yscrollcommand=ys.set)

        host.rowconfigure(0,weight=1);host.columnconfigure(0,weight=1)

        self.canvas.grid(row=0,column=0,sticky='nsew')

        ys.grid(row=0,column=1,sticky='ns');xs.grid(row=1,column=0,sticky='ew')

        self.canvas.bind('<Control-MouseWheel>',self._wheel)

        self.canvas.bind('<ButtonPress-1>',lambda e:self.canvas.scan_mark(e.x,e.y))
        self.canvas.bind('<B1-Motion>',lambda e:self.canvas.scan_dragto(e.x,e.y,gain=1))
        self.draw()

        self.after_idle(self.center_root)

    def center_root(self):
        """Vuelve a colocar la raíz del árbol en el centro de la vista."""
        self.update_idletasks()

        vertices, _, width, height = self.layout
        if not vertices:
            return

        viewport = max(1, self.canvas.winfo_width())
        target_x = vertices[0][0] * self.zoom - viewport / 2
        scrollable = max(0.0, width * self.zoom - viewport)

        if scrollable:
            self.canvas.xview_moveto(max(0.0, min(1.0, target_x / scrollable)))

        else:
            self.canvas.xview_moveto(0)

        self.canvas.yview_moveto(0)

    def _wheel(self,event):
        self.set_zoom(self.zoom*(1.15 if event.delta>0 else 1/1.15))


    def set_zoom(self,new):
        self.zoom=max(0.35,min(2.4,new))
        self.scale_label.configure(text=f'{self.zoom*100:.0f}%')
        self.draw()


    def draw(self):
        self.canvas.delete('all')
        vertices,edges,w,h=self.layout
        s=self.zoom
        for parent,child in edges:
            x1,y1,_,_=vertices[parent];x2,y2,_,_=vertices[child]
            ym=(y1+y2)/2
            self.canvas.create_line(x1*s,(y1+11)*s,x1*s,ym*s,x2*s,ym*s,x2*s,(y2-11)*s,
                fill=EDGE,width=max(1,1.5*s),smooth=True)
        for x,y,label,leaf in vertices:
            self.canvas.create_text(x*s,y*s,text=label,fill=LEAF if leaf else DARK,
                font=('Segoe UI',max(8,int(12*s)), 'normal' if leaf else 'bold'))
        self.canvas.configure(scrollregion=(0,0,w*s,h*s))

    def save_svg(self):
        filename=filedialog.asksaveasfilename(parent=self,title='Export Parse Tree',
            defaultextension='.svg',filetypes=[('SVG vector image','*.svg')],
            initialfile='jacaranda_parse_tree.svg')

        if filename:
            export_svg(filename,self.layout)

    def save_raster(self, fmt):
        extension = '.png' if fmt == 'PNG' else '.jpg'
        filename = filedialog.asksaveasfilename(
            parent=self, title=f'Export Parse Tree ({fmt})',
            defaultextension=extension,
            filetypes=[(f'{fmt} image', f'*{extension}')],
            initialfile=f'jacaranda_parse_tree{extension}')
        if filename:
            try:
                export_raster(filename, self.layout, fmt)
            except (OSError, ImportError, ValueError) as err:
                messagebox.showerror('Error exporting the tree', str(err), parent=self)
