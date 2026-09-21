import time
import sys

sys.path.append(".")
from scservo_sdk import *

# 1. CẤU HÌNH THÔNG SỐ KẾT NỐI
DEVICENAME = 'COM19'        # Sửa thành cổng COM thực tế của bạn
BAUDRATE   = 1000000

# ID của 3 động cơ bánh Omni
SCS_ID_1 = 7
SCS_ID_2 = 8
SCS_ID_3 = 9

# 2. KHỞI TẠO VÀ MỞ CỔNG COM
portHandler = PortHandler(DEVICENAME)
packetHandler = sms_sts(portHandler)

if not portHandler.openPort() or not portHandler.setBaudRate(BAUDRATE):
    print("Lỗi mở cổng COM hoặc cài đặt Baudrate!")
    sys.exit()

# 3. GÓC ĐỘ CHO XE ĐI THẲNG
target_angles = {
    SCS_ID_1: 1800, 
    SCS_ID_2: -1800, 
    SCS_ID_3: 1800
}

speed = 1500
acc = 50 

print("Đang gửi lệnh điều khiển 3 bánh Omni đi thẳng...")

# 4. GỬI LỆNH ĐIỀU KHIỂN TỪNG SERVO
for servo_id, angle in target_angles.items():
    position = int((angle / 360.0) * 4095)
    if position < 0:
        position = 4095 + position # Xử lý vị trí nếu góc âm

    # Sử dụng hàm WritePosEx chuẩn của Feetech SDK cho dòng SMS/STS
    # Cú pháp: WritePosEx(ID, Position, Speed, Acceleration)
    comm_result, error = packetHandler.WritePosEx(servo_id, position, speed, acc)
    
    if comm_result != COMM_SUCCESS:
        print(f"Lỗi gửi lệnh cho Servo {servo_id}: {packetHandler.getTxRxResult(comm_result)}")
    else:
        print(f"Servo {servo_id} nhận lệnh thành công.")

# 5. CHỜ VÀ ĐÓNG CỔNG
time.sleep(3)
portHandler.closePort()
print("Đã hoàn tất!")