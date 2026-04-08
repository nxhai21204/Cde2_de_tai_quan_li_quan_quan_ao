import logging
# Theo dõi hoạt động hệ thống, Chuẩn hóa log cho toàn bộ ứng dụng, dễ debug
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )