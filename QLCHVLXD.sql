-- Xóa database nếu đã tồn tại
DROP DATABASE IF EXISTS qlch_vlxd;

-- Tạo database mới với chuẩn UTF-8 đầy đủ
CREATE DATABASE qlch_vlxd
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Sử dụng database
USE qlch_vlxd;

-----------------------------------------------------
-- BẢNG NHÂN VIÊN
-----------------------------------------------------
CREATE TABLE nhanvien (
    MaNV VARCHAR(20) PRIMARY KEY,         -- Mã nhân viên
    HoTenNV VARCHAR(100) NOT NULL,        -- Họ tên nhân viên
    Sdt VARCHAR(15) NOT NULL,             -- Số điện thoại
    Phai VARCHAR(5) NOT NULL,             -- Giới tính
    NgaySinh DATE NOT NULL,               -- Ngày sinh
    ChucVu VARCHAR(50) NOT NULL,          -- Chức vụ
    DiaChi VARCHAR(200),                  -- Địa chỉ
    Luong INT NOT NULL,                   -- Lương cơ bản
    TinhTrang VARCHAR(20) NOT NULL        -- Tình trạng làm việc
);
-----------------------------------------------------
-- BẢNG KHÁCH HÀNG
-----------------------------------------------------
CREATE TABLE khachhang (
    MaKH VARCHAR(20) PRIMARY KEY,         -- Mã khách hàng
    HoTen VARCHAR(100) NOT NULL,          -- Tên khách hàng
    SDT VARCHAR(15) NOT NULL,             -- Số điện thoại
    DiaChi VARCHAR(255) NOT NULL,         -- Địa chỉ
    CCCD VARCHAR(20) NOT NULL,            -- Căn cước công dân
    GhiChu VARCHAR(255)                   -- Ghi chú thêm
);
-----------------------------------------------------
-- BẢNG NHÀ CUNG CẤP
-----------------------------------------------------
CREATE TABLE nhacungcap (
    MaNCC VARCHAR(20) PRIMARY KEY,        -- Mã nhà cung cấp
    TenNCC VARCHAR(100) NOT NULL,         -- Tên nhà cung cấp
    SDT VARCHAR(15) NOT NULL,             -- Số điện thoại
    DiaChi VARCHAR(200),                  -- Địa chỉ
    GhiChu VARCHAR(255)                   -- Ghi chú thêm
);
-----------------------------------------------------
-- BẢNG VẬT LIỆU
-----------------------------------------------------
CREATE TABLE vatlieu (
    MaVL VARCHAR(20) PRIMARY KEY,         -- Mã vật liệu
    TenVL VARCHAR(100) NOT NULL,          -- Tên vật liệu
    DonViTinh VARCHAR(50),                -- Đơn vị tính
    GiaNhap DECIMAL(15,2) NOT NULL,       -- Giá nhập
    GiaBan DECIMAL(15,2) NOT NULL,        -- Giá bán
    TonKho INT DEFAULT 0,                 -- Số lượng tồn kho
    MaNCC VARCHAR(20),                    -- Mã nhà cung cấp

    FOREIGN KEY (MaNCC) REFERENCES nhacungcap(MaNCC)
        ON UPDATE CASCADE                 -- Nếu mã NCC đổi → cập nhật theo
        ON DELETE SET NULL                -- Nếu NCC bị xóa → để NULL
);
-----------------------------------------------------
-- BẢNG HÓA ĐƠN BÁN HÀNG
-----------------------------------------------------
CREATE TABLE hoadon (
    MaHD VARCHAR(20) PRIMARY KEY,         -- Mã hóa đơn
    MaKH VARCHAR(20),                     -- Mã khách hàng
    MaNV VARCHAR(20),                     -- Mã nhân viên bán
    NgayBan DATE,                         -- Ngày bán hàng
    HinhThucTT VARCHAR(50),               -- Hình thức thanh toán
    GhiChu VARCHAR(255),                  -- Ghi chú
    TongTien DECIMAL(15,2) DEFAULT 0,     -- Tổng tiền hóa đơn

    FOREIGN KEY (MaKH) REFERENCES khachhang(MaKH),
    FOREIGN KEY (MaNV) REFERENCES nhanvien(MaNV)
);
-----------------------------------------------------
-- BẢNG CHI TIẾT HÓA ĐƠN
-----------------------------------------------------
CREATE TABLE ct_hoadon (
    MaHD VARCHAR(20) NOT NULL,            -- Mã hóa đơn
    MaVL VARCHAR(20) NOT NULL,            -- Mã vật liệu
    SoLuong INT NOT NULL,                 -- Số lượng bán ra
    DonGia DECIMAL(15,2) NOT NULL,        -- Đơn giá bán
    ThanhTien DECIMAL(15,2) AS (SoLuong * DonGia) STORED, -- Tự tính

    PRIMARY KEY (MaHD, MaVL),             -- 1 vật liệu chỉ xuất hiện 1 lần trong hóa đơn
    FOREIGN KEY (MaHD) REFERENCES hoadon(MaHD),
    FOREIGN KEY (MaVL) REFERENCES vatlieu(MaVL)
);
-----------------------------------------------------
-- BẢNG PHIẾU NHẬP KHO
-----------------------------------------------------
CREATE TABLE phieunhap (
    MaPN VARCHAR(20) PRIMARY KEY,         -- Mã phiếu nhập
    NgayNhap DATE NOT NULL,               -- Ngày nhập kho
    MaNCC VARCHAR(20) NOT NULL,           -- Mã nhà cung cấp
    MaNV VARCHAR(20) NOT NULL,            -- Mã nhân viên nhập kho
    GhiChu VARCHAR(255),                  -- Ghi chú
    TongTien DECIMAL(18,2) DEFAULT 0,     -- Tổng tiền phiếu nhập

    FOREIGN KEY (MaNCC) REFERENCES nhacungcap(MaNCC),
    FOREIGN KEY (MaNV) REFERENCES nhanvien(MaNV)
);
-----------------------------------------------------
-- BẢNG CHI TIẾT PHIẾU NHẬP
-----------------------------------------------------
CREATE TABLE ct_phieunhap (
    MaPN VARCHAR(20) NOT NULL,            -- Mã phiếu nhập
    MaVL VARCHAR(20) NOT NULL,            -- Mã vật liệu
    SoLuongNhap INT NOT NULL,             -- Số lượng nhập
    DonGiaNhap DECIMAL(15,2) NOT NULL,    -- Giá nhập
    ThanhTien DECIMAL(15,2) AS (SoLuongNhap * DonGiaNhap) STORED, -- Tự tính

    PRIMARY KEY (MaPN, MaVL),
    FOREIGN KEY (MaPN) REFERENCES phieunhap(MaPN),
    FOREIGN KEY (MaVL) REFERENCES vatlieu(MaVL)
);
