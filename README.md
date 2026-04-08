TÀI LIỆU THIẾT KẾ ỨNG DỤNG BÁN HÀNG (MOBILE APP)
I. TỔNG QUAN ỨNG DỤNG
Ứng dụng là hệ thống bán hàng trên nền tảng Mobile App với các chức năng chính:
- Cho phép người dùng mua sản phẩm (cà phê, đồ ăn, ...)
- Quản lý giỏ hàng và đơn hàng
- Chat hỗ trợ với admin
- Admin quản lý sản phẩm, kho và báo cáo
II. ĐỐI TƯỢNG SỬ DỤNG
1. Khách hàng (User)
- Đăng ký / đăng nhập
- Xem sản phẩm
- Thêm vào giỏ hàng
- Đặt hàng
- Theo dõi đơn hàng
- Chat với admin
2. Quản trị viên (Admin)
- Quản lý user
- Quản lý sản phẩm & danh mục
- Quản lý kho
- Quản lý đơn hàng
- Xem báo cáo
III. MÔ TẢ CHỨC NĂNG HỆ THỐNG
1. Auth (Xác thực): Đăng ký, đăng nhập, refresh token (JWT)
2. Users: Xem danh sách, chi tiết, cập nhật, xóa (Admin)
3. Categories: Tạo / sửa / xóa / xem danh sách
4. Products: Xem danh sách, chi tiết, thêm / xóa
5. Product Variants: Thêm biến thể (size, topping), cập nhật / xóa
6. Inventory: Nhập hàng, xuất hàng, xem tồn kho
7. Cart: Thêm sản phẩm, xem giỏ, cập nhật, xóa, checkout
8. Order Items: Lưu chi tiết sản phẩm trong đơn
9. Orders: Tạo, xem, hủy, cập nhật trạng thái
11. Reports: Thống kê doanh thu, sản phẩm bán chạy
IV. LUỒNG HOẠT ĐỘNG
User Flow
Login → Xem sản phẩm → Thêm vào giỏ → Checkout → Theo dõi đơn → Chat nếu cần
Admin Flow
Quản lý sản phẩm → Quản lý đơn → Chat hỗ trợ → Xem báo cáo.

