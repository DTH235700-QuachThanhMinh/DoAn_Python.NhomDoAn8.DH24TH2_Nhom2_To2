# vatlieu_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
from lienket import connect_db

class VatLieuFrame(tk.Frame):
    def __init__(self, parent, show_main_menu=None):
        super().__init__(parent, bg="white")
        self.show_main_menu = show_main_menu

        self.ncc_map = {}
        self.reload_ncc_map()

        self.create_ui()
        self.load_vl()

    # ===================================================================
    #               FORMAT & VALIDATION (THÊM GIỐNG NHÂN VIÊN)
    # ===================================================================

    def format_name(self, text):
        """Viết hoa từng chữ đầu giống Nhân Viên"""
        return " ".join(word.capitalize() for word in text.split())

    def valid_price(self, s):
        """Kiểm tra giá hợp lệ"""
        return s.replace(".", "").replace(",", "").isdigit()

    def format_price_display(self, s):
        """Hiển thị giá thành 1.000.000"""
        try:
            return "{:,}".format(int(s)).replace(",", ".")
        except:
            return s

    # ===================================================================
    #               LOAD MAP NHÀ CUNG CẤP
    # ===================================================================
    def reload_ncc_map(self):
        self.ncc_map = {}
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT MaNCC, TenNCC FROM nhacungcap")
            for ma, ten in cur.fetchall():
                self.ncc_map[ten] = ma
            conn.close()
        except:
            self.ncc_map = {}

    # ===================================================================
    #                                UI
    # ===================================================================
    def create_ui(self):
        tk.Label(self, text="QUẢN LÝ VẬT LIỆU", font=("Arial", 18, "bold"),
                 bg="white", fg="#003A75").pack(pady=10)

        frame_info = tk.Frame(self, bg="white")
        frame_info.pack(padx=20, pady=10, fill="x")

        for i in range(4):
            frame_info.columnconfigure(i, weight=1)

        self.entry_mavl = self._make_entry(frame_info, "Mã vật liệu:", 0, 0)
        self.entry_tenvl = self._make_entry(frame_info, "Tên vật liệu:", 0, 2)

        tk.Label(frame_info, text="Đơn vị tính:", bg="white").grid(row=1, column=0, sticky="w")
        self.cbb_donvi = ttk.Combobox(
            frame_info, state="readonly",
            values=[" ", "cây", "bao", "viên", "thùng", "m", "m²", "m³", "cuộn", "tấm", "thùng"]
        )
        self.cbb_donvi.grid(row=1, column=1, sticky="we", padx=5)
        self.cbb_donvi.set(" ")

        self.entry_gianhap = self._make_entry(frame_info, "Giá nhập:", 1, 2)
        self.entry_giaban = self._make_entry(frame_info, "Giá bán:", 2, 0)
        self.entry_tonkho = self._make_entry(frame_info, "Tồn kho:", 2, 2)

        tk.Label(frame_info, text="Nhà cung cấp:", bg="white").grid(row=3, column=0, sticky="w")
        self.cbb_ncc = ttk.Combobox(frame_info, state="readonly", values=list(self.ncc_map.keys()))
        self.cbb_ncc.grid(row=3, column=1, sticky="we", padx=5)

        # ------------------------------------------------------------------
        #                           TÌM KIẾM
        # ------------------------------------------------------------------
        frame_search = tk.Frame(self, bg="white")
        frame_search.pack(fill="x", padx=20)

        frame_search.columnconfigure(0, weight=3)

        tk.Label(frame_search, text="Tìm kiếm:", bg="white").grid(row=0, column=0, sticky="w")
        self.entry_search = tk.Entry(frame_search)
        self.entry_search.grid(row=1, column=0, sticky="we", padx=10)

        self.cbb_search_type = ttk.Combobox(
            frame_search,
            values=[" ", "MaVL", "TenVL", "DonViTinh", "TenNCC"],
            state="readonly"
        )
        self.cbb_search_type.grid(row=1, column=1, padx=5)
        self.cbb_search_type.set(" ")

        tk.Button(frame_search, text="Tìm kiếm",
                  bg="#003A75", fg="white",
                  width=12, command=self.search_vl).grid(row=1, column=2, padx=5)

        # ------------------------------------------------------------------
        #                                TABLE
        # ------------------------------------------------------------------
        tk.Label(self, text="Danh sách vật liệu", bg="white",
                 font=("Arial", 11, "bold")).pack(anchor="w", padx=20)

        columns = ("MaVL", "TenVL", "DonViTinh", "GiaNhap", "GiaBan", "TonKho", "TenNCC")

        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(fill="both", padx=10, pady=5)

        # ------------------------------------------------------------------
        #                             BUTTONS
        # ------------------------------------------------------------------
        frame_btn = tk.Frame(self, bg="white")
        frame_btn.pack(pady=10)

        btn = dict(width=15, fg="white", font=("Arial", 11, "bold"))

        tk.Button(frame_btn, text="Thêm", bg="#3498DB",
                  command=self.add_vl, **btn).grid(row=0, column=0, padx=5)
        tk.Button(frame_btn, text="Lưu", bg="#27AE60",
                  command=self.save_edit, **btn).grid(row=0, column=1, padx=5)
        tk.Button(frame_btn, text="Sửa", bg="#E74C3C",
                  command=self.load_selected_to_edit, **btn).grid(row=0, column=2, padx=5)
        tk.Button(frame_btn, text="Hủy", bg="#E67E22",
                  command=self.clear_input, **btn).grid(row=0, column=3, padx=5)
        tk.Button(frame_btn, text="Xóa", bg="#800080",
                  command=self.delete_vl, **btn).grid(row=0, column=4, padx=5)

    # ===================================================================
    #                          ENTRY TẠO NHANH
    # ===================================================================
    def _make_entry(self, parent, text, row, col):
        tk.Label(parent, text=text, bg="white").grid(row=row, column=col, sticky="w")
        e = tk.Entry(parent)
        e.grid(row=row, column=col+1, sticky="we", padx=5)
        return e

    # ===================================================================
    #                         LOAD VẬT LIỆU
    # ===================================================================
    def load_vl(self):
        self.reload_ncc_map()
        self.cbb_ncc["values"] = list(self.ncc_map.keys())

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT v.MaVL, v.TenVL, v.DonViTinh, v.GiaNhap,
                   v.GiaBan, v.TonKho, n.TenNCC
            FROM vatlieu v
            LEFT JOIN nhacungcap n ON v.MaNCC = n.MaNCC
        """)
        rows = cur.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())

        # format giá giống Nhân Viên
        for r in rows:
            r = list(r)
            r[3] = self.format_price_display(r[3])  # giá nhập
            r[4] = self.format_price_display(r[4])  # giá bán
            self.tree.insert("", "end", values=r)

    # ===================================================================
    #                               THÊM
    # ===================================================================
    def add_vl(self):
        mavl = self.entry_mavl.get()
        tenvl = self.format_name(self.entry_tenvl.get())
        dv = self.cbb_donvi.get()
        gianhap = self.entry_gianhap.get()
        giaban = self.entry_giaban.get()
        tonkho = self.entry_tonkho.get()
        tenncc = self.cbb_ncc.get()

        if not all([mavl, tenvl, dv, gianhap, giaban, tonkho, tenncc]):
            return messagebox.showwarning("Thiếu", "Vui lòng nhập đủ thông tin!")

        if not self.valid_price(gianhap) or not self.valid_price(giaban):
            return messagebox.showerror("Lỗi", "Giá phải là số!")

        mancc = self.ncc_map.get(tenncc)

        gianhap_num = int(gianhap.replace(".", "").replace(",", ""))
        giaban_num = int(giaban.replace(".", "").replace(",", ""))

        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO vatlieu (MaVL, TenVL, DonViTinh, GiaNhap, GiaBan, TonKho, MaNCC)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (mavl, tenvl, dv, gianhap_num, giaban_num, tonkho, mancc))
            conn.commit()
            messagebox.showinfo("OK", "Thêm thành công!")
            self.load_vl()
            self.clear_input()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        conn.close()

    # ===================================================================
    #                               XÓA
    # ===================================================================
    def delete_vl(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chưa chọn!", "Chọn vật liệu để xóa!")

        mavl = self.tree.item(sel)["values"][0]
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa nhân viên {mavl}?"):
            return

        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM vatlieu WHERE MaVL = %s", (mavl,))
            conn.commit()
            messagebox.showinfo("OK", "Xóa thành công!")
            self.load_vl()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        conn.close()

    # ===================================================================
    #                        LOAD ĐỂ SỬA
    # ===================================================================
    def load_selected_to_edit(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chưa chọn!", "Chọn vật liệu để sửa!")

        data = self.tree.item(sel)["values"]

        self.entry_mavl.delete(0, tk.END)
        self.entry_mavl.insert(0, data[0])

        self.entry_tenvl.delete(0, tk.END)
        self.entry_tenvl.insert(0, data[1])

        self.cbb_donvi.set(data[2])

        self.entry_gianhap.delete(0, tk.END)
        self.entry_gianhap.insert(0, data[3])

        self.entry_giaban.delete(0, tk.END)
        self.entry_giaban.insert(0, data[4])

        self.entry_tonkho.delete(0, tk.END)
        self.entry_tonkho.insert(0, data[5])

        self.cbb_ncc.set(data[6])

    # ===================================================================
    #                         LƯU SỬA
    # ===================================================================
    def save_edit(self):
        mavl = self.entry_mavl.get()
        tenvl = self.format_name(self.entry_tenvl.get())
        dv = self.cbb_donvi.get()
        gianhap = self.entry_gianhap.get()
        giaban = self.entry_giaban.get()
        tonkho = self.entry_tonkho.get()
        tenncc = self.cbb_ncc.get()

        if not self.valid_price(gianhap) or not self.valid_price(giaban):
            return messagebox.showerror("Lỗi", "Giá phải là số hợp lệ!")

        gianhap_num = int(gianhap.replace(".", "").replace(",", ""))
        giaban_num = int(giaban.replace(".", "").replace(",", ""))

        mancc = self.ncc_map.get(tenncc)

        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE vatlieu SET
                TenVL=%s, DonViTinh=%s, GiaNhap=%s, GiaBan=%s, TonKho=%s, MaNCC=%s
                WHERE MaVL=%s
            """, (tenvl, dv, gianhap_num, giaban_num, tonkho, mancc, mavl))

            conn.commit()
            messagebox.showinfo("OK", "Lưu thành công!")
            self.load_vl()
            self.clear_input()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        conn.close()

    # ===================================================================
    #                          TÌM KIẾM
    # ===================================================================
    def search_vl(self):
        keyword = self.entry_search.get().strip()
        field = self.cbb_search_type.get()

        if keyword == "":
            return self.load_vl()

        conn = connect_db()
        cur = conn.cursor()

        if field == "TenNCC":
            cur.execute("""
                SELECT v.MaVL, v.TenVL, v.DonViTinh, v.GiaNhap,
                       v.GiaBan, v.TonKho, n.TenNCC
                FROM vatlieu v
                LEFT JOIN nhacungcap n ON v.MaNCC = n.MaNCC
                WHERE n.TenNCC LIKE %s
            """, ('%' + keyword + '%',))
        else:
            cur.execute(f"""
                SELECT v.MaVL, v.TenVL, v.DonViTinh, v.GiaNhap,
                       v.GiaBan, v.TonKho, n.TenNCC
                FROM vatlieu v
                LEFT JOIN nhacungcap n ON v.MaNCC = n.MaNCC
                WHERE {field} LIKE %s
            """, ('%' + keyword + '%',))

        rows = cur.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())

        # format giá lại
        for r in rows:
            r = list(r)
            r[3] = self.format_price_display(r[3])
            r[4] = self.format_price_display(r[4])
            self.tree.insert("", "end", values=r)

    # ===================================================================
    #                          CLEAR INPUT
    # ===================================================================
    def clear_input(self):
        self.entry_mavl.delete(0, tk.END)
        self.entry_tenvl.delete(0, tk.END)
        self.cbb_donvi.set(" ")
        self.entry_gianhap.delete(0, tk.END)
        self.entry_giaban.delete(0, tk.END)
        self.entry_tonkho.delete(0, tk.END)
        self.cbb_ncc.set("")
