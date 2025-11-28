import tkinter as tk
from tkinter import ttk, messagebox
import decimal
from lienket import connect_db

class CTHoaDonFrame(tk.Frame):

    def __init__(self, parent, show_main_menu=None):
        super().__init__(parent, bg="white")
        self.show_main_menu = show_main_menu

        self.vl_name_to_code = {}
        self.list_mahd = []
        self._editing_original = None

        # load danh sách Mã hóa đơn và Vật liệu (TenVL->MaVL)
        self.load_maps()

        self.create_ui()
        self.load_table()

    # ----------------------
    # Load maps from DB
    # ----------------------
    def load_maps(self):
        try:
            conn = connect_db()
            cur = conn.cursor()

            # danh sách hóa đơn (MaHD)
            cur.execute("SELECT MaHD FROM hoadon ORDER BY MaHD")
            self.list_mahd = [r[0] for r in cur.fetchall()]

            # tên vật liệu -> mã vật liệu
            cur.execute("SELECT MaVL, TRIM(TenVL) FROM vatlieu ORDER BY TenVL")
            mats = cur.fetchall()
            conn.close()
            self.vl_name_to_code = {ten: ma for ma, ten in mats}

        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))
            self.list_mahd = []
            self.vl_name_to_code = {}

    # ----------------------
    # UI
    # ----------------------
    def create_ui(self):
        tk.Label(self, text="CHI TIẾT HÓA ĐƠN",
                 font=("Arial", 18, "bold"),
                 bg="white", fg="#003A75").pack(pady=10)

        # ------------------- FORM INPUT -------------------
        frame_info = tk.Frame(self, bg="white")
        frame_info.pack(padx=20, pady=10, fill="x")

        for i in range(4):
            frame_info.columnconfigure(i, weight=1)

        # ---- Row 1: MaHD (combobox) and TenVL (combobox) ----
        tk.Label(frame_info, text="Mã hóa đơn:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.cbb_mahd = ttk.Combobox(frame_info, state="readonly", values=self.list_mahd)
        self.cbb_mahd.grid(row=0, column=1, sticky="we", padx=5)
        # allow refresh of mahd list from DB
        tk.Button(frame_info, text="↻", width=3, command=self.refresh_mahd_list).grid(row=0, column=2, sticky="w")

        tk.Label(frame_info, text="Tên vật liệu:", bg="white").grid(row=0, column=2, sticky="w", pady=5)
        self.cbb_tenvl = ttk.Combobox(frame_info, state="readonly", values=list(self.vl_name_to_code.keys()))
        self.cbb_tenvl.grid(row=0, column=3, sticky="we", padx=5)
        self.cbb_tenvl.bind("<<ComboboxSelected>>", lambda e: self.on_tenvl_selected())

        # ---- Row 2: SoLuong & DonGia ----
        tk.Label(frame_info, text="Số lượng:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_soluong = tk.Entry(frame_info)
        self.entry_soluong.grid(row=1, column=1, sticky="we", padx=5)
        self.entry_soluong.bind("<KeyRelease>", lambda e: self.compute_thanhtien())

        tk.Label(frame_info, text="Đơn giá:", bg="white").grid(row=1, column=2, sticky="w", pady=5)
        self.entry_dongia = tk.Entry(frame_info)
        self.entry_dongia.grid(row=1, column=3, sticky="we", padx=5)
        self.entry_dongia.bind("<KeyRelease>", lambda e: self.compute_thanhtien())

        # ---- Row 3: ThanhTien (readonly) ----
        tk.Label(frame_info, text="Thành tiền:", bg="white").grid(row=2, column=0, sticky="w", pady=5)
        self.var_thanhtien = tk.StringVar(value="0")
        tk.Entry(frame_info, textvariable=self.var_thanhtien, state="readonly").grid(row=2, column=1, sticky="we", padx=5)

        # ------------------- SEARCH -------------------
        frame_search = tk.Frame(self, bg="white")
        frame_search.pack(padx=20, pady=10, fill="x")
        frame_search.columnconfigure(0, weight=3)

        tk.Label(frame_search, text="Tìm kiếm:", bg="white").grid(row=0, column=0, sticky="w")
        self.entry_search = tk.Entry(frame_search)
        self.entry_search.grid(row=1, column=0, sticky="we", padx=10)

        self.cbb_search_type = ttk.Combobox(frame_search,
                            values=[" ", "MaHD", "TenVL", "SoLuong"], state="readonly")
        self.cbb_search_type.grid(row=1, column=1, padx=5)
        self.cbb_search_type.set(" ")

        tk.Button(frame_search, text="Tìm", width=12,
                  bg="#003A75", fg="white",
                  command=self.search).grid(row=1, column=2, padx=5)

        # ------------------- TABLE -------------------
        tk.Label(self, text="Danh sách chi tiết hóa đơn",
                 bg="white", font=("Arial", 11, "bold")).pack(anchor="w", padx=20)

        cols = ("MaHD", "TenVL", "SoLuong", "DonGia", "ThanhTien", "MaVL")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)

        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center", width=140)

        self.tree.pack(padx=10, pady=6, fill="both")
        self.tree.bind("<Double-1>", lambda e: self.load_selected_edit())

        # ------------------- BUTTONS -------------------
        frame_btn = tk.Frame(self, bg="white")
        frame_btn.pack(pady=10)

        btn = dict(width=15, fg="white", font=("Arial", 11, "bold"))

        tk.Button(frame_btn, text="Thêm", bg="#3498DB",
                  command=self.add_ct, **btn).grid(row=0, column=0, padx=5)
        tk.Button(frame_btn, text="Sửa", bg="#E67E22",
                  command=self.load_selected_edit, **btn).grid(row=0, column=1, padx=5)
        tk.Button(frame_btn, text="Lưu", bg="#27AE60",
                  command=self.save_edit, **btn).grid(row=0, column=2, padx=5)
        tk.Button(frame_btn, text="Xóa", bg="#800080",
                  command=self.delete_ct, **btn).grid(row=0, column=3, padx=5)
        tk.Button(frame_btn, text="Hủy", bg="#E74C3C",
                  command=self.clear_inputs, **btn).grid(row=0, column=4, padx=5)

    # ----------------------
    # helper format: format money for display 1.000.000
    # ----------------------
    def format_money_display(self, value):
        try:
            # allow floats or ints; display without decimals if whole
            if value is None:
                return "0"
            # if it's a decimal.Decimal or str, convert to int if no fraction
            v = float(value)
            if v.is_integer():
                return "{:,}".format(int(v)).replace(",", ".")
            else:
                # show with 2 decimals, replace comma with dot thousands
                s = "{:,.2f}".format(v)
                return s.replace(",", ".")
        except:
            return str(value)

    # ----------------------
    # compute thanhtien and show formatted
    # ----------------------
    def compute_thanhtien(self):
        try:
            sl_text = self.entry_soluong.get().strip() or "0"
            dg_text = self.entry_dongia.get().strip() or "0"

            # accept numbers with thousand separators either '.' or ','
            sl_clean = sl_text.replace(".", "").replace(",", "")
            dg_clean = dg_text.replace(".", "").replace(",", "")

            sl = decimal.Decimal(sl_clean)
            dg = decimal.Decimal(dg_clean)
            tt = sl * dg
            # display formatted
            self.var_thanhtien.set(self.format_money_display(tt))
        except:
            self.var_thanhtien.set("0")

    # ----------------------
    # load table
    # ----------------------
    def load_table(self):
        self.reload_maps_and_comboboxes()
        self.tree.delete(*self.tree.get_children())

        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT c.MaHD, v.TenVL, c.SoLuong, c.DonGia, c.ThanhTien, c.MaVL
                FROM ct_hoadon c
                LEFT JOIN vatlieu v ON c.MaVL = v.MaVL
                ORDER BY c.MaHD
            """)
            rows = cur.fetchall()
            conn.close()

            for r in rows:
                r = list(r)
                # format DonGia and ThanhTien for display
                try:
                    r[3] = self.format_money_display(r[3])
                except:
                    pass
                try:
                    r[4] = self.format_money_display(r[4])
                except:
                    pass
                self.tree.insert("", "end", values=r)

        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    # ----------------------
    # reload maps & combobox values
    # ----------------------
    def reload_maps_and_comboboxes(self):
        self.load_maps()
        # refresh combobox lists
        self.cbb_mahd['values'] = self.list_mahd
        self.cbb_tenvl['values'] = list(self.vl_name_to_code.keys())

    def refresh_mahd_list(self):
        self.reload_maps_and_comboboxes()
        messagebox.showinfo("OK", "Đã refresh danh sách Mã hóa đơn và Vật liệu")

    def on_tenvl_selected(self):
        # when a TenVL selected, optionally you could auto-fill DonGia from vatlieu table
        # but to keep "thêm không sửa" spirit, we just ensure mapping exists
        sel = self.cbb_tenvl.get()
        if sel and sel not in self.vl_name_to_code:
            messagebox.showwarning("Lỗi", "Tên vật liệu không tồn tại trong DB!")

    # ----------------------
    # ADD
    # ----------------------
    def add_ct(self):
        mahd = self.cbb_mahd.get().strip()
        tenvl = self.cbb_tenvl.get().strip()

        if not mahd:
            return messagebox.showwarning("Thiếu dữ liệu", "Chưa chọn Mã hóa đơn!")
        if not tenvl:
            return messagebox.showwarning("Thiếu dữ liệu", "Chưa chọn Tên vật liệu!")

        if tenvl not in self.vl_name_to_code:
            return messagebox.showerror("Lỗi", "Tên vật liệu không tồn tại!")

        mavl = self.vl_name_to_code[tenvl]

        # parse numbers, accept thousand separators
        try:
            sl_text = self.entry_soluong.get().strip()
            dg_text = self.entry_dongia.get().strip()
            sl = decimal.Decimal(sl_text.replace(".", "").replace(",", ""))
            dg = decimal.Decimal(dg_text.replace(".", "").replace(",", ""))
        except Exception:
            return messagebox.showwarning("Sai dữ liệu", "Số lượng hoặc đơn giá không hợp lệ!")

        try:
            conn = connect_db()
            cur = conn.cursor()

            # insert
            cur.execute("""
                INSERT INTO ct_hoadon (MaHD, MaVL, SoLuong, DonGia)
                VALUES (%s, %s, %s, %s)
            """, (mahd, mavl, float(sl), float(dg)))

            # update tong tien (IFNULL / COALESCE for safety)
            cur.execute("""
                UPDATE hoadon
                SET TongTien = (SELECT IFNULL(SUM(ThanhTien),0) FROM ct_hoadon WHERE MaHD=%s)
                WHERE MaHD=%s
            """, (mahd, mahd))

            conn.commit()
            conn.close()

            self.load_table()
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # ----------------------
    # load selected row into form (for edit)
    # ----------------------
    def load_selected_edit(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chọn dòng!", "Hãy chọn chi tiết hóa đơn để sửa!")

        item = sel[0]
        mahd, tenvl, sl, dg, tt, mavl = self.tree.item(item)["values"]

        # set comboboxes / entries
        self.cbb_mahd.set(mahd)
        self.cbb_tenvl.set(tenvl)

        self.entry_soluong.delete(0, tk.END)
        self.entry_soluong.insert(0, str(sl))

        # DonGia may be displayed formatted in grid; convert to plain numeric for edit if needed
        try:
            dg_plain = str(dg).replace(".", "").replace(",", "")
            self.entry_dongia.delete(0, tk.END)
            self.entry_dongia.insert(0, dg_plain)
        except:
            self.entry_dongia.delete(0, tk.END)
            self.entry_dongia.insert(0, str(dg))

        # show ThanhTien formatted
        self.var_thanhtien.set(self.format_money_display(tt))

        self._editing_original = {"MaHD": mahd, "MaVL": mavl}

    # ----------------------
    # save edit
    # ----------------------
    def save_edit(self):
        if not self._editing_original:
            return messagebox.showwarning("Lỗi", "Bạn chưa chọn dòng để sửa!")

        mahd_old = self._editing_original["MaHD"]
        mavl_old = self._editing_original["MaVL"]

        mahd_new = self.cbb_mahd.get().strip()
        tenvl = self.cbb_tenvl.get().strip()

        if not mahd_new:
            return messagebox.showwarning("Thiếu dữ liệu", "Chưa chọn Mã hóa đơn!")

        if tenvl not in self.vl_name_to_code:
            return messagebox.showerror("Lỗi", "Tên vật liệu không tồn tại!")

        mavl_new = self.vl_name_to_code[tenvl]

        try:
            sl_text = self.entry_soluong.get().strip()
            dg_text = self.entry_dongia.get().strip()
            sl = decimal.Decimal(sl_text.replace(".", "").replace(",", ""))
            dg = decimal.Decimal(dg_text.replace(".", "").replace(",", ""))
        except:
            return messagebox.showwarning("Sai", "Số lượng / giá không hợp lệ!")

        try:
            conn = connect_db()
            cur = conn.cursor()

            cur.execute("""
                UPDATE ct_hoadon
                SET MaHD=%s, MaVL=%s, SoLuong=%s, DonGia=%s
                WHERE MaHD=%s AND MaVL=%s
            """, (mahd_new, mavl_new, float(sl), float(dg), mahd_old, mavl_old))

            cur.execute("""
                UPDATE hoadon
                SET TongTien = (SELECT IFNULL(SUM(ThanhTien),0) FROM ct_hoadon WHERE MaHD=%s)
                WHERE MaHD=%s
            """, (mahd_new, mahd_new))

            conn.commit()
            conn.close()

            self.load_table()
            self.clear_inputs()
            self._editing_original = None
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # ----------------------
    # delete
    # ----------------------
    def delete_ct(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chưa chọn!", "Chọn dòng để xóa!")

        item = sel[0]
        mahd, tenvl, sl, dg, tt, mavl = self.tree.item(item)["values"]

        if not messagebox.askyesno("Xác nhận", f"Xóa vật liệu '{tenvl}' khỏi hóa đơn {mahd}?"):
            return

        try:
            conn = connect_db()
            cur = conn.cursor()

            cur.execute("DELETE FROM ct_hoadon WHERE MaHD=%s AND MaVL=%s", (mahd, mavl))

            cur.execute("""
                UPDATE hoadon
                SET TongTien = (
                    SELECT IFNULL(SUM(ThanhTien), 0)
                    FROM ct_hoadon
                    WHERE MaHD=%s
                )
                WHERE MaHD=%s
            """, (mahd, mahd))

            conn.commit()
            conn.close()

            self.load_table()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # ----------------------
    # search
    # ----------------------
    def search(self):
        key = self.entry_search.get().strip()
        if not key:
            return self.load_table()

        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT c.MaHD, v.TenVL, c.SoLuong, c.DonGia, c.ThanhTien, c.MaVL
                FROM ct_hoadon c
                LEFT JOIN vatlieu v ON c.MaVL=v.MaVL
                WHERE c.MaHD LIKE %s OR v.TenVL LIKE %s
            """, ("%" + key + "%", "%" + key + "%"))
            rows = cur.fetchall()
            conn.close()

            self.tree.delete(*self.tree.get_children())
            for r in rows:
                r = list(r)
                # format money cols
                try:
                    r[3] = self.format_money_display(r[3])
                except:
                    pass
                try:
                    r[4] = self.format_money_display(r[4])
                except:
                    pass
                self.tree.insert("", "end", values=r)
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    # ----------------------
    # clear inputs
    # ----------------------
    def clear_inputs(self):
        self.cbb_mahd.set("")
        self.cbb_tenvl.set("")
        self.entry_soluong.delete(0, tk.END)
        self.entry_dongia.delete(0, tk.END)
        self.var_thanhtien.set("0")
        self._editing_original = None
