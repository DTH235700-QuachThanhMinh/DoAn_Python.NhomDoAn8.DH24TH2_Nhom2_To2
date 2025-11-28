from importlib.resources import contents
import tkinter as tk
from tkinter import messagebox
from lienket import connect_db
import pandas as pd
from tkinter import filedialog
from forms.nhanvien_ui import NhanVienFrame
from forms.khachhang_ui import KhachHangFrame
from forms.nhacungcap_ui import NhaCungCapFrame
from forms.vatlieu_ui import VatLieuFrame
from forms.hoadon_ui import HoaDonFrame
from forms.cthoadon_ui import CTHoaDonFrame
from forms.phieunhap_ui import PhieuNhapFrame
from forms.ct_phieunhap_ui import CTPhieuNhapFrame


# ========================= TEST DB =========================
def test_connection():
    try:
        conn = connect_db()
        conn.close()
        print("KẾT NỐI MYSQL OK")
        return True
    except:
        print("KẾT NỐI MYSQL THẤT BẠI")
        return False

# =========================== CANH GIỮA ===========================
def center_window(win, w=1200, h=700):
    win.update_idletasks()
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

# ====================== MENU CHÍNH ========================
def create_menu(root, username, role):

    main = tk.Frame(root, bg="#F0F2F5")
    main.pack(fill="both", expand=True)

    menu = tk.Frame(main, bg="#003A75", width=250)
    menu.pack(side="left", fill="y")

    content = tk.Frame(main, bg="white")
    content.pack(side="left", fill="both", expand=True)

    def show_frame(form_class):
        for w in content.winfo_children():
            w.destroy()
        frame = form_class(content)
        frame.pack(fill="both", expand=True)

    # ===== TITLE =====
    tk.Label(menu, text="MENU CHÍNH", bg="#003A75",
             fg="white", font=("Arial", 18, "bold")).pack(pady=30)

    # ===== STYLE =====
    btn_style = dict(bg="white", fg="#003A75",
                     font=("Arial", 12, "bold"),
                     width=22, height=2, relief="flat")

    # ===== NHÂN VIÊN =====
    def open_nv():
        if role != "Quản lý":
            return messagebox.showwarning("Cấm truy cập", "Chỉ Quản lý được vào mục này")
        show_frame(NhanVienFrame)
    def open_ncc():
        if role != "Quản lý":
            return messagebox.showwarning("Cấm truy cập", "Chỉ Quản lý được vào mục này")
        show_frame(NhaCungCapFrame)

    tk.Button(menu, text="1. Quản lý nhân viên",
              command=open_nv, **btn_style).pack(pady=5)
    
    tk.Button(menu, text="2. Quản lý khách hàng",
              command=lambda: show_frame(KhachHangFrame), **btn_style).pack(pady=5)
    
    tk.Button(menu, text="3. Quản lý nhà cung cấp",
              command=open_ncc, **btn_style).pack(pady=5)
    
    tk.Button(menu, text="4. Quản lý vật liệu",
              command=lambda: show_frame(VatLieuFrame), **btn_style).pack(pady=5)
    
    tk.Button(menu, text="5. Quản lý hóa đơn",
              command=lambda: show_frame(HoaDonFrame), **btn_style).pack(pady=5)
    
    tk.Button(menu, text="6. Quản lý chi tiết hóa đơn",
              command=lambda: show_frame(CTHoaDonFrame), **btn_style).pack(pady=5)
    
    tk.Button(menu, text="7. Quản lý phiếu nhập",
              command=lambda: show_frame(PhieuNhapFrame), **btn_style).pack(pady=5)
    
    tk.Button(menu, text="8. Quản lý chi tiết phiếu nhập",
              command=lambda: show_frame(CTPhieuNhapFrame), **btn_style).pack(pady=5)

    # ===== TRANG CHÀO =====
    tk.Label(content,
             text=f"Hệ thống quản lý cửa hàng VLXD", fg="#E01414",
             bg="white", font=("Arial", 24, "bold")
             ).place(relx=0.5, rely=0.40, anchor="center")

    tk.Label(content,
             text=f"Xin chào: {username} ({role})", fg="#003A75",
             bg="white", font=("Arial", 24, "bold")
             ).place(relx=0.5, rely=0.50, anchor="center")

    tk.Label(content,
             text="Vui lòng chọn chức năng bên trái",
             bg="white", font=("Arial", 16)
             ).place(relx=0.5, rely=0.55, anchor="center")

    # ==================== NÚT DƯỚI CÙNG =====================
    bottom_frame = tk.Frame(menu, bg="#003A75")
    bottom_frame.pack(side="bottom", pady=25)

    btn_small_style = dict(
    font=("Arial", 10, "bold"),
    width=12,
    height=1,
    relief="raised"
)


# ---- Quay lại ----
    def go_back():
        for w in root.winfo_children():
            w.destroy()
        login_screen(root)

    tk.Button(bottom_frame,
          text="Quay lại",
          bg="#28A745", fg="white",
          command=go_back,
          **btn_small_style).grid(row=0, column=0, padx=5)

    def confirm_exit():
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn thoát?"):
            root.quit()

    tk.Button(bottom_frame,
          text="Thoát",
          bg="#C9302C", fg="white",
          command=confirm_exit,
          **btn_small_style).grid(row=0, column=1, padx=5)

# ====================== LOGIN SCREEN ========================
def login_screen(root):

    frame = tk.Frame(root, bg="#F0F2F5")
    frame.pack(fill="both", expand=True)

    box = tk.Frame(frame, bg="white", bd=2, relief="groove")
    box.place(relx=0.5, rely=0.5, anchor="center")

    box.config(width=420, height=380)
    box.pack_propagate(False)

    tk.Label(box, text="ĐĂNG NHẬP", bg="white",
             font=("Arial", 22, "bold"), fg="#003A75").pack(pady=20)

    accounts = {
        "admin": ("123456", "Quản lý"),
        "nv1": ("abc123", "Nhân viên"),
        "nv2": ("xyz456", "Nhân viên")
    }

    # USERNAME
    tk.Label(box, text="Tên đăng nhập:", bg="white").pack()
    entry_user = tk.Entry(box, width=30)
    entry_user.pack(pady=5)

    # PASSWORD
    tk.Label(box, text="Mật khẩu:", bg="white").pack()
    entry_pass = tk.Entry(box, show="*", width=30)
    entry_pass.pack(pady=5)

    # ROLE
    tk.Label(box, text="Chức vụ:", bg="white").pack()
    role_var = tk.StringVar(value="Nhân viên")

    tk.Radiobutton(box, text="Quản lý", variable=role_var,
                   value="Quản lý", bg="white").pack()
    tk.Radiobutton(box, text="Nhân viên", variable=role_var,
                   value="Nhân viên", bg="white").pack()

    # ========= LOGIN ===========
    def do_login():
        user = entry_user.get()
        pw = entry_pass.get()
        role = role_var.get()

        if user in accounts:
            correct_pw, correct_role = accounts[user]

            if pw != correct_pw:
                return messagebox.showerror("Lỗi", "Sai mật khẩu!", "Vui lòng nhập lại")

            if role != correct_role:
                return messagebox.showerror("Lỗi", "Sai chức vụ!")

            messagebox.showinfo("Thành công", "Đăng nhập thành công!")

            frame.destroy()
            create_menu(root, user, role)

        else:
            messagebox.showerror("Lỗi", "Không tồn tại tài khoản")

    tk.Button(box, text="Đăng nhập", bg="#0056D6",
              fg="white", width=20, font=("Arial", 12),
              command=do_login).pack(pady=20)


# =========================== MAIN ==========================
def main():

    if not test_connection():
        return messagebox.showerror("Lỗi DB", "Không thể kết nối MySQL!")

    root = tk.Tk()
    root.title("Phần mềm quản lý cửa hàng VLXD")
    center_window(root, 1200, 700)

    login_screen(root)

    root.mainloop()


if __name__ == "__main__":
    main()

