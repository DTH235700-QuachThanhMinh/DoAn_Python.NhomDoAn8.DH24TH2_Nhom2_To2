import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from lienket import connect_db


class PhieuNhapFrame(tk.Frame):
    def __init__(self, parent, show_main_menu=None):
        super().__init__(parent, bg="white")
        self.show_main_menu = show_main_menu

        self.ncc_map = {}
        self.nv_map = {}

        self.load_maps()
        self.create_ui()
        self.load_phieunhap()

    # ============================================================
    # LOAD MAP NCC + NV
    # ============================================================
    def load_maps(self):
        self.ncc_map.clear()
        self.nv_map.clear()

        conn = connect_db()
        cur = conn.cursor()

        cur.execute("SELECT MaNCC, TenNCC FROM nhacungcap ORDER BY TenNCC")
        for ma, ten in cur.fetchall():
            self.ncc_map[ten] = ma

        cur.execute("SELECT MaNV, HoTenNV FROM nhanvien ORDER BY HoTenNV")
        for ma, ten in cur.fetchall():
            self.nv_map[ten] = ma

        conn.close()

    # ============================================================
    # UI
    # ============================================================
    def create_ui(self):
        tk.Label(self, text="QUẢN LÝ PHIẾU NHẬP",
                 font=("Arial", 18, "bold"), bg="white", fg="#003A75").pack(pady=10)

        frame = tk.Frame(self, bg="white")
        frame.pack(fill="x", padx=20)

        for i in range(4):
            frame.columnconfigure(i, weight=1)

        # Mã PN
        tk.Label(frame, text="Mã phiếu nhập:", bg="white").grid(row=0, column=0, sticky="w")
        self.entry_mapn = tk.Entry(frame)
        self.entry_mapn.grid(row=0, column=1, padx=5, pady=5, sticky="we")

        # Ngày nhập
        tk.Label(frame, text="Ngày nhập:", bg="white").grid(row=0, column=2, sticky="w")
        self.entry_ngay = tk.Entry(frame)
        self.entry_ngay.insert(0, date.today().isoformat())
        self.entry_ngay.grid(row=0, column=3, padx=5, pady=5, sticky="we")

        # Nhà cung cấp (COMBOBOX)
        tk.Label(frame, text="Nhà cung cấp:", bg="white").grid(row=1, column=0, sticky="w")
        self.cbb_ncc = ttk.Combobox(frame, state="readonly",
                                    values=list(self.ncc_map.keys()))
        self.cbb_ncc.grid(row=1, column=1, padx=5, pady=5, sticky="we")

        # Nhân viên (COMBOBOX)
        tk.Label(frame, text="Nhân viên:", bg="white").grid(row=1, column=2, sticky="w")
        self.cbb_nv = ttk.Combobox(frame, state="readonly",
                                   values=list(self.nv_map.keys()))
        self.cbb_nv.grid(row=1, column=3, padx=5, pady=5, sticky="we")

        # Ghi chú
        tk.Label(frame, text="Ghi chú:", bg="white").grid(row=2, column=0, sticky="w")
        self.entry_ghichu = tk.Entry(frame)
        self.entry_ghichu.grid(row=2, column=1, padx=5, pady=5, sticky="we")

        # Tổng tiền
        tk.Label(frame, text="Tổng tiền:", bg="white").grid(row=2, column=2, sticky="w")
        self.entry_tongtien = tk.Entry(frame, state="readonly")
        self.entry_tongtien.grid(row=2, column=3, padx=5, pady=5, sticky="we")
        self.entry_tongtien.insert(0, "0")

        # ============================================================
        # SEARCH
        # ============================================================
        search_frame = tk.Frame(self, bg="white")
        search_frame.pack(fill="x", padx=20, pady=10)

        search_frame.columnconfigure(0, weight=3)

        tk.Label(search_frame, text="Tìm kiếm:", bg="white").grid(row=0, column=0, sticky="w")
        self.entry_search = tk.Entry(search_frame)
        self.entry_search.grid(row=1, column=0, sticky="we", padx=10)

        self.cbb_search_type = ttk.Combobox(
            search_frame,
            values=[" ", "MaPN", "TenNCC", "TenNV"],
            state="readonly"
        )
        self.cbb_search_type.set(" ")
        self.cbb_search_type.grid(row=1, column=1, padx=5)

        tk.Button(search_frame, text="Tìm", bg="#003A75", fg="white",
                  command=self.search_phieunhap).grid(row=1, column=2, padx=5)

        # ============================================================
        # TABLE
        # ============================================================
        cols = ("MaPN", "NgayNhap", "TenNCC", "TenNV", "TongTien", "GhiChu")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)

        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=160)

        self.tree.pack(fill="both", padx=20, pady=10)

        # ============================================================
        # BUTTONS
        # ============================================================
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=10)

        btn = dict(width=15, fg="white", font=("Arial", 11, "bold"))

        tk.Button(btn_frame, text="Thêm", bg="#3498DB",
                  command=self.add_phieunhap, **btn).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Sửa", bg="#E67E22",
                  command=self.load_selected_to_edit, **btn).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Lưu", bg="#27AE60",
                  command=self.save_edit, **btn).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Xóa", bg="#C0392B",
                  command=self.delete_phieunhap, **btn).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Hủy", bg="#7D3C98",
                  command=self.clear_input, **btn).grid(row=0, column=4, padx=5)

    # ============================================================
    # FETCH
    # ============================================================
    def fetch_all_phieunhap(self):
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                p.MaPN,
                p.NgayNhap,
                ncc.TenNCC,
                nv.HoTenNV,
                p.TongTien,
                p.GhiChu
            FROM phieunhap p
            JOIN nhacungcap ncc ON p.MaNCC = ncc.MaNCC
            JOIN nhanvien nv ON p.MaNV = nv.MaNV
            ORDER BY p.MaPN
        """)

        rows = cur.fetchall()
        conn.close()
        return rows

    # ============================================================
    # LOAD TABLE
    # ============================================================
    def load_phieunhap(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.fetch_all_phieunhap():
            self.tree.insert("", "end", values=row)

    # ============================================================
    # ADD
    # ============================================================
    def add_phieunhap(self):
        mapn = self.entry_mapn.get().strip()
        ngay = self.entry_ngay.get().strip()
        tenncc = self.cbb_ncc.get().strip()
        tennv = self.cbb_nv.get().strip()
        ghichu = self.entry_ghichu.get().strip()

        if not all([mapn, ngay, tenncc, tennv]):
            return messagebox.showwarning("Thiếu dữ liệu", "Hãy nhập đủ thông tin!")

        if tenncc not in self.ncc_map:
            return messagebox.showerror("Lỗi", "Tên nhà cung cấp không tồn tại!")

        if tennv not in self.nv_map:
            return messagebox.showerror("Lỗi", "Tên nhân viên không tồn tại!")

        mancc = self.ncc_map[tenncc]
        manv = self.nv_map[tennv]

        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO phieunhap (MaPN, NgayNhap, MaNCC, MaNV, TongTien, GhiChu)
            VALUES (%s, %s, %s, %s, 0, %s)
        """, (mapn, ngay, mancc, manv, ghichu))

        conn.commit()
        conn.close()

        self.load_phieunhap()
        self.clear_input()

    # ============================================================
    # DELETE
    # ============================================================
    def delete_phieunhap(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chưa chọn", "Hãy chọn phiếu nhập để xóa")

        item = sel[0]
        mapn = self.tree.item(item)["values"][0]

        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa phiếu nhập {mapn}?"):
            return

        try:
            conn = connect_db()
            cur = conn.cursor()

            cur.execute("DELETE FROM ct_phieunhap WHERE MaPN=%s", (mapn,))
            cur.execute("DELETE FROM phieunhap WHERE MaPN=%s", (mapn,))

            conn.commit()
            conn.close()

            self.load_phieunhap()
            messagebox.showinfo("OK", f"Đã xóa phiếu nhập {mapn}")

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # ============================================================
    # LOAD SELECTED
    # ============================================================
    def load_selected_to_edit(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chưa chọn", "Hãy chọn dòng để sửa")

        data = self.tree.item(sel)["values"]

        self.entry_mapn.delete(0, tk.END)
        self.entry_mapn.insert(0, data[0])

        self.entry_ngay.delete(0, tk.END)
        self.entry_ngay.insert(0, data[1])

        self.cbb_ncc.set(data[2])
        self.cbb_nv.set(data[3])

        self.entry_tongtien.config(state="normal")
        self.entry_tongtien.delete(0, tk.END)
        self.entry_tongtien.insert(0, data[4])
        self.entry_tongtien.config(state="readonly")

        self.entry_ghichu.delete(0, tk.END)
        self.entry_ghichu.insert(0, data[5])

    # ============================================================
    # SAVE EDIT
    # ============================================================
    def save_edit(self):
        mapn = self.entry_mapn.get().strip()
        ngay = self.entry_ngay.get().strip()
        tenncc = self.cbb_ncc.get().strip()
        tennv = self.cbb_nv.get().strip()
        ghichu = self.entry_ghichu.get().strip()

        if tenncc not in self.ncc_map:
            return messagebox.showerror("Lỗi", "Tên nhà cung cấp không tồn tại!")

        if tennv not in self.nv_map:
            return messagebox.showerror("Lỗi", "Tên nhân viên không tồn tại!")

        mancc = self.ncc_map[tenncc]
        manv = self.nv_map[tennv]

        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE phieunhap
            SET NgayNhap=%s, MaNCC=%s, MaNV=%s, GhiChu=%s
            WHERE MaPN=%s
        """, (ngay, mancc, manv, ghichu, mapn))

        conn.commit()
        conn.close()

        self.load_phieunhap()
        self.clear_input()

    # ============================================================
    # SEARCH
    # ============================================================
    def search_phieunhap(self):
        kw = self.entry_search.get().strip()
        field = self.cbb_search_type.get()

        if kw == "":
            return self.load_phieunhap()

        conn = connect_db()
        cur = conn.cursor()

        if field == "TenNCC":
            sql = """
                SELECT p.MaPN, p.NgayNhap, n.TenNCC, nv.HoTenNV, p.TongTien, p.GhiChu
                FROM phieunhap p
                JOIN nhacungcap n ON p.MaNCC = n.MaNCC
                JOIN nhanvien nv ON p.MaNV = nv.MaNV
                WHERE n.TenNCC LIKE %s
            """
        elif field == "TenNV":
            sql = """
                SELECT p.MaPN, p.NgayNhap, n.TenNCC, nv.HoTenNV, p.TongTien, p.GhiChu
                FROM phieunhap p
                JOIN nhacungcap n ON p.MaNCC = n.MaNCC
                JOIN nhanvien nv ON p.MaNV = nv.MaNV
                WHERE nv.HoTenNV LIKE %s
            """
        else:
            sql = """
                SELECT p.MaPN, p.NgayNhap, n.TenNCC, nv.HoTenNV, p.TongTien, p.GhiChu
                FROM phieunhap p
                JOIN nhacungcap n ON p.MaNCC = n.MaNCC
                JOIN nhanvien nv ON p.MaNV = nv.MaNV
                WHERE p.MaPN LIKE %s
            """

        cur.execute(sql, ('%' + kw + '%',))
        rows = cur.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", values=r)

    # ============================================================
    # CLEAR INPUT
    # ============================================================
    def clear_input(self):
        self.entry_mapn.delete(0, tk.END)
        self.entry_ngay.delete(0, tk.END)
        self.entry_ngay.insert(0, date.today().isoformat())
        self.cbb_ncc.set("")
        self.cbb_nv.set("")
        self.entry_ghichu.delete(0, tk.END)
        self.entry_tongtien.config(state="normal")
        self.entry_tongtien.delete(0, tk.END)
        self.entry_tongtien.insert(0, "0")
        self.entry_tongtien.config(state="readonly")
