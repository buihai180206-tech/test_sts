import sys
import time
import numpy as np

sys.path.append(".")
from scservo_sdk import *

# ==========================================
# 1. ĐỘNG HỌC NGƯỢC (INVERSE KINEMATICS)
# ==========================================
def inverse_kinematics(v_x, v_y, w_z):
    d = 0.13     # Khoảng cách từ tâm tới bánh (m)
    r = 0.0508   # Bán kính bánh xe (m)

    v = np.array([v_x, v_y, w_z])
    H = np.array([
        [1.0,  0.0, -d],
        [-0.5, -np.sqrt(3)/2, -d],
        [-0.5,  np.sqrt(3)/2, -d]
    ])
    return (1.0 / r) * np.dot(H, v) # u1, u2, u3 (rad/s)

# ==========================================
# 2. CẤU HÌNH PHẦN CỨNG
# ==========================================
DEVICENAME = "/dev/ttyACM0"
BAUDRATE   = 1000000
MOTOR_IDS  = [8, 7, 9]

portHandler = PortHandler(DEVICENAME)
packetHandler = sms_sts(portHandler)

if not portHandler.openPort() or not portHandler.setBaudRate(BAUDRATE):
    print("Lỗi mở cổng COM hoặc cài đặt Baudrate!")
    sys.exit()

# Cài đặt Mode = 1 (Wheel Mode - Quay liên tục) cho cả 3 Servo (Địa chỉ 33)
for servo_id in MOTOR_IDS:
    packetHandler.write1ByteTxRx(servo_id, 33, 1)

# ==========================================
# 3. THIẾT LẬP VẬN TỐC ĐI THẲNG
# ==========================================
v_x_target = 0  # m/s (Đi thẳng)
v_y_target = 0.2   # m/s
w_z_target = 0.0   # rad/s (Không xoay)

u_wheels = inverse_kinematics(v_x_target, v_y_target, w_z_target)
print(f"Tốc độ góc tính toán [u1, u2, u3] (rad/s): {u_wheels}")

# ==========================================
# 4. GỬI TỐC ĐỘ ĐẾN ĐỘNG CƠ
# ==========================================
T_RUN = 10.0 # Thời gian chạy (giây)
acc = 50

for i, servo_id in enumerate(MOTOR_IDS):
    u_rad_s = u_wheels[i]
    
    # Quy đổi rad/s sang đơn vị Speed của STS (1 step/s ≈ 0.001534 rad/s)
    speed_steps = int(u_rad_s * 4095 / (2 * np.pi))

    # ĐỔI TỪ WriteSpe THÀNH WriteSpec
    comm_result, error = packetHandler.WriteSpec(servo_id, speed_steps, acc)

    if comm_result != COMM_SUCCESS:
        print(f"Lỗi Servo {servo_id}: {packetHandler.getTxRxResult(comm_result)}")
    else:
        print(f"Servo {servo_id} -> Speed (steps/s): {speed_steps}")

print(f"Xe đang di chuyển trong {T_RUN} giây...")
time.sleep(T_RUN)


u_wheels_1 = inverse_kinematics(0.2, 0, 0)
for i, servo_id in enumerate(MOTOR_IDS):
    u_rad_s_1 = u_wheels_1[i]
    
    # Quy đổi rad/s sang đơn vị Speed của STS (1 step/s ≈ 0.001534 rad/s)
    speed_steps_1 = int(u_rad_s_1 * 4095 / (2 * np.pi))

    # ĐỔI TỪ WriteSpe THÀNH WriteSpec
    comm_result_1, error_1 = packetHandler.WriteSpec(servo_id, speed_steps_1, acc)

    if comm_result_1 != COMM_SUCCESS:
        print(f"Lỗi Servo {servo_id}: {packetHandler.getTxRxResult(comm_result_1)}")
    else:
        print(f"Servo {servo_id} -> Speed (steps/s): {speed_steps_1}")

print(f"Xe đang di chuyển trong {T_RUN} giây...")
time.sleep(2)

u_wheels_2 = inverse_kinematics(0, -0.2, 0)
for i, servo_id in enumerate(MOTOR_IDS):
    u_rad_s_2 = u_wheels_2[i]
    
    # Quy đổi rad/s sang đơn vị Speed của STS (1 step/s ≈ 0.001534 rad/s)
    speed_steps_2 = int(u_rad_s_2 * 4095 / (2 * np.pi))

    # ĐỔI TỪ WriteSpe THÀNH WriteSpec
    comm_result_2, error_2 = packetHandler.WriteSpec(servo_id, speed_steps_2, acc)

    if comm_result_2 != COMM_SUCCESS:
        print(f"Lỗi Servo {servo_id}: {packetHandler.getTxRxResult(comm_result_2)}")
    else:
        print(f"Servo {servo_id} -> Speed (steps/s): {speed_steps_2}")

print(f"Xe đang di chuyển trong {T_RUN} giây...")
time.sleep(10)

u_wheels_3 = inverse_kinematics(0, -0.2, 0)
for i, servo_id in enumerate(MOTOR_IDS):
    u_rad_s_3 = u_wheels_3[i]
    
    # Quy đổi rad/s sang đơn vị Speed của STS (1 step/s ≈ 0.001534 rad/s)
    speed_steps_3 = int(u_rad_s_3 * 4095 / (2 * np.pi))

    # ĐỔI TỪ WriteSpe THÀNH WriteSpec
    comm_result_3, error_3 = packetHandler.WriteSpec(servo_id, speed_steps_3, acc)

    if comm_result_3 != COMM_SUCCESS:
        print(f"Lỗi Servo {servo_id}: {packetHandler.getTxRxResult(comm_result_3)}")
    else:
        print(f"Servo {servo_id} -> Speed (steps/s): {speed_steps_3}")

print(f"Xe đang di chuyển trong {T_RUN} giây...")
time.sleep(2)

# ==========================================
# 5. DỪNG XE VÀ ĐÓNG CỔNG
# ==========================================
for servo_id in MOTOR_IDS:
    packetHandler.WriteSpec(servo_id, 0, acc) # Dừng động cơ (Tốc độ = 0)

portHandler.closePort()
print("Đã dừng xe và kết thúc chương trình!")