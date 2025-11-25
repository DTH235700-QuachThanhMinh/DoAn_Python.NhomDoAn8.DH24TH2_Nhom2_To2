import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import decimal
from lienket import connect_db

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


class CTPhieuNhapFrame(tk.Frame):

    def __init__(self, parent, show_main_menu=None):
        super().__init__(parent, bg="white")
        self.show_main_menu = show_main_menu

        # mapping từ Tên -> Mã (vật liệu)
        self._name_to_code = {}
        # MaPN list
        self._mapn_list = []
        self._editing_original = None

        self.create_ui()
        self.load_material_map()
        self.load_mapn_list()
        self.load_table()

    # ======================= HELPERS =======================
    def _format_thousands(self, value):
        """Chuyển số (int/Decimal/str chứa số) thành chuỗi hiển thị 1.000"""
        try:
            # xử lý chuỗi có dấu . hoặc , trước
            s = str(value)
            s = s.replace(".", "").replace(",", "")
            iv = int(decimal.Decimal(s))
            return "{:,}".format(iv).replace(",", ".")
        except Exception:
            return str(value)

    def _parse_number(self, s):
        """Loại bỏ dấu phân cách và trả về Decimal. Nếu không parse được ném exception."""
        if s is None:
            return decimal.Decimal(0)
        txt = str(s).replace(".", "").replace(",", "").strip()
        if txt == "":
            return decimal.Decimal(0)
        return decimal.Decimal(txt)

    def _format_entry_thousands(self, entry_widget):
        """Dùng để bind KeyRelease: giữ lại các chữ số, định dạng hiển thị với dấu '.'"""
        txt = entry_widget.get()
        # cho phép chỉ số nguyên (loại bỏ ký tự không phải số)
        filtered = "".join(ch for ch in txt if ch.isdigit())
        if filtered == "":
            entry_widget.delete(0, tk.END)
            return
        try:
            iv = int(filtered)
            formatted = "{:,}".format(iv).replace(",", ".")
            # set mới
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, formatted)
            # đặt con trỏ cuối
            entry_widget.icursor(tk.END)
        except Exception:
            # nếu lỗi giữ nguyên
            pass

    # ============================================================
    # UI
    # ============================================================
    def create_ui(self):
        tk.Label(self, text="CHI TIẾT PHIẾU NHẬP",
                 font=("Arial", 18, "bold"), bg="white", fg="#003A75"
                 ).pack(pady=10)

        frame_info = tk.Frame(self, bg="white")
        frame_info.pack(padx=20, fill="x")

        for i in range(4):
            frame_info.columnconfigure(i, weight=1)

        # MaPN: COMBO (không cho nhập tay)
        tk.Label(frame_info, text="Mã Phiếu Nhập:", bg="white").grid(row=0, column=0, sticky="w")
        self.cbb_mapn = ttk.Combobox(frame_info, state="readonly")
        self.cbb_mapn.grid(row=0, column=1, sticky="we", padx=5)

        # TenVL: COMBO (không cho nhập tay)
        tk.Label(frame_info, text="Tên vật liệu:", bg="white").grid(row=0, column=2, sticky="w")
        self.cbb_tenvl = ttk.Combobox(frame_info, state="readonly")
        self.cbb_tenvl.grid(row=0, column=3, sticky="we", padx=5)
        self.cbb_tenvl.bind("<<ComboboxSelected>>", lambda e: self.on_tenvl_selected())

        # MaVL read-only (hiển thị)
        tk.Label(frame_info, text="Mã VL:", bg="white").grid(row=1, column=0, sticky="w")
        self.entry_mavl = tk.Entry(frame_info, state="readonly")
        self.entry_mavl.grid(row=1, column=1, sticky="we", padx=5)

        tk.Label(frame_info, text="Số lượng:", bg="white").grid(row=1, column=2, sticky="w")
        self.entry_soluong = tk.Entry(frame_info)
        self.entry_soluong.grid(row=1, column=3, sticky="we", padx=5)
        # format khi gõ
        self.entry_soluong.bind("<KeyRelease>", lambda e: (self._format_entry_thousands(self.entry_soluong), self.compute_total()))

        tk.Label(frame_info, text="Đơn giá:", bg="white").grid(row=2, column=0, sticky="w")
        self.entry_dongia = tk.Entry(frame_info)
        self.entry_dongia.grid(row=2, column=1, sticky="we", padx=5)
        self.entry_dongia.bind("<KeyRelease>", lambda e: (self._format_entry_thousands(self.entry_dongia), self.compute_total()))

        tk.Label(frame_info, text="Thành tiền:", bg="white").grid(row=2, column=2, sticky="w")
        self.var_thanhtien = tk.StringVar(value="0")
        tk.Entry(frame_info, textvariable=self.var_thanhtien, state="readonly").grid(
            row=2, column=3, sticky="we", padx=5
        )

        # SEARCH
        frame_search = tk.Frame(self, bg="white")
        frame_search.pack(padx=20, fill="x", pady=10)
        frame_search.columnconfigure(0, weight=3)

        tk.Label(frame_search, text="Tìm kiếm:", bg="white").grid(row=0, column=0, sticky="w")
        self.entry_search = tk.Entry(frame_search)
        self.entry_search.grid(row=1, column=0, sticky="we", padx=10)

        self.cbb_search_type = ttk.Combobox(frame_search,
                                           values=[" ", "MaPN", "TenVL", "SoLuongNhap", "DonGiaNhap"], state="readonly")
        self.cbb_search_type.set(" ")
        self.cbb_search_type.grid(row=1, column=1, padx=5)

        tk.Button(frame_search, text="Tìm", bg="#003A75", fg="white", width=12,
                  command=self.search).grid(row=1, column=2, padx=5)

        # TABLE
        cols = ("MaPN", "TenVL", "SoLuongNhap", "DonGiaNhap", "ThanhTien", "MaVL")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=13)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=150)
        self.tree.pack(fill="both", padx=20, pady=10)
        self.tree.bind("<Double-1>", lambda e: self.load_for_edit())

        # BUTTONS
        frame_btn = tk.Frame(self, bg="white")
        frame_btn.pack(pady=10)

        btn = dict(width=15, fg="white", font=("Arial", 11, "bold"))
        tk.Button(frame_btn, text="Thêm", bg="#3498DB", command=self.add_ct, **btn).grid(row=0, column=0, padx=5)
        tk.Button(frame_btn, text="Sửa", bg="#E67E22", command=self.load_for_edit, **btn).grid(row=0, column=1, padx=5)
        tk.Button(frame_btn, text="Lưu", bg="#27AE60", command=self.save_edit, **btn).grid(row=0, column=2, padx=5)
        tk.Button(frame_btn, text="Xóa", bg="#C0392B", command=self.delete_ct, **btn).grid(row=0, column=3, padx=5)
        tk.Button(frame_btn, text="Hủy", bg="#7D3C98", command=self.clear_inputs, **btn).grid(row=0, column=4, padx=5)

    # ============================================================
    def on_tenvl_selected(self):
        """Khi chọn tên vật liệu, set MaVL lên entry_mavl"""
        name = self.cbb_tenvl.get()
        mavl = self._name_to_code.get(name, "")
        # set entry_mavl (readonly)
        self.entry_mavl.config(state="normal")
        self.entry_mavl.delete(0, tk.END)
        self.entry_mavl.insert(0, mavl)
        self.entry_mavl.config(state="readonly")

    # ============================================================
    def compute_total(self):
        """Tính Thành tiền theo Số lượng và Đơn giá; hiển thị đã format"""
        try:
            sl = self._parse_number(self.entry_soluong.get())
            dg = self._parse_number(self.entry_dongia.get())
            tt = sl * dg
            # hiển thị với dấu chấm
            self.var_thanhtien.set(self._format_thousands(tt))
        except Exception:
            self.var_thanhtien.set("0")

    # ============================================================
    def load_material_map(self):
        """Load tên vật liệu -> mã vật liệu và set combobox TenVL"""
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT MaVL, TenVL FROM vatlieu")
        rows = cur.fetchall()
        conn.close()
        self._name_to_code = {ten: ma for ma, ten in rows}
        names = [""] + [ten for _, ten in rows]
        self.cbb_tenvl['values'] = names
        self.cbb_tenvl.set("")

    def load_mapn_list(self):
        """Load danh sách MaPN vào combobox (không cho nhập tay)"""
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT MaPN FROM phieunhap ORDER BY MaPN")
        rows = cur.fetchall()
        conn.close()
        self._mapn_list = [r[0] for r in rows]
        vals = [""] + self._mapn_list
        self.cbb_mapn['values'] = vals
        self.cbb_mapn.set("")

    # ============================================================
    def load_table(self):
        self.tree.delete(*self.tree.get_children())
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT c.MaPN, v.TenVL, c.SoLuongNhap, c.DonGiaNhap, c.ThanhTien, c.MaVL
            FROM ct_phieunhap c
            JOIN vatlieu v ON c.MaVL = v.MaVL
            ORDER BY c.MaPN
        """)
        rows = cur.fetchall()
        conn.close()
        for row in rows:
            r = list(row)
            # format số hiển thị
            try:
                r[2] = self._format_thousands(r[2])  # SoLuongNhap
                r[3] = self._format_thousands(r[3])  # DonGiaNhap
                r[4] = self._format_thousands(r[4])  # ThanhTien
            except:
                pass
            self.tree.insert("", "end", values=r)

    # ============================================================
    def update_tong_tien(self, mapn):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE phieunhap
            SET TongTien = (SELECT COALESCE(SUM(ThanhTien),0) FROM ct_phieunhap WHERE MaPN=%s)
            WHERE MaPN=%s
        """, (mapn, mapn))
        conn.commit()
        conn.close()

    def check_mapn_exists(self, mapn):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT MaPN FROM phieunhap WHERE MaPN=%s", (mapn,))
        ok = cur.fetchone()
        conn.close()
        return ok is not None

    # ============================================================
    def add_ct(self):
        mapn = self.cbb_mapn.get().strip()
        tenvl = self.cbb_tenvl.get().strip()

        if not mapn:
            return messagebox.showerror("Lỗi", "Vui lòng chọn Mã phiếu nhập!")
        if not self.check_mapn_exists(mapn):
            return messagebox.showerror("Lỗi", "Mã phiếu nhập không tồn tại!")

        mavl = self._name_to_code.get(tenvl)
        if not mavl:
            return messagebox.showerror("Lỗi", "Vui lòng chọn Tên vật liệu!")

        try:
            sl = self._parse_number(self.entry_soluong.get())
            dg = self._parse_number(self.entry_dongia.get())
        except Exception:
            return messagebox.showerror("Lỗi", "Sai định dạng số!")

        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO ct_phieunhap (MaPN, MaVL, SoLuongNhap, DonGiaNhap)
                VALUES (%s,%s,%s,%s)
            """, (mapn, mavl, float(sl), float(dg)))
            conn.commit()
            messagebox.showinfo("OK", "Thêm thành công!")
            conn.close()
        except Exception as e:
            return messagebox.showerror("Lỗi khi lưu", str(e))

        self.update_tong_tien(mapn)
        self.load_table()
        self.clear_inputs()

    # ============================================================
    def load_for_edit(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chưa chọn!", "Chọn vật liệu để sửa!")

        mapn, tenvl, sl, dg, tt, mavl = self.tree.item(sel)["values"]

        # Set combobox và entries (lưu ý: tree chứa dữ liệu đã format)
        self.cbb_mapn.set(mapn)
        self.cbb_tenvl.set(tenvl)

        # set MaVL
        self.entry_mavl.config(state="normal")
        self.entry_mavl.delete(0, tk.END)
        self.entry_mavl.insert(0, mavl)
        self.entry_mavl.config(state="readonly")

        # set số lượng & đơn giá (để dạng hiển thị đã format)
        self.entry_soluong.delete(0, tk.END)
        self.entry_soluong.insert(0, sl)
        self.entry_dongia.delete(0, tk.END)
        self.entry_dongia.insert(0, dg)
        self.var_thanhtien.set(tt)

        self._editing_original = {"MaPN": mapn, "MaVL": mavl}

    # ============================================================
    def save_edit(self):
        if not self._editing_original:
            return

        oldpn = self._editing_original["MaPN"]
        oldvl = self._editing_original["MaVL"]

        mapn = self.cbb_mapn.get().strip()
        tenvl = self.cbb_tenvl.get().strip()
        mavl = self._name_to_code.get(tenvl)

        if not mavl:
            return messagebox.showerror("Lỗi", "Vui lòng chọn Tên vật liệu!")

        try:
            sl = self._parse_number(self.entry_soluong.get())
            dg = self._parse_number(self.entry_dongia.get())
        except Exception:
            return messagebox.showerror("Lỗi", "Sai định dạng số!")

        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                UPDATE ct_phieunhap
                SET SoLuongNhap=%s, DonGiaNhap=%s
                WHERE MaPN=%s AND MaVL=%s
            """, (float(sl), float(dg), oldpn, oldvl))
            conn.commit()
            conn.close()
        except Exception as e:
            return messagebox.showerror("Lỗi khi cập nhật", str(e))

        self.update_tong_tien(mapn)
        self.load_table()
        self.clear_inputs()

    # ============================================================
    def delete_ct(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Thông báo", "Chọn dòng để xóa!")

        item = sel[0]
        mapn, tenvl, sl, dg, tt, mavl = self.tree.item(item)["values"]

        if not messagebox.askyesno("Xác nhận", f"Xóa vật liệu '{tenvl}' khỏi phiếu nhập {mapn}?"):
            return

        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM ct_phieunhap WHERE MaPN=%s AND MaVL=%s",
                (mapn, mavl)
            )
            conn.commit()
            conn.close()
            self.update_tong_tien(mapn)
            self.load_table()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # ============================================================
    def search(self):
        key = self.entry_search.get().strip()

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT c.MaPN, v.TenVL, c.SoLuongNhap, c.DonGiaNhap, c.ThanhTien, c.MaVL
            FROM ct_phieunhap c
            JOIN vatlieu v ON c.MaVL = v.MaVL
            WHERE 
                c.MaPN LIKE %s OR 
                v.TenVL LIKE %s
        """, (f"%{key}%", f"%{key}%"))

        rows = cur.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        for r in rows:
            row = list(r)
            try:
                row[2] = self._format_thousands(row[2])
                row[3] = self._format_thousands(row[3])
                row[4] = self._format_thousands(row[4])
            except:
                pass
            self.tree.insert("", "end", values=row)

    # ============================================================
    def clear_inputs(self):
        self.cbb_mapn.set("")
        self.cbb_tenvl.set("")
        self.entry_mavl.config(state="normal")
        self.entry_mavl.delete(0, tk.END)
        self.entry_mavl.config(state="readonly")
        self.entry_soluong.delete(0, tk.END)
        self.entry_dongia.delete(0, tk.END)
        self.var_thanhtien.set("0")
        self._editing_original = None
