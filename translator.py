import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import time
from googletrans import Translator
from tqdm import tqdm

class RobustTranslator(Translator):
    def translate(self, text, dest='bn', src='en'):
        if not text or pd.isna(text) or str(text).strip() == "":
            return text
        for _ in range(3):
            try:
                return super().translate(text, dest=dest, src=src).text
            except:
                time.sleep(1)
        return str(text)  
    
def translate_csv():
    input_path = entry_path.get()
    column = entry_column.get().strip()
    range_input = entry_range.get().strip()
    output_dir = entry_output.get()

    if not input_path or not os.path.exists(input_path):
        messagebox.showerror("Error", "Please select a valid CSV file!")
        return
    if not column:
        messagebox.showerror("Error", "Please enter column name!")
        return
    if not range_input:
        messagebox.showerror("Error", "Please enter row range (e.g. 1:100)!")
        return
    if not output_dir:
        messagebox.showerror("Error", "Please choose output folder!")
        return

    try:
        start, end = map(int, range_input.split(":"))
        if start < 0 or start >= end:
            raise ValueError
    except:
        messagebox.showerror("Error", "Invalid range! Use format like 1:100 or 500:600")
        return

    btn_start.config(state='disabled')
    progress['value'] = 0
    root.update()

    try:
        df = pd.read_csv(input_path)

        if column not in df.columns:
            messagebox.showerror("Error", f"Column '{column}' not found!\nAvailable: {list(df.columns)}")
            return

        if end > len(df):
            end = len(df)

        translator = RobustTranslator()

        for i in tqdm(range(start, end), desc="Translating", leave=False):
            english = df.at[i, column]
            bangla = translator.translate(str(english))
            df.at[i, column] = bangla
            time.sleep(0.6)  
            progress['value'] = (i - start + 1) / (end - start) * 100
            root.update()

        output_df = df.iloc[:end].copy()
        output_file = os.path.join(output_dir, f"BANGLA_{os.path.basename(input_path)}_rows_{start}-{end-1}.csv")
        output_df.to_csv(output_file, index=False, encoding='utf-8-sig')

        messagebox.showinfo("Success!", f"Translation Complete!\nSaved to:\n{output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{str(e)}")
    finally:
        btn_start.config(state='normal')
        progress['value'] = 100

root = tk.Tk()
root.title("English to Bangla CSV Translator")
root.geometry("650x400")
root.resizable(False, False)
root.configure(padx=20, pady=20)

tk.Label(root, text="English to Bangla CSV Translator", font=("Arial", 16, "bold")).pack(pady=10)

tk.Label(root, text="1. Select CSV File:").pack(anchor='w', pady=(10,0))
frame1 = tk.Frame(root)
frame1.pack(fill='x')
entry_path = tk.Entry(frame1, width=60)
entry_path.pack(side='left', expand=True, fill='x')
tk.Button(frame1, text="Browse", command=lambda: entry_path.insert(0, filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")]))).pack(side='right')

tk.Label(root, text="2. Column with English text:").pack(anchor='w', pady=(10,0))
entry_column = tk.Entry(root, width=40)
entry_column.pack()

tk.Label(root, text="3. Row range to translate (e.g. 1:100 or 1000:1100):").pack(anchor='w', pady=(10,0))
entry_range = tk.Entry(root, width=40)
entry_range.pack()

tk.Label(root, text="4. Choose Output Folder:").pack(anchor='w', pady=(10,0))
frame2 = tk.Frame(root)
frame2.pack(fill='x')
entry_output = tk.Entry(frame2, width=60)
entry_output.pack(side='left', expand=True, fill='x')
tk.Button(frame2, text="Browse", command=lambda: entry_output.insert(0, filedialog.askdirectory())).pack(side='right')

progress = ttk.Progressbar(root, length=500, mode='determinate')
progress.pack(pady=20)

btn_start = tk.Button(root, text="START TRANSLATION", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", height=2, command=translate_csv)
btn_start.pack(pady=10)

tk.Label(root, text="Tip: Translate 100 rows at a time to avoid Google blocking", fg="gray").pack(pady=10)

root.mainloop()