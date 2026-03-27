📌 I. TỔNG QUAN ỨNG DỤNG

Ứng dụng là hệ thống bán hàng (Mobile App) cho phép:

Người dùng mua sản phẩm (cà phê, đồ ăn…)
Quản lý giỏ hàng, đơn hàng
Chat hỗ trợ với admin
Admin quản lý sản phẩm, kho, báo cáo
📌 II. ĐỐI TƯỢNG SỬ DỤNG
👤 1. Khách hàng (User)
Đăng ký / đăng nhập
Xem sản phẩm
Thêm vào giỏ hàng
Đặt hàng
Theo dõi đơn hàng
Chat với admin
👨‍💼 2. Quản trị viên (Admin)
Quản lý user
Quản lý sản phẩm & danh mục
Quản lý kho
Quản lý đơn hàng
Chat với khách hàng
Xem báo cáo
📌 III. MÔ TẢ CHỨC NĂNG HỆ THỐNG
🔐 1. Auth (Xác thực)
Đăng ký
Đăng nhập
Refresh token

👉 Bảo mật hệ thống bằng JWT

👤 2. Users
Xem danh sách user
Xem chi tiết
Cập nhật
Xóa

👉 Chỉ admin

🗂️ 3. Categories
Tạo / sửa / xóa
Xem danh sách

👉 Phân loại sản phẩm

🛍️ 4. Products
Xem danh sách
Xem chi tiết
Thêm / xóa
🧩 5. Product Variants
Thêm biến thể (size, topping)
Cập nhật / xóa
📦 6. Inventory (Kho)
Nhập hàng
Xuất hàng
Xem tồn kho
🛒 7. Cart (Giỏ hàng)
Thêm sản phẩm
Xem giỏ
Cập nhật số lượng
Xóa sản phẩm
Checkout
📋 8. Order Items
Lưu chi tiết từng sản phẩm trong đơn
CRUD order item
🧾 9. Orders
Tạo đơn hàng
Xem danh sách
Xem chi tiết
Hủy đơn
Cập nhật trạng thái
💬 10. Chat
Gửi / nhận tin nhắn
Xem lịch sử chat
Admin xem danh sách hội thoại
Hiển thị user online
📊 11. Reports
Thống kê doanh thu
Sản phẩm bán chạy
📌 IV. LUỒNG HOẠT ĐỘNG
👤 User
Login
Xem sản phẩm
Thêm vào giỏ
Checkout
Theo dõi đơn
Chat nếu cần
👨‍💼 Admin
Quản lý sản phẩm
Quản lý đơn
Chat hỗ trợ
Xem báo cáo
II.Vẽ demo
