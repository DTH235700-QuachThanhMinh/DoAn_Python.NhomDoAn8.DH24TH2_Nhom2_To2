import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import tkinter as tk
from tkinter import ttk, messagebox

from db_functions import (
    load_table, add_record, delete_record,
    update_record, search_record
)


class KhachHangFrame(tk.Frame):
    def __init__(self, parent, show_main_menu=None):
        super().__init__(parent, bg="white")
        self.show_main_menu = show_main_menu
        self.create_ui()
        self.load_kh()

    # ======================================================
    #                VALIDATION & FORMAT
    # ======================================================
    def valid_phone(self, phone):
        return phone.isdigit() and len(phone) == 10

    def valid_cccd(self, cccd):
        return cccd.isdigit() and len(cccd) == 12

    def format_name(self, text):
        return " ".join(word.capitalize() for word in text.split())

    # ======================================================
    #                     UI
    # ======================================================
    def create_ui(self):

        tk.Label(
            self, text="QUẢN LÝ KHÁCH HÀNG",
            font=("Arial", 18, "bold"),
            bg="white", fg="#003A75"
        ).pack(pady=10)

        frame_info = tk.Frame(self, bg="white")
        frame_info.pack(padx=20, pady=10, fill="x")

        for i in range(4):
            frame_info.columnconfigure(i, weight=1, uniform="col")

        # Hàng 1
        self.entry_makh = self._make_entry(frame_info, "Mã KH:", 0, 0)
        self.entry_tenkh = self._make_entry(frame_info, "Họ tên KH:", 0, 2)

        # Hàng 2
        self.entry_sdt = self._make_entry(frame_info, "Số điện thoại:", 1, 0)
        self.entry_cccd = self._make_entry(frame_info, "CCCD:", 1, 2)

        # Hàng 3
        self.entry_diachi = self._make_entry(frame_info, "Địa chỉ:", 2, 0)

        # ================== SEARCH ==================
        frame_search = tk.Frame(self, bg="white")
        frame_search.pack(padx=20, pady=10, fill="x")
        frame_search.columnconfigure(0, weight=3)

        tk.Label(frame_search, text="Tìm kiếm:", bg="white").grid(row=0, column=0, sticky="w")

        self.entry_search = tk.Entry(frame_search)
        self.entry_search.grid(row=1, column=0, sticky="we", padx=10)

        self.cbb_search_type = ttk.Combobox(
            frame_search,
            values=[" ", "MaKH", "HoTen", "SDT", "CCCD", "DiaChi"],
            state="readonly"
        )
        self.cbb_search_type.grid(row=1, column=1, padx=5)
        self.cbb_search_type.set(" ")

        tk.Button(
            frame_search, text="Tìm", width=12,
            bg="#003A75", fg="white", command=self.search_kh
        ).grid(row=1, column=2, padx=5)

        # ================== TABLE ==================
        tk.Label(self, text="Danh sách khách hàng", bg="white",
                 font=("Arial", 11, "bold")).pack(anchor="w", padx=20)

        self.columns = ("MaKH", "HoTen", "SDT", "DiaChi", "CCCD")

        self.tree = ttk.Treeview(self, columns=self.columns, show="headings", height=11)
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(padx=10, pady=5, fill="both")

        # ================== BUTTONS ==================
        frame_btn = tk.Frame(self, bg="white")
        frame_btn.pack(pady=10)

        btn = dict(width=15, fg="white", font=("Arial", 11, "bold"))

        tk.Button(frame_btn, text="Thêm", bg="#3498DB",
                  command=self.add_kh, **btn).grid(row=0, column=0, padx=5)

        tk.Button(frame_btn, text="Lưu", bg="#27AE60",
                  command=self.save_edit, **btn).grid(row=0, column=1, padx=5)

        tk.Button(frame_btn, text="Sửa", bg="#E74C3C",
                  command=self.load_selected_to_edit, **btn).grid(row=0, column=2, padx=5)

        tk.Button(frame_btn, text="Hủy", bg="#E67E22",
                  command=self.clear_input, **btn).grid(row=0, column=3, padx=5)

        tk.Button(frame_btn, text="Xóa", bg="#800080",
                  command=self.delete_kh, **btn).grid(row=0, column=4, padx=5)

    # ======================================================
    #             ENTRY HELPER
    # ======================================================
    def _make_entry(self, parent, text, row, col):
        tk.Label(parent, text=text, bg="white").grid(row=row, column=col, sticky="w", pady=5)
        e = tk.Entry(parent)
        e.grid(row=row, column=col+1, sticky="we", padx=5)
        return e

    # ======================================================
    #                GET VALUES
    # ======================================================
    def get_values(self):
        return [
            self.entry_makh.get().strip(),
            self.format_name(self.entry_tenkh.get()),
            self.entry_sdt.get().strip(),
            self.format_name(self.entry_diachi.get()),
            self.entry_cccd.get().strip()
        ]

    # ======================================================
    #                LOAD TABLE
    # ======================================================
    def load_kh(self):
        self.tree.delete(*self.tree.get_children())
        for r in load_table("khachhang"):
            self.tree.insert("", "end", values=r)

    # ======================================================
    #                      ADD
    # ======================================================
    def add_kh(self):
        makh, hoten, sdt, diachi, cccd = self.get_values()

        if "" in [makh, hoten, sdt, diachi, cccd]:
            return messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ thông tin!")

        if not self.valid_phone(sdt):
            return messagebox.showerror("Lỗi", "Số điện thoại phải đúng 10 số!")

        if not self.valid_cccd(cccd):
            return messagebox.showerror("Lỗi", "CCCD phải đúng 12 số!")

        fields = ["MaKH", "HoTen", "SDT", "DiaChi", "CCCD"]
        add_record("khachhang", fields, [makh, hoten, sdt, diachi, cccd])

        messagebox.showinfo("OK", "Thêm khách hàng thành công!")
        self.load_kh()
        self.clear_input()

    # ======================================================
    #                      DELETE
    # ======================================================
    def delete_kh(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Thông báo", "Chọn khách hàng để xóa!")

        makh = self.tree.item(sel)["values"][0]

        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa khách hàng {makh}?"):
            return

        delete_record("khachhang", "MaKH", makh)

        messagebox.showinfo("OK", "Đã xóa!")
        self.load_kh()
        self.clear_input()

    # ======================================================
    #                LOAD TO EDIT FORM
    # ======================================================
    def load_selected_to_edit(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Thông báo", "Chọn khách hàng để sửa!")

        data = self.tree.item(sel)["values"]

        self.entry_makh.delete(0, tk.END)
        self.entry_makh.insert(0, data[0])

        self.entry_tenkh.delete(0, tk.END)
        self.entry_tenkh.insert(0, data[1])

        self.entry_sdt.delete(0, tk.END)
        self.entry_sdt.insert(0, data[2])

        self.entry_diachi.delete(0, tk.END)
        self.entry_diachi.insert(0, data[3])

        self.entry_cccd.delete(0, tk.END)
        self.entry_cccd.insert(0, data[4])

    # ======================================================
    #                     SAVE EDIT
    # ======================================================
    def save_edit(self):
        makh = self.entry_makh.get().strip()
        _, hoten, sdt, diachi, cccd = self.get_values()

        if "" in [makh, hoten, sdt, diachi, cccd]:
            return messagebox.showwarning("Lỗi", "Không được để trống!")

        if not self.valid_phone(sdt):
            return messagebox.showerror("Lỗi", "SĐT phải đúng 10 số!")

        if not self.valid_cccd(cccd):
            return messagebox.showerror("Lỗi", "CCCD phải đúng 12 số!")

        fields = ["HoTen", "SDT", "DiaChi", "CCCD"]
        new_data = [hoten, sdt, diachi, cccd]

        update_record("khachhang", "MaKH", makh, fields, new_data)

        messagebox.showinfo("OK", "Cập nhật thành công!")
        self.load_kh()
        self.clear_input()

    # ======================================================
    #                      SEARCH
    # ======================================================
    def search_kh(self):
        keyword = self.entry_search.get().strip()
        field = self.cbb_search_type.get()

        if field == " ":
            return self.load_kh()

        rows = search_record("khachhang", field, keyword)

        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", values=r)

    # ======================================================
    #                     CLEAR INPUT
    # ======================================================
    def clear_input(self):
        self.entry_makh.delete(0, tk.END)
        self.entry_tenkh.delete(0, tk.END)
        self.entry_sdt.delete(0, tk.END)
        self.entry_diachi.delete(0, tk.END)
        self.entry_cccd.delete(0, tk.END)
