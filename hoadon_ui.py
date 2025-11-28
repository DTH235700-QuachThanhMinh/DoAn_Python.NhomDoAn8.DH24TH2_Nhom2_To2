import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import tkinter as tk
from tkinter import ttk, messagebox
from lienket import connect_db
import datetime


class HoaDonFrame(tk.Frame):
    def __init__(self, parent, show_main_menu=None):
        super().__init__(parent, bg="white")
        self.show_main_menu = show_main_menu

        self.kh_map = {}   # HoTen → MaKH
        self.nv_map = {}   # HoTenNV → MaNV

        self.load_map_kh_nv()
        self.create_ui()
        self.load_hd()

    # =====================================================
    # VALIDATION 
    # =====================================================
    def valid_date(self, date_text):
        try:
            datetime.datetime.strptime(date_text, "%Y-%m-%d")
            return True
        except:
            return False

    def format_name(self, text):
        return " ".join(word.capitalize() for word in text.split())

    # =====================================================
    # LOAD MAP KH & NV
    # =====================================================
    def load_map_kh_nv(self):
        try:
            conn = connect_db()
            cur = conn.cursor()

            cur.execute("SELECT MaKH, HoTen FROM khachhang ORDER BY HoTen")
            self.kh_map = {ten: ma for ma, ten in cur.fetchall()}

            cur.execute("SELECT MaNV, HoTenNV FROM nhanvien ORDER BY HoTenNV")
            self.nv_map = {ten: ma for ma, ten in cur.fetchall()}

            conn.close()

        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    # =====================================================
    # UI
    # =====================================================
    def create_ui(self):
        tk.Label(self, text="QUẢN LÝ HÓA ĐƠN",
                 font=("Arial", 18, "bold"), bg="white", fg="#003A75").pack(pady=10)

        frame_info = tk.Frame(self, bg="white")
        frame_info.pack(padx=20, pady=10, fill="x")

        for i in range(4):
            frame_info.columnconfigure(i, weight=1)

        # Mã hóa đơn
        self.entry_mahd = self._make_entry(frame_info, "Mã hóa đơn:", 0, 0)

        # KH Combobox
        tk.Label(frame_info, text="Khách hàng:", bg="white").grid(row=0, column=2, sticky="w")
        self.cbb_kh = ttk.Combobox(frame_info, state="readonly", values=list(self.kh_map.keys()))
        self.cbb_kh.grid(row=0, column=3, sticky="we", padx=5)

        # NV Combobox
        tk.Label(frame_info, text="Nhân viên lập:", bg="white").grid(row=1, column=0, sticky="w")
        self.cbb_nv = ttk.Combobox(frame_info, state="readonly", values=list(self.nv_map.keys()))
        self.cbb_nv.grid(row=1, column=1, sticky="we", padx=5)

        # Ngày bán
        self.entry_ngayban = self._make_entry(frame_info, "Ngày bán (yyyy-mm-dd):", 1, 2)

        # Hình thức thanh toán
        tk.Label(frame_info, text="Hình thức TT:", bg="white").grid(row=2, column=0, sticky="w")
        self.cbb_hinhthuc = ttk.Combobox(frame_info, state="readonly",
                                         values=["Tiền mặt", "Chuyển khoản", "Quẹt thẻ"])
        self.cbb_hinhthuc.grid(row=2, column=1, sticky="we", padx=5)

        # Ghi chú
        self.entry_ghichu = self._make_entry(frame_info, "Ghi chú:", 2, 2)

        # =====================================================
        # SEARCH
        # =====================================================
        frame_search = tk.Frame(self, bg="white")
        frame_search.pack(padx=20, pady=10, fill="x")

        frame_search.columnconfigure(0, weight=3)

        tk.Label(frame_search, text="Tìm kiếm:", bg="white").grid(row=0, column=0, sticky="w")
        self.entry_search = tk.Entry(frame_search)
        self.entry_search.grid(row=1, column=0, sticky="we", padx=10)

        self.cbb_search_type = ttk.Combobox(
            frame_search,
            values=[" ", "MaHD", "HoTen", "HoTenNV", "NgayBan", "HinhThucTT"],
            state="readonly"
        )
        self.cbb_search_type.set(" ")
        self.cbb_search_type.grid(row=1, column=1, padx=5)

        tk.Button(frame_search, text="Tìm kiếm", bg="#003A75", fg="white",
                  width=15, command=self.search_hd).grid(row=1, column=2, padx=5)

        # =====================================================
        # TABLE
        # =====================================================
        cols = ("MaHD", "HoTen", "HoTenNV", "NgayBan", "HinhThucTT", "GhiChu", "TongTien")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        tk.Label(self, text="Danh sách hóa đơn",
                 bg="white", font=("Arial", 11, "bold")).pack(anchor="w", padx=20)

        self.tree.pack(fill="both", padx=20, pady=10)

        # =====================================================
        # BUTTONS
        # =====================================================
        frame_btn = tk.Frame(self, bg="white")
        frame_btn.pack(pady=10)
        btn = dict(width=15, fg="white", font=("Arial", 11, "bold"))

        tk.Button(frame_btn, text="Thêm", bg="#3498DB",
                  command=self.add_hd, **btn).grid(row=0, column=0, padx=5)

        tk.Button(frame_btn, text="Lưu", bg="#27AE60",
                  command=self.save_edit, **btn).grid(row=0, column=1, padx=5)

        tk.Button(frame_btn, text="Sửa", bg="#E74C3C",
                  command=self.load_selected_to_edit, **btn).grid(row=0, column=2, padx=5)

        tk.Button(frame_btn, text="Hủy", bg="#E67E22",
                  command=self.clear_input, **btn).grid(row=0, column=3, padx=5)

        tk.Button(frame_btn, text="Xóa", bg="#800080",
                  command=self.delete_hd, **btn).grid(row=0, column=4, padx=5)

    def _make_entry(self, parent, text, row, col):
        tk.Label(parent, text=text, bg="white").grid(row=row, column=col, sticky="w")
        e = tk.Entry(parent)
        e.grid(row=row, column=col+1, sticky="we", padx=5)
        return e

    # =====================================================
    # LOAD TABLE
    # =====================================================
    def load_hd(self):
        try:
            conn = connect_db()
            cur = conn.cursor()

            cur.execute("""
                SELECT h.MaHD, k.HoTen, n.HoTenNV, h.NgayBan,
                       h.HinhThucTT, h.GhiChu, h.TongTien
                FROM hoadon h
                LEFT JOIN khachhang k ON h.MaKH = k.MaKH
                LEFT JOIN nhanvien n ON h.MaNV = n.MaNV
            """)

            rows = cur.fetchall()
            conn.close()

            self.tree.delete(*self.tree.get_children())

            for r in rows:
                # Format tổng tiền
                tong = "{:,}".format(int(r[6])).replace(",", ".")
                new_r = list(r)
                new_r[6] = tong
                self.tree.insert("", "end", values=new_r)

        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    # =====================================================
    # ADD
    # =====================================================
    def add_hd(self):
        mahd = self.entry_mahd.get().strip()
        tenkh = self.cbb_kh.get()
        tennv = self.cbb_nv.get()
        ngayban = self.entry_ngayban.get().strip()
        hinhthuc = self.cbb_hinhthuc.get()

        if not mahd or not tenkh or not tennv:
            return messagebox.showwarning("Thiếu", "Vui lòng nhập đầy đủ thông tin!")

        if tenkh not in self.kh_map:
            return messagebox.showerror("Lỗi", "Khách hàng không tồn tại!")

        if tennv not in self.nv_map:
            return messagebox.showerror("Lỗi", "Nhân viên không tồn tại!")

        if not self.valid_date(ngayban):
            return messagebox.showerror("Lỗi ngày", "Ngày bán phải dạng yyyy-mm-dd!")

        try:
            conn = connect_db()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO hoadon (MaHD, MaKH, MaNV, NgayBan, HinhThucTT, GhiChu, TongTien)
                VALUES (%s,%s,%s,%s,%s,%s, 0)
            """, (
                mahd,
                self.kh_map[tenkh],
                self.nv_map[tennv],
                ngayban,
                hinhthuc,
                self.entry_ghichu.get().strip()
            ))

            conn.commit()
            conn.close()

            self.load_hd()
            self.clear_input()
            messagebox.showinfo("OK", "Thêm thành công!")

        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    # =====================================================
    # SEARCH
    # =====================================================
    def search_hd(self):
        keyword = self.entry_search.get().strip()
        field = self.cbb_search_type.get()

        try:
            conn = connect_db()
            cur = conn.cursor()

            if field == "HoTen":
                sql = """
                    SELECT h.MaHD, k.HoTen, n.HoTenNV, h.NgayBan, h.HinhThucTT, h.GhiChu, h.TongTien
                    FROM hoadon h
                    JOIN khachhang k ON h.MaKH = k.MaKH
                    JOIN nhanvien n ON h.MaNV = n.MaNV
                    WHERE k.HoTen LIKE %s
                """
            elif field == "HoTenNV":
                sql = """
                    SELECT h.MaHD, k.HoTen, n.HoTenNV, h.NgayBan, h.HinhThucTT, h.GhiChu, h.TongTien
                    FROM hoadon h
                    JOIN khachhang k ON h.MaKH = k.MaKH
                    JOIN nhanvien n ON h.MaNV = n.MaNV
                    WHERE n.HoTenNV LIKE %s
                """
            else:
                sql = f"""
                    SELECT h.MaHD, k.HoTen, n.HoTenNV, h.NgayBan, h.HinhThucTT, h.GhiChu, h.TongTien
                    FROM hoadon h
                    JOIN khachhang k ON h.MaKH = k.MaKH
                    JOIN nhanvien n ON h.MaNV = n.MaNV
                    WHERE h.{field} LIKE %s
                """

            cur.execute(sql, ('%' + keyword + '%',))
            rows = cur.fetchall()
            conn.close()

            self.tree.delete(*self.tree.get_children())

            for r in rows:
                tong = "{:,}".format(int(r[6])).replace(",", ".")
                new_r = list(r)
                new_r[6] = tong
                self.tree.insert("", "end", values=new_r)

        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    # =====================================================
    # LOAD SELECTED
    # =====================================================
    def load_selected_to_edit(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chưa chọn", "Chọn hóa đơn để sửa")

        data = self.tree.item(sel)["values"]

        self.entry_mahd.delete(0, tk.END)
        self.entry_mahd.insert(0, data[0])

        self.cbb_kh.set(data[1])
        self.cbb_nv.set(data[2])

        self.entry_ngayban.delete(0, tk.END)
        self.entry_ngayban.insert(0, data[3])

        self.cbb_hinhthuc.set(data[4])

        self.entry_ghichu.delete(0, tk.END)
        self.entry_ghichu.insert(0, data[5])

    # =====================================================
    # SAVE EDIT
    # =====================================================
    def save_edit(self):
        mahd = self.entry_mahd.get().strip()
        tenkh = self.cbb_kh.get()
        tennv = self.cbb_nv.get()
        ngayban = self.entry_ngayban.get().strip()
        hinhthuc = self.cbb_hinhthuc.get()

        if tenkh not in self.kh_map:
            return messagebox.showerror("Sai KH", "Khách hàng không tồn tại!")

        if tennv not in self.nv_map:
            return messagebox.showerror("Sai NV", "Nhân viên không tồn tại!")

        if not self.valid_date(ngayban):
            return messagebox.showerror("Sai ngày", "Ngày bán phải dạng yyyy-mm-dd!")

        try:
            conn = connect_db()
            cur = conn.cursor()

            cur.execute("""
                UPDATE hoadon SET
                    MaKH=%s, MaNV=%s, NgayBan=%s,
                    HinhThucTT=%s, GhiChu=%s
                WHERE MaHD=%s
            """, (
                self.kh_map[tenkh],
                self.nv_map[tennv],
                ngayban,
                hinhthuc,
                self.entry_ghichu.get().strip(),
                mahd
            ))

            conn.commit()
            conn.close()

            self.load_hd()
            self.clear_input()
            messagebox.showinfo("OK", "Sửa thành công!")

        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    # =====================================================
    # DELETE
    # =====================================================
    def delete_hd(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chưa chọn", "Hãy chọn hóa đơn để xóa!")

        mahd = self.tree.item(sel[0])["values"][0]

        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa hóa đơn {mahd}?"):
            return

        try:
            conn = connect_db()
            cur = conn.cursor()

            cur.execute("DELETE FROM ct_hoadon WHERE MaHD=%s", (mahd,))
            cur.execute("DELETE FROM hoadon WHERE MaHD=%s", (mahd,))

            conn.commit()
            conn.close()

            self.load_hd()
            messagebox.showinfo("OK", "Đã xóa hóa đơn!")

        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    # =====================================================
    # CLEAR
    # =====================================================
    def clear_input(self):
        self.entry_mahd.delete(0, tk.END)
        self.cbb_kh.set("")
        self.cbb_nv.set("")
        self.entry_ngayban.delete(0, tk.END)
        self.cbb_hinhthuc.set("")
        self.entry_ghichu.delete(0, tk.END)
