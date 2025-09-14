#!/usr/bin/env python3
"""crispresso_abe_gui_clean.py
Simple Tkinter GUI for ABE efficiency calculation from CRISPResso-style files.
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd, os
def calculate_efficiency(file_path, protospacer, selected_position):
    df = pd.read_csv(file_path, sep=None, engine='python')
    df.columns = [c.strip() for c in df.columns]
    if 'Reference_Sequence' not in df.columns or 'Aligned_Sequence' not in df.columns:
        raise ValueError('Expected columns "Reference_Sequence" and "Aligned_Sequence".')
    ref_seq = str(df['Reference_Sequence'].iloc[0]).upper()
    protospacer = protospacer.upper()
    start = ref_seq.find(protospacer)
    if start == -1:
        raise ValueError('Protospacer not found in Reference_Sequence.')
    total_reads = df.get('#Reads', df.get('Reads', df.get('Count', 1))).sum()
    edited_total = edited_window = edited_selected = 0
    sel_base = protospacer[selected_position-1]
    for _, row in df.iterrows():
        aln = str(row['Aligned_Sequence']).upper()
        reads = row.get('#Reads', row.get('Reads', row.get('Count', 1)))
        any_edit = window_edit = sel_edit = False
        for i in range(len(protospacer)):
            ref = protospacer[i]
            aln_base = aln[start + i]
            if ref == 'A' and aln_base == 'G':
                any_edit = True
                if 3 <= i <= 7:
                    window_edit = True
                if i == (selected_position-1):
                    sel_edit = True
        if any_edit:
            edited_total += reads
        if window_edit:
            edited_window += reads
        if sel_edit:
            edited_selected += reads
    eff_total = (edited_total/total_reads)*100 if total_reads>0 else 0.0
    eff_window = (edited_window/total_reads)*100 if total_reads>0 else 0.0
    eff_selected = (edited_selected/total_reads)*100 if total_reads>0 and sel_base=='A' else None
    return {'protospacer':protospacer,'total_reads':int(total_reads),'edited_total':int(edited_total),'eff_total':eff_total,'eff_window':eff_window,'eff_selected':eff_selected,'selected_base':sel_base}
def browse_file(entry):
    file_path = filedialog.askopenfilename(filetypes=[("Text files","*.txt;*.tsv;*.csv"),("All files","*.*")])
    if file_path:
        entry.delete(0, tk.END); entry.insert(0, file_path)
def on_calculate(entry_file, entry_protospacer, position_var, output_text):
    file_path = entry_file.get()
    protospacer = entry_protospacer.get().strip()
    try:
        pos = int(position_var.get())
    except:
        messagebox.showwarning("Input Error", "Select a valid position (1-20)."); return
    if not file_path or not protospacer:
        messagebox.showwarning("Input Error", "Please provide both file and protospacer."); return
    try:
        res = calculate_efficiency(file_path, protospacer, pos)
    except Exception as e:
        messagebox.showerror("Error", str(e)); return
    output_text.delete(1.0, tk.END)
    lines = [
        f"Protospacer: {res['protospacer']}",
        f"Total reads: {res['total_reads']}",
        f"Reads with any A->G in protospacer: {res['edited_total']} ({res['eff_total']:.2f}%)",
        f"A->G within window (pos4-8): {res['eff_window']:.2f}%"
    ]
    if res['eff_selected'] is not None:
        lines.append(f"A->G at selected position: {res['eff_selected']:.2f}% (Ref: {res['selected_base']})")
    else:
        lines.append(f"Selected position not editable (Ref: {res['selected_base']})")
    output_text.insert(tk.END, "\n".join(lines))
# GUI
root = tk.Tk(); root.title("ABE Efficiency Calculator (clean)")
tk.Label(root, text="CRISPResso2 file:").grid(row=0,column=0,sticky="e")
entry_file = tk.Entry(root, width=50); entry_file.grid(row=0,column=1,padx=5,pady=5)
tk.Button(root, text="Browse", command=lambda: browse_file(entry_file)).grid(row=0,column=2)
tk.Label(root, text="20-nt protospacer:").grid(row=1,column=0,sticky="e")
entry_protospacer = tk.Entry(root, width=30); entry_protospacer.grid(row=1,column=1,padx=5,pady=5,sticky="w")
tk.Label(root, text="Position (1-20):").grid(row=2,column=0,sticky="e")
position_var = tk.StringVar(root); position_var.set("6")
position_menu = tk.OptionMenu(root, position_var, *[str(i) for i in range(1,21)]); position_menu.grid(row=2,column=1,sticky="w",pady=5)
tk.Button(root, text="Calculate", command=lambda: on_calculate(entry_file, entry_protospacer, position_var, output_text)).grid(row=3,column=1,pady=8)
output_text = tk.Text(root, width=70, height=10); output_text.grid(row=4,column=0,columnspan=3,padx=10,pady=5)
root.mainloop()
