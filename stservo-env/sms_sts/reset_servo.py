import sys
import time
sys.path.append("..")
from scservo_sdk import *
 
DEVICENAME = 'COM18'  # Kiểm tra đúng cổng COM của bạn
BAUDRATE = 1000000
STS_ID = 5
 
# Địa chỉ thanh ghi
ADDR_TORQUE_ENABLE  = 40
ADDR_LOCK           = 55
ADDR_GOAL_POSITION  = 42
ADDR_MIN_ANGLE      = 9
ADDR_MAX_ANGLE      = 11
ADDR_PRESENT_POS    = 56
ADDR_PRESENT_VOLTAGE = 62
ADDR_STATUS         = 65   # <-- mã lỗi thật sự, không phải 63
 
portHandler = PortHandler(DEVICENAME)
packetHandler = sms_sts(portHandler)
 
if not (portHandler.openPort() and portHandler.setBaudRate(BAUDRATE)):
    print("Không mở được cổng COM hoặc set baudrate thất bại!")
    sys.exit(1)
 
print(f"--- Khôi phục Servo ID {STS_ID} ---")
 
# 0. Kiểm tra trạng thái lỗi TRƯỚC khi làm gì cả
status_before, result, error = packetHandler.read1ByteTxRx(STS_ID, ADDR_STATUS)
if result == COMM_SUCCESS:
    print(f"Status trước khi xử lý: {status_before} (Binary: {bin(status_before)})")
else:
    print("Không đọc được status ban đầu, vẫn tiếp tục...")
    status_before = None
 
# 1. Tắt Torque để servo ngừng giữ lực (an toàn khi thao tác EEPROM)
packetHandler.write1ByteTxRx(STS_ID, ADDR_TORQUE_ENABLE, 0)
time.sleep(0.05)
 
# 2. Mở khóa EEPROM để cho phép ghi cấu hình
packetHandler.write1ByteTxRx(STS_ID, ADDR_LOCK, 0)
time.sleep(0.05)
 
# 3. Đọc vị trí thực tế hiện tại và đặt Goal_Position trùng vào đó
#    (tránh servo giật mạnh khi bật lại torque)
pres_pos, result, error = packetHandler.read2ByteTxRx(STS_ID, ADDR_PRESENT_POS)
if result == COMM_SUCCESS:
    print(f"Vị trí thực tế đọc được: {pres_pos}")
    packetHandler.write2ByteTxRx(STS_ID, ADDR_GOAL_POSITION, pres_pos)
else:
    print("Không đọc được vị trí hiện tại!")
 
# 4. Đặt lại dải góc tối đa (0 -> 4095) phòng khi bị giới hạn sai lệch
packetHandler.write2ByteTxRx(STS_ID, ADDR_MIN_ANGLE, 0)
packetHandler.write2ByteTxRx(STS_ID, ADDR_MAX_ANGLE, 4095)
time.sleep(0.05)
 
# 5. Khóa lại EEPROM
packetHandler.write1ByteTxRx(STS_ID, ADDR_LOCK, 1)
time.sleep(0.05)
 
# 6. Bật lại Torque
packetHandler.write1ByteTxRx(STS_ID, ADDR_TORQUE_ENABLE, 1)
time.sleep(0.1)
 
# 7. Kiểm tra lại status SAU khi xử lý để biết lỗi còn hay hết
status_after, result, error = packetHandler.read1ByteTxRx(STS_ID, ADDR_STATUS)
voltage, vresult, verror = packetHandler.read1ByteTxRx(STS_ID, ADDR_PRESENT_VOLTAGE)
 
print("\n--- Kết quả ---")
if result == COMM_SUCCESS:
    print(f"Status sau khi xử lý  : {status_after} (Binary: {bin(status_after)})")
    if status_after == 0:
        print("-> Servo đã sạch lỗi, hoạt động bình thường.")
    else:
        print("-> Servo VẪN còn báo lỗi. Đây là lỗi thật sự do điều kiện phần cứng")
        print("   (điện áp/nhiệt độ/quá tải), không phải do phần mềm chưa xóa cờ.")
        if vresult == COMM_SUCCESS:
            print(f"   Điện áp hiện tại đang là {voltage / 10.0} V — kiểm tra xem có")
            print("   vượt mức Max_Voltage_Limit của servo hay không (chạy check_status.py).")
else:
    print("Không đọc lại được status sau khi xử lý.")
 
portHandler.closePort()
 