import time
import sys

sys.path.append(".")
from scservo_sdk import *

# 1. CẤU HÌNH THÔNG SỐ KẾT NỐI
DEVICENAME = 'COM18'        # Sửa thành cổng COM thực tế của bạn
BAUDRATE   = 1000000

# ID của 3 động cơ (đảm bảo cả 3 đã được đặt ID khác nhau)
SCS_ID_1 = 7
SCS_ID_2 = 8
SCS_ID_3 = 9

# 2. KHỞI TẠO VÀ MỞ CỔNG COM
portHandler = PortHandler(DEVICENAME)
packetHandler = sms_sts(portHandler)

if not portHandler.openPort() or not portHandler.setBaudRate(BAUDRATE):
    print("Lỗi mở cổng COM hoặc cài đặt Baudrate!")
    sys.exit()

# 3. KHỞI TẠO ĐỐI TƯỢNG SYNC WRITE (Đã sửa lỗi truyền thừa tham số ở đây)
groupSyncWrite = GroupSyncWrite(portHandler, packetHandler, SMS_STS_GOAL_POSITION_L)

# 4. KHAI BÁO GÓC MUỐN QUAY CHO TỪNG SERVO (Tính bằng Độ)
angles = {
    SCS_ID_1: 0,    # Servo 1 -> 0 độ
    SCS_ID_2: 90,   # Servo 2 -> 90 độ
    SCS_ID_3: 180   # Servo 3 -> 180 độ
}

speed = 1500  # Tốc độ quay (0 - 4095)
acc = 50      # Gia tốc (0 - 254)

print("Đang đóng gói và gửi lệnh đồng bộ cho 3 servo...")

# 5. ĐÓNG GÓI DỮ LIỆU
for servo_id, angle in angles.items():
    # Tính giá trị pulse (0 - 4095)
    position = int((angle / 360.0) * 4095)
    
    # Đóng gói dữ liệu điều khiển:
    # [Position_L, Position_H, Time_L, Time_H, Speed_L, Speed_H, Acc]
    param_goal_position = [
        SCS_LOBYTE(position),
        SCS_HIBYTE(position),
        0, 0,
        SCS_LOBYTE(speed),
        SCS_HIBYTE(speed),
        acc
    ]
    
    # Thêm tham số của từng servo vào danh sách SyncWrite
    groupSyncWrite.addParam(servo_id, param_goal_position)

# 6. GỬI 1 GÓI TIN DUY NHẤT ĐỂ ĐIỀU KHIỂN ĐỒNG THỜI
scs_comm_result = groupSyncWrite.txPacket()
if scs_comm_result != COMM_SUCCESS:
    print(f"Lỗi gửi SyncWrite: {packetHandler.getTxRxResult(scs_comm_result)}")
else:
    print("Gửi lệnh thành công! 3 Servo đang quay cùng lúc...")

# Xóa danh sách tham số sau khi gửi
groupSyncWrite.clearParam()

# 7. CHỜ 2 GIÂY ĐỂ HOÀN THÀNH CHUYỂN ĐỘNG VÀ ĐÓNG CỔNG
time.sleep(2)
portHandler.closePort()
print("Đã hoàn tất!")