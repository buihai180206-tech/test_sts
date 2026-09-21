import sys
sys.path.append("..")
from scservo_sdk import *
 
DEVICENAME = 'COM18'   # Sửa lại đúng cổng COM của bạn
BAUDRATE = 1000000
STS_ID = 5
 
# Địa chỉ thanh ghi RAM
ADDR_PRESENT_VOLTAGE     = 62
ADDR_PRESENT_TEMPERATURE = 63
ADDR_STATUS               = 65   # <-- mã lỗi thật sự nằm ở đây
ADDR_MOVING               = 66
ADDR_PRESENT_LOAD_L       = 60
 
# Địa chỉ thanh ghi EEPROM (giới hạn cấu hình, để đối chiếu khi chẩn đoán)
ADDR_MAX_TEMP_LIMIT   = 13
ADDR_MAX_VOLTAGE_LIMIT = 14
ADDR_MIN_VOLTAGE_LIMIT = 15
 
portHandler = PortHandler(DEVICENAME)
packetHandler = sms_sts(portHandler)
 
if not (portHandler.openPort() and portHandler.setBaudRate(BAUDRATE)):
    print("Không mở được cổng COM hoặc set baudrate thất bại!")
    sys.exit(1)
 
print(f"--- Chẩn đoán Servo ID {STS_ID} ---")
 
# 1. Điện áp hiện tại
voltage, result, error = packetHandler.read1ByteTxRx(STS_ID, ADDR_PRESENT_VOLTAGE)
if result == COMM_SUCCESS:
    print(f"Điện áp hiện tại      : {voltage / 10.0} V")
else:
    print("Không đọc được điện áp!")
 
# 2. Nhiệt độ hiện tại (đây mới là ý nghĩa thật của địa chỉ 63)
temp, result, error = packetHandler.read1ByteTxRx(STS_ID, ADDR_PRESENT_TEMPERATURE)
if result == COMM_SUCCESS:
    print(f"Nhiệt độ hiện tại     : {temp} °C")
else:
    print("Không đọc được nhiệt độ!")
 
# 3. Tải hiện tại
load, result, error = packetHandler.read2ByteTxRx(STS_ID, ADDR_PRESENT_LOAD_L)
if result == COMM_SUCCESS:
    print(f"Tải hiện tại (raw)    : {load}")
 
# 4. MÃ LỖI THẬT SỰ (Status / Hardware Error Status)
status, result, error = packetHandler.read1ByteTxRx(STS_ID, ADDR_STATUS)
if result == COMM_SUCCESS:
    print(f"Status/Error thật sự  : {status} (Binary: {bin(status)})")
    if status == 0:
        print("  -> Không có lỗi nào đang được servo báo.")
    else:
        print("  -> Servo đang báo lỗi thật sự (xem từng bit trong tài liệu SDK/nhà sản xuất).")
else:
    print("Không đọc được thanh ghi status!")
 
# 5. Đang di chuyển hay không
moving, result, error = packetHandler.read1ByteTxRx(STS_ID, ADDR_MOVING)
if result == COMM_SUCCESS:
    print(f"Đang di chuyển        : {'Có' if moving else 'Không'}")
 
# 6. Giới hạn cấu hình để đối chiếu (giúp phát hiện nguồn quá áp / quá nhiệt cấu hình)
max_temp, result, error = packetHandler.read1ByteTxRx(STS_ID, ADDR_MAX_TEMP_LIMIT)
max_v, result, error = packetHandler.read1ByteTxRx(STS_ID, ADDR_MAX_VOLTAGE_LIMIT)
min_v, result, error = packetHandler.read1ByteTxRx(STS_ID, ADDR_MIN_VOLTAGE_LIMIT)
print("\n--- Giới hạn cấu hình trong EEPROM ---")
print(f"Max_Temperature_Limit : {max_temp} °C")
print(f"Max_Voltage_Limit      : {max_v / 10.0 if isinstance(max_v, int) else max_v} V")
print(f"Min_Voltage_Limit      : {min_v / 10.0 if isinstance(min_v, int) else min_v} V")
 
if result == COMM_SUCCESS and voltage is not None:
    if 'max_v' in locals() and isinstance(max_v, int) and voltage > max_v:
        print("\n⚠️  CẢNH BÁO: điện áp thực tế đang VƯỢT max_voltage_limit cấu hình cho servo này!")
        print("    Đây rất có thể là nguyên nhân gốc gây lỗi, không phải phần mềm.")
 
portHandler.closePort()