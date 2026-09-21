import time
import sys

# Thêm đường dẫn để Import thư viện SDK của động cơ
sys.path.append(".")
from scservo_sdk import *

# 1. CẤU HÌNH THÔNG SỐ
DEVICENAME = 'COM18'        # Cổng COM nối với mạch URT (thay đúng cổng trên máy bạn)
BAUDRATE   = 1000000       # Tốc độ giao tiếp mặc định của STS3215 là 1Mbps
SCS_ID     = 1             # ID của động cơ (mặc định thường là 1)

# 2. KHỞI TẠO ĐỐI TƯỢNG GIAO TIẾP
portHandler = PortHandler(DEVICENAME)
packetHandler = sms_sts(portHandler)

# 3. MỞ CỔNG COM VÀ THIẾT LẬP TỐC ĐỘ BAUD
if not portHandler.openPort():
    print("Không thể mở cổng COM! Kiểm tra lại dây cáp hoặc tên cổng.")
    sys.exit()

if not portHandler.setBaudRate(BAUDRATE):
    print("Không thể thiết lập Baudrate!")
    sys.exit()

# 4. CHUYỂN ĐỔI GÓC TỪ ĐỘ SANG GIÁ TRỊ VỊ TRÍ (PULSES)
# Động cơ STS3215 quay từ 0 - 360 độ tương ứng giá trị từ 0 - 4095
target_angle = 180
target_position = int((target_angle / 360.0) * 4095)  # 90 độ sẽ tính ra khoảng 1023

# Các thông số chuyển động
speed = 1500    # Tốc độ quay (giá trị từ 0 đến 4095)
acc = 50        # Gia tốc (giá trị từ 0 đến 254 giúp chuyển động mượt hơn)

# 5. GỬI LỆNH ĐIỀU KHIỂN ĐỘNG CƠ
print(f"Đang quay động cơ ID {SCS_ID} đến góc {target_angle} độ (Vị trí pulse: {target_position})...")

scs_comm_result, scs_error = packetHandler.WritePosEx(
    SCS_ID, target_position, speed, acc
)

# Kiểm tra xem gửi lệnh thành công hay lỗi
if scs_comm_result != COMM_SUCCESS:
    print(f"Lỗi truyền thông tin: {packetHandler.getTxRxResult(scs_comm_result)}")
elif scs_error != 0:
    print(f"Lỗi từ Servo: {packetHandler.getRxPacketError(scs_error)}")
else:
    print("Gửi lệnh thành công!")

# Chờ 2 giây để động cơ kịp hoàn thành hành trình quay
time.sleep(2)

# 6. ĐÓNG CỔNG KẾT NỐI SAU KHU THỰC HIỆN XONG
portHandler.closePort()
print("Đã đóng kết nối thành công.")