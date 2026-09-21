#!/usr/bin/env python
import os
import sys

sys.path.append("..")
from scservo_sdk import *

# 1. Cấu hình cổng COM và Baudrate
DEVICENAME = 'COM19'      # Sửa lại đúng cổng COM trên máy bạn (ví dụ: 'COM3', 'COM4')
BAUDRATE   = 1000000      # Tốc độ truyền mặc định (Thường là 1000000 hoặc 57600)

portHandler   = PortHandler(DEVICENAME)
packetHandler = sms_sts(portHandler)

if not portHandler.openPort():
    print(f"Lỗi: Không thể mở cổng {DEVICENAME}")
    quit()

if not portHandler.setBaudRate(BAUDRATE):
    print("Lỗi: Không thể cài đặt Baudrate")
    portHandler.closePort()
    quit()

print(f"--- Đang quét ID Servo trên cổng {DEVICENAME} (Baudrate: {BAUDRATE}) ---")
found_servos = []

# 2. Vòng lặp quét từ ID 1 đến 253
for scs_id in range(1, 254):
    scs_model_number, scs_comm_result, scs_error = packetHandler.ping(scs_id)
    
    if scs_comm_result == COMM_SUCCESS:
        print(f"[THÀNH CÔNG] Tìm thấy Servo tại ID: {scs_id} (Model: {scs_model_number})")
        found_servos.append(scs_id)

print("--------------------------------------------------")
if found_servos:
    print(f"Tổng cộng tìm thấy {len(found_servos)} Servo có ID: {found_servos}")
else:
    print("Không tìm thấy Servo nào!")
    print("Gợi ý kiểm tra:")
    print(" 1. Đã cấp nguồn ngoài (6V - 12V) cho Servo chưa?")
    print(" 2. Baudrate có đúng không? (Thử đổi BAUDRATE thành 57600 hoặc 115200)")

portHandler.closePort()