"""Purple Jacaranda Tkinter desktop app. Lark grammar + Interpreter."""
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
from engine import run,parse,JacarandaError

SAMPLE='''int suma(int a, int b) {\n    return a + b;\n}\n\nint main() {\n    int total = suma(3, 4);\n    print(total);\n    return 0;\n}\n'''
class JacarandaGUI:
    def __init__(self,root):
        self.root=root;root.title('JACARANDA | Lexer · Parser · SDT · Interpreter');root.geometry('1140x720');root.minsize(850,550)
        root.configure(bg='#eee9f7')
        head=tk.Frame(root,bg='#53366f');head.pack(fill='x')
        tk.Label(head,text='JACARANDA',font=('Segoe UI',21,'bold'),bg='#53366f',fg='white').pack(anchor='w',padx=20,pady=(14,1))
        tk.Label(head,text='Educational C-like Interpreter  |  Lark LALR Parser + SDT + Execution',font=('Segoe UI',10),bg='#53366f',fg='#e8d9f4').pack(anchor='w',padx=20,pady=(0,14))
        bar=tk.Frame(root,bg='#eee9f7');bar.pack(fill='x',padx=14,pady=12)
        for text,action in [('Run Program',self.execute),('Check Parse',self.check),('View Parse Tree',self.tree),('Open File',self.open_file),('Save File',self.save_file),('Clear',self.clear)]:
            tk.Button(bar,text=text,command=action,bg='#725197',fg='white',activebackground='#926aba',relief='flat',padx=12,pady=7).pack(side='left',padx=3)
        panes=tk.PanedWindow(root,orient='horizontal',sashwidth=6,bg='#ddd3ed');panes.pack(fill='both',expand=True,padx=14,pady=(0,14))
        left=tk.Frame(panes,bg='#fff');right=tk.Frame(panes,bg='#fff');panes.add(left,minsize=200);panes.add(right,minsize=200)
        tk.Label(left,text='Source Code',bg='#fff',fg='#53366f',font=('Segoe UI',12,'bold')).pack(anchor='w',padx=12,pady=8)
        self.source=tk.Text(left,font=('Consolas',11),wrap='none',bg='#fff',fg='#23222d',undo=True,insertbackground='#53366f');self.source.pack(fill='both',expand=True,padx=8,pady=(0,8));self.source.insert('1.0',SAMPLE)
        tk.Label(right,text='Analysis & Execution Results',bg='#fff',fg='#53366f',font=('Segoe UI',12,'bold')).pack(anchor='w',padx=12,pady=8)
        self.output=tk.Text(right,font=('Consolas',10),wrap='word',bg='#faf7ff',fg='#2f2740',state='disabled');self.output.pack(fill='both',expand=True,padx=8,pady=(0,8))
        self.status=tk.Label(root,text='Ready',bg='#eee9f7',fg='#53366f',anchor='w');self.status.pack(fill='x',padx=18,pady=(0,8))
    def get_code(self):return self.source.get('1.0','end-1c')
    def put(self,value):
        self.output.config(state='normal');self.output.delete('1.0','end');self.output.insert('1.0',value);self.output.config(state='disabled')
    def execute(self):
        result=run(self.get_code());self.put(result.formatted());self.status.config(text='Execution succeeded' if result.ok else result.phase+' error')
    def check(self):
        try:node=parse(self.get_code());self.put('Parsing Success!\n\n'+node.pretty());self.status.config(text='Syntax valid')
        except JacarandaError as e:self.put(str(e));self.status.config(text='Syntax invalid')
    def tree(self):
        try:node=parse(self.get_code());text=node.pretty()
        except JacarandaError as e:self.put(str(e));return
        win=tk.Toplevel(self.root);win.title('Jacaranda · Parse Tree');win.geometry('740x680')
        pane=tk.Text(win,font=('Consolas',10),wrap='none');pane.pack(fill='both',expand=True);pane.insert('1.0',text);pane.config(state='disabled')
    def open_file(self):
        name=filedialog.askopenfilename(filetypes=[('Source files','*.c *.txt *.h'),('All files','*.*')]);
        if not name:return
        try:self.source.delete('1.0','end');self.source.insert('1.0',Path(name).read_text(encoding='utf-8'));self.status.config(text=f'Loaded {Path(name).name}')
        except (OSError,UnicodeError) as e:messagebox.showerror('File error',str(e))
    def save_file(self):
        name=filedialog.asksaveasfilename(defaultextension='.c',filetypes=[('C-like source','*.c'),('Text file','*.txt')]);
        if name:
            try:Path(name).write_text(self.get_code(),encoding='utf-8');self.status.config(text=f'Saved {Path(name).name}')
            except OSError as e:messagebox.showerror('Save error',str(e))
    def clear(self):self.source.delete('1.0','end');self.put('');self.status.config(text='Cleared')
if __name__=='__main__':
    root=tk.Tk();JacarandaGUI(root);root.mainloop()
