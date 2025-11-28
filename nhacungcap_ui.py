import tkinter as tk
from tkinter import ttk, messagebox

from db_functions import (
    load_table, add_record, delete_record,
    update_record, search_record
)

class NhaCungCapFrame(tk.Frame):
    def __init__(self, parent, show_main_menu=None):
        super().__init__(parent, bg="white")
        self.show_main_menu = show_main_menu
        self.create_ui()
        self.load_ncc()

    # ============================================================
    #               VALIDATION & FORMAT
    # ============================================================
    def valid_phone(self, phone: str):
        return phone.isdigit() and len(phone) == 10

    def format_name(self, text):
        """Viết hoa mỗi chữ cái đầu và loại bỏ khoảng trắng thừa"""
        return " ".join(word.capitalize() for word in text.split())

    # ============================================================
    #                   TẠO GIAO DIỆN
    # ============================================================
    def create_ui(self):

        tk.Label(
            self, text="QUẢN LÝ NHÀ CUNG CẤP",
            font=("Arial", 18, "bold"),
            bg="white", fg="#003A75"
        ).pack(pady=10)

        frame_info = tk.Frame(self, bg="white")
        frame_info.pack(padx=20, pady=10, fill="x")

        for i in range(4):
            frame_info.columnconfigure(i, weight=1, uniform="col")

        # Hàng 1
        self.entry_mancc = self._make_entry(frame_info, "Mã NCC:", 0, 0)
        self.entry_tenncc = self._make_entry(frame_info, "Tên NCC:", 0, 2)

        # Hàng 2
        self.entry_sdt = self._make_entry(frame_info, "Số điện thoại:", 1, 0)
        self.entry_diachi = self._make_entry(frame_info, "Địa chỉ:", 1, 2)

        # Hàng 3
        self.entry_ghichu = self._make_entry(frame_info, "Ghi chú:", 2, 0)

        # ================== SEARCH ==================
        frame_search = tk.Frame(self, bg="white")
        frame_search.pack(padx=20, pady=10, fill="x")

        frame_search.columnconfigure(0, weight=3)

        tk.Label(frame_search, text="Tìm kiếm:", bg="white").grid(row=0, column=0, sticky="w")
        self.entry_search = tk.Entry(frame_search)
        self.entry_search.grid(row=1, column=0, sticky="we", padx=10)

        self.cbb_search_type = ttk.Combobox(
            frame_search,
            values=[" ", "MaNCC", "TenNCC", "SDT"],
            state="readonly"
        )
        self.cbb_search_type.grid(row=1, column=1, padx=5)
        self.cbb_search_type.set(" ")

        tk.Button(
            frame_search, text="Tìm kiếm", bg="#003A75", fg="white",
            width=12, command=self.search_ncc
        ).grid(row=1, column=2, padx=5)

        # ================= TABLE ====================
        tk.Label(self, text="Danh sách nhà cung cấp",
                 bg="white",
                 font=("Arial", 11, "bold")
                 ).pack(anchor="w", padx=20)

        columns = ("MaNCC", "TenNCC", "SDT", "DiaChi", "GhiChu")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(padx=10, pady=5, fill="both")

        # ================= BUTTONS ==================
        frame_btn = tk.Frame(self, bg="white")
        frame_btn.pack(pady=10)

        btn = dict(width=15, fg="white", font=("Arial", 11, "bold"))

        tk.Button(frame_btn, text="Thêm", bg="#3498DB",
                  command=self.add_ncc, **btn).grid(row=0, column=0, padx=5)

        tk.Button(frame_btn, text="Lưu", bg="#27AE60",
                  command=self.save_edit, **btn).grid(row=0, column=1, padx=5)

        tk.Button(frame_btn, text="Sửa", bg="#E74C3C",
                  command=self.load_selected_to_edit, **btn).grid(row=0, column=2, padx=5)

        tk.Button(frame_btn, text="Hủy", bg="#E67E22",
                  command=self.clear_input, **btn).grid(row=0, column=3, padx=5)

        tk.Button(frame_btn, text="Xóa", bg="#800080",
                  command=self.delete_ncc, **btn).grid(row=0, column=4, padx=5)

    # ============================================================
    #             HÀM TẠO ENTRY CHUẨN
    # ============================================================
    def _make_entry(self, parent, text, row, col):
        tk.Label(parent, text=text, bg="white").grid(row=row, column=col, sticky="w", pady=5)
        e = tk.Entry(parent)
        e.grid(row=row, column=col + 1, sticky="we", padx=5)
        return e

    # ============================================================
    #                      CRUD
    # ============================================================
    def get_values(self):
        return [
            self.entry_mancc.get().strip(),
            self.format_name(self.entry_tenncc.get()),
            self.entry_sdt.get().strip(),
            self.format_name(self.entry_diachi.get()),
            self.entry_ghichu.get().strip()
        ]

    # ---------------- LOAD ----------------
    def load_ncc(self):
        self.tree.delete(*self.tree.get_children())
        for r in load_table("nhacungcap"):
            self.tree.insert("", "end", values=r)

    # ---------------- ADD -----------------
    def add_ncc(self):
        values = self.get_values()

        mancc, tenncc, sdt, diachi, ghichu = values

        if "" in [mancc, tenncc, sdt, diachi]:
            return messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ thông tin!")

        if not self.valid_phone(sdt):
            return messagebox.showerror("Lỗi", "SĐT phải đúng 10 số!")

        fields = ["MaNCC", "TenNCC", "SDT", "DiaChi", "GhiChu"]

        add_record("nhacungcap", fields, values)
        messagebox.showinfo("OK", "Thêm nhà cung cấp thành công!")
        self.load_ncc()
        self.clear_input()

    # ---------------- DELETE -----------------
    def delete_ncc(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Thông báo", "Chọn NCC để xóa!")

        mancc = self.tree.item(sel)["values"][0]

        if not messagebox.askyesno("Xác nhận", f"Xóa nhà cung cấp {mancc}?"):
            return

        delete_record("nhacungcap", "MaNCC", mancc)
        messagebox.showinfo("OK", "Đã xóa!")
        self.load_ncc()
        self.clear_input()

    # ---------------- LOAD EDIT -----------------
    def load_selected_to_edit(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Thông báo", "Chọn NCC để sửa!")

        data = self.tree.item(sel)["values"]

        self.entry_mancc.delete(0, tk.END)
        self.entry_mancc.insert(0, data[0])

        self.entry_tenncc.delete(0, tk.END)
        self.entry_tenncc.insert(0, data[1])

        self.entry_sdt.delete(0, tk.END)
        self.entry_sdt.insert(0, data[2])

        self.entry_diachi.delete(0, tk.END)
        self.entry_diachi.insert(0, data[3])

        self.entry_ghichu.delete(0, tk.END)
        self.entry_ghichu.insert(0, data[4])

    # ---------------- SAVE EDIT -----------------
    def save_edit(self):
        mancc = self.entry_mancc.get().strip()
        _, tenncc, sdt, diachi, ghichu = self.get_values()

        if "" in [mancc, tenncc, sdt, diachi]:
            return messagebox.showwarning("Lỗi", "Không được để trống!")

        if not self.valid_phone(sdt):
            return messagebox.showerror("Lỗi", "SĐT phải đúng 10 số!")

        fields = ["TenNCC", "SDT", "DiaChi", "GhiChu"]
        new_values = [tenncc, sdt, diachi, ghichu]

        update_record("nhacungcap", "MaNCC", mancc, fields, new_values)

        messagebox.showinfo("OK", "Cập nhật thành công!")
        self.load_ncc()
        self.clear_input()

    # ---------------- SEARCH -----------------
    def search_ncc(self):
        keyword = self.entry_search.get().strip()
        field = self.cbb_search_type.get()

        if field == " ":
            return self.load_ncc()

        rows = search_record("nhacungcap", field, keyword)

        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", values=r)

    # ---------------- CLEAR -----------------
    def clear_input(self):
        self.entry_mancc.delete(0, tk.END)
        self.entry_tenncc.delete(0, tk.END)
        self.entry_sdt.delete(0, tk.END)
        self.entry_diachi.delete(0, tk.END)
        self.entry_ghichu.delete(0, tk.END)
