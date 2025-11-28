import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from db_functions import (
    load_table, add_record, delete_record, update_record, search_record
)

class NhanVienFrame(tk.Frame):
    def __init__(self, parent, show_main_menu=None):
        super().__init__(parent, bg="white")
        self.show_main_menu = show_main_menu
        self.create_ui()
        self.load_nv()

    # ==============================================================================
    #                               VALIDATION & FORMAT
    # ==============================================================================
    def valid_phone(self, phone):
        return phone.isdigit() and len(phone) == 10

    def valid_date(self, date_text):
        try:
            datetime.datetime.strptime(date_text, "%Y-%m-%d")
            return True
        except:
            return False

    def valid_salary(self, salary):
        cleaned = salary.replace(".", "").replace(",", "")
        return cleaned.isdigit()

    def format_name(self, text):
        return " ".join(word.capitalize() for word in text.split())

    def format_salary_display(self, s):
        """Hiện lương dạng 1.000.000"""
        try:
            return "{:,}".format(int(s)).replace(",", ".")
        except:
            return s

    # ====================================================================================
    #                                      TẠO GIAO DIỆN
    # ====================================================================================
    def create_ui(self):

        tk.Label(
            self, text="QUẢN LÝ NHÂN VIÊN",
            font=("Arial", 18, "bold"),
            bg="white", fg="#003A75"
        ).pack(pady=10)

        frame_nv_info = tk.Frame(self, bg="white")
        frame_nv_info.pack(padx=20, pady=10, fill="x")

        for i in range(4):
            frame_nv_info.columnconfigure(i, weight=1)

        self.entry_manv = self._make_entry(frame_nv_info, "Mã nhân viên:", 0, 0)
        self.cbb_chucvu = self._make_combo(frame_nv_info, "Chức vụ:", 0, 2,
                                           [" ", "Quản lý", "Kế toán", "Lái xe", "Nhân viên bán hàng", "Nhân viên kho"])

        self.entry_hotennv = self._make_entry(frame_nv_info, "Họ tên:", 1, 0)
        self.entry_sdt = self._make_entry(frame_nv_info, "Số điện thoại:", 1, 2)

        tk.Label(frame_nv_info, text="Phái:", bg="white").grid(row=2, column=0, sticky="w", pady=5)
        frame_gt = tk.Frame(frame_nv_info, bg="white")
        frame_gt.grid(row=2, column=1, sticky="we", padx=5)

        self.var_phai = tk.StringVar(value="Nam")
        tk.Radiobutton(frame_gt, text="Nam", variable=self.var_phai, value="Nam", bg="white").pack(side="left")
        tk.Radiobutton(frame_gt, text="Nữ", variable=self.var_phai, value="Nữ", bg="white").pack(side="left")

        self.entry_ngaysinh = self._make_entry(frame_nv_info, "Ngày sinh (yyyy-mm-dd):", 2, 2)

        self.entry_diachi = self._make_entry(frame_nv_info, "Địa chỉ:", 3, 0)
        self.entry_luong = self._make_entry(frame_nv_info, "Lương:", 3, 2)

        self.cbb_tinhtrang = self._make_combo(frame_nv_info, "Tình trạng:", 4, 0, [" ", "Đang làm", "Nghỉ việc", "Tạm nghỉ"])

        # ================================= SEARCH ==============================
        frame_search = tk.Frame(self, bg="white")
        frame_search.pack(padx=20, pady=10, fill="x")

        frame_search.columnconfigure(0, weight=3)

        tk.Label(frame_search, text="Tìm kiếm:", bg="white").grid(row=0, column=0, sticky="w")
        self.entry_search = tk.Entry(frame_search)
        self.entry_search.grid(row=1, column=0, sticky="we", padx=10)

        self.cbb_search_type = ttk.Combobox(frame_search, values=[" ", "MaNV", "HoTenNV", "Sdt", "ChucVu", "TinhTrang"],
            state="readonly")
        self.cbb_search_type.grid(row=1, column=1, padx=5)

        tk.Button(frame_search, text="Tìm", bg="#003A75", fg="white", width=12, command=self.search_nv
                  ).grid(row=1, column=2, padx=5)

        # ================================ TABLE ========================================
        tk.Label(self, text="Danh sách nhân viên", bg="white", font=("Arial", 11, "bold")).pack(anchor="w", padx=20)

        columns = ("MaNV", "HoTenNV", "Sdt", "Phai", "NgaySinh", "ChucVu", "DiaChi", "Luong", "TinhTrang")

        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=11)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(padx=10, pady=5, fill="both")

        # ============================== BUTTONS ======================================
        frame_btn = tk.Frame(self, bg="white")
        frame_btn.pack(pady=10)
        btn = dict(width=15, fg="white", font=("Arial", 11, "bold"))
        tk.Button(frame_btn, text="Thêm", bg="#3498DB",
                  command=self.add_nv, **btn).grid(row=0, column=0, padx=5)
        tk.Button(frame_btn, text="Lưu", bg="#27AE60",
                  command=self.save_edit, **btn).grid(row=0, column=1, padx=5)
        tk.Button(frame_btn, text="Sửa", bg="#E74C3C",
                  command=self.load_selected_to_edit, **btn).grid(row=0, column=2, padx=5)
        tk.Button(frame_btn, text="Hủy", bg="#E67E22",
                  command=self.clear_input, **btn).grid(row=0, column=3, padx=5)
        tk.Button(frame_btn, text="Xóa", bg="#800080",
                  command=self.delete_nv, **btn).grid(row=0, column=4, padx=5)

    # ========================================================================================
    #                                ENTRY / COMBO TẠO TỰ ĐỘNG
    # ========================================================================================
    def _make_entry(self, parent, label, row, col):
        tk.Label(parent, text=label, bg="white").grid(row=row, column=col, sticky="w", pady=5)
        e = tk.Entry(parent)
        e.grid(row=row, column=col+1, sticky="we", padx=5)
        return e

    def _make_combo(self, parent, label, row, col, values):
        tk.Label(parent, text=label, bg="white").grid(row=row, column=col, sticky="w", pady=5)
        cb = ttk.Combobox(parent, values=values, state="readonly")
        cb.grid(row=row, column=col+1, sticky="we", padx=5)
        return cb

    # ======================================================================================
    #                                        CHỨC NĂNG
    # ======================================================================================
    def get_values(self):
        return [
            self.entry_manv.get(),
            self.format_name(self.entry_hotennv.get()),
            self.entry_sdt.get(),
            self.var_phai.get(),
            self.entry_ngaysinh.get(),
            self.cbb_chucvu.get(),
            self.format_name(self.entry_diachi.get()),  # <== viết hoa địa chỉ
            self.entry_luong.get(),
            self.cbb_tinhtrang.get(),]

    # =================================== LOAD TABLE =============================================
    def load_nv(self):
        self.tree.delete(*self.tree.get_children())
        for r in load_table("nhanvien"):
            r = list(r)

            # Format lương để HIỂN THỊ
            try:
                r[7] = self.format_salary_display(r[7])
            except:
                pass

            self.tree.insert("", "end", values=r)

    # ====================================== ADD ============================================
    def add_nv(self):
        values = self.get_values()
        manv, hoten, sdt, phai, ngaysinh, chucvu, diachi, luong, tinhtrang = values

        if "" in values:
            return messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ thông tin!")
        if not self.valid_phone(sdt):
            return messagebox.showerror("Lỗi", "Số điện thoại phải đúng 10 số!")
        if not self.valid_date(ngaysinh):
            return messagebox.showerror("Lỗi", "Ngày phải dạng YYYY-MM-DD!")
        if not self.valid_salary(luong):
            return messagebox.showerror("Lỗi", "Lương phải là số hợp lệ!")

        # CHUYỂN LƯƠNG VỀ SỐ INT
        luong_num = int(luong.replace(".", "").replace(",", ""))
        values[7] = luong_num

        fields = ["MaNV", "HoTenNV", "Sdt", "Phai", "NgaySinh",
                "ChucVu", "DiaChi", "Luong", "TinhTrang"]
        add_record("nhanvien", fields, values)
        messagebox.showinfo("OK", "Thêm nhân viên thành công!")
        self.load_nv()
        self.clear_input()

    # ==================================== DELETE ==============================================
    def delete_nv(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Thông báo", "Chọn nhân viên để xóa!")

        manv = self.tree.item(sel)["values"][0]
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa nhân viên {manv}?"):
            return

        delete_record("nhanvien", "MaNV", manv)
        messagebox.showinfo("OK", "Đã xóa!")
        self.load_nv()
        self.clear_input()

    # ========================================== LOAD TO FORM ==========================================
    def load_selected_to_edit(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Thông báo", "Chọn nhân viên để sửa!")

        data = self.tree.item(sel)["values"]

        self.entry_manv.delete(0, tk.END)
        self.entry_manv.insert(0, data[0])

        self.entry_hotennv.delete(0, tk.END)
        self.entry_hotennv.insert(0, data[1])

        self.entry_sdt.delete(0, tk.END)
        self.entry_sdt.insert(0, data[2])

        self.var_phai.set(data[3])

        self.entry_ngaysinh.delete(0, tk.END)
        self.entry_ngaysinh.insert(0, data[4])

        self.cbb_chucvu.set(data[5])

        self.entry_diachi.delete(0, tk.END)
        self.entry_diachi.insert(0, data[6])

        self.entry_luong.delete(0, tk.END)
        self.entry_luong.insert(0, data[7])

        self.cbb_tinhtrang.set(data[8])

    # ================================= SAVE EDIT =======================================
    def save_edit(self):
        manv = self.entry_manv.get()
        values = self.get_values()
        (_, hoten, sdt, phai, ngaysinh, chucvu, diachi, luong, tinhtrang) = values

        if "" in values:
            return messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ thông tin!")
        if not self.valid_phone(sdt):
            return messagebox.showerror("Lỗi", "SĐT phải đúng 10 số!")
        if not self.valid_date(ngaysinh):
            return messagebox.showerror("Lỗi", "Ngày sinh phải dạng YYYY-MM-DD!")
        if not self.valid_salary(luong):
            return messagebox.showerror("Lỗi", "Lương phải là số hợp lệ!")

        # CHUYỂN LƯƠNG VỀ INT
        luong_num = int(luong.replace(".", "").replace(",", ""))
        fields = ["HoTenNV", "Sdt", "Phai", "NgaySinh",
                "ChucVu", "DiaChi", "Luong", "TinhTrang"]
        new_values = [hoten, sdt, phai, ngaysinh, chucvu, diachi, luong_num, tinhtrang]
        update_record("nhanvien", "MaNV", manv, fields, new_values)

        messagebox.showinfo("OK", "Cập nhật thành công!")
        self.load_nv()
        self.clear_input()

    # ================================ SEARCH ===========================================
    def search_nv(self):
        keyword = self.entry_search.get().strip()
        field = self.cbb_search_type.get()
        if field == " ":
            return self.load_nv()
        
        rows = search_record("nhanvien", field, keyword)
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            # Format salary display
            r = list(r)
            try:
                r[7] = self.format_salary_display(r[7])
            except:
                pass
            self.tree.insert("", "end", values=r)

    # =================================== CLEAR ======================================
    def clear_input(self):
        self.entry_manv.delete(0, tk.END)
        self.entry_hotennv.delete(0, tk.END)
        self.entry_sdt.delete(0, tk.END)
        self.entry_ngaysinh.delete(0, tk.END)
        self.entry_diachi.delete(0, tk.END)
        self.entry_luong.delete(0, tk.END)
        self.var_phai.set("Nam")
        self.cbb_chucvu.set("")
        self.cbb_tinhtrang.set("")
