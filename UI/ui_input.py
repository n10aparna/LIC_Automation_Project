import tkinter as tk
from tkinter import filedialog, messagebox

def get_user_inputs():
    result = {}

    def browse_file():
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

    def submit():
        file_path = file_entry.get()
        retries = retry_entry.get()
        flag = flag_var.get()

        if not file_path:
            messagebox.showerror("Error", "Please select a file")
            return

        if not retries.isdigit() or int(retries) <= 0:
            messagebox.showerror("Error", "Retries must be greater than 0")
            return

        result["file_path"] = file_path
        result["retries"] = int(retries)
        result["flag"] = flag

        root.destroy()

    root = tk.Tk()
    root.title("Test Configuration")
    root.geometry("450x320")

    # ---------------- File ----------------
    tk.Label(root, text="Select File:").pack(pady=5)

    file_frame = tk.Frame(root)
    file_frame.pack()

    file_entry = tk.Entry(file_frame, width=30)
    file_entry.pack(side=tk.LEFT, padx=5)

    tk.Button(file_frame, text="Browse", command=browse_file).pack(side=tk.LEFT)

    # ---------------- Retries ----------------
    tk.Label(root, text="Number of Retries:").pack(pady=5)

    retry_entry = tk.Entry(root)
    retry_entry.pack()
    retry_entry.insert(0, "1")  # ✅ default 1

    # ---------------- Radio Buttons ----------------
    tk.Label(root, text="Select Processing Mode:").pack(pady=8)

    flag_var = tk.StringVar(value="A")  # ✅ Default = A

    radio_frame = tk.Frame(root)
    radio_frame.pack()

    tk.Radiobutton(radio_frame, text="A", variable=flag_var, value="A").pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(radio_frame, text="B", variable=flag_var, value="B").pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(radio_frame, text="C", variable=flag_var, value="C").pack(side=tk.LEFT, padx=10)

    # ---------------- Description ----------------
    description = (
        "A: Untried records (no remark or new)\n"
        "B: Only failed records (Remark = 'Unable to fetch')\n"
        "C: All records marked as False"
    )

    tk.Label(root, text=description, fg="gray", justify="left").pack(pady=10)

    # ---------------- Submit ----------------
    tk.Button(root, text="Start", command=submit, bg="green", fg="white").pack(pady=10)

    root.mainloop()

    return result