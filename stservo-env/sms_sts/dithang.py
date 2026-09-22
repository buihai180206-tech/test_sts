import sys
import time
import numpy as np

# Thêm thư viện SDK
sys.path.append(".")
from scservo_sdk import *

# ==========================================
# 1. TÍNH ĐỘNG HỌC NGƯỢC (INVERSE KINEMATICS)
# ==========================================
def inverse_kinematics(v_x, v_y, w_z):
    d = 0.13  # Khoảng cách từ tâm xe đến bánh xe (m)
    r = 0.0508  # Bán kính bánh xe (m)

    v = np.array([v_x, v_y, w_z])
    H = np.array(
        [
            [1.0, 0.0, -d],
            [-0.5, -np.sqrt(3) / 2, -d],
            [-0.5, np.sqrt(3) / 2, -d],
        ]
    )
    # Tốc độ góc của 3 bánh xe (rad/s)
    u = (1.0 / r) * np.dot(H, v)
    return u


# ==========================================
# 2. CẤU HÌNH PHẦN CỨNG & KẾT NỐI
# ==========================================
DEVICENAME = "COM19"  # Sửa lại đúng cổng COM trên máy bạn
BAUDRATE = 1000000

# ID tương ứng với bánh 1, bánh 2, bánh 3
MOTOR_IDS = [9, 8, 7]

portHandler = PortHandler(DEVICENAME)
packetHandler = sms_sts(portHandler)

if not portHandler.openPort() or not portHandler.setBaudRate(BAUDRATE):
    print("Lỗi mở cổng COM hoặc cài đặt Baudrate!")
    sys.exit()

# ==========================================
# 3. TÍNH VẬN TỐC CHO ROBOT ĐI THẲNG
# ==========================================
# Vận tốc mong muốn: đi thẳng theo v_x = 0.2 m/s, v_y = 0, w_z = 0
v_x_target = 0.0  # m/s (Đi thẳng)
v_y_target = 0.13  # m/s (Đi ngang)
w_z_target = 0.0  # rad/s (Xoay tại chỗ)

u_wheels = inverse_kinematics(v_x_target, v_y_target, w_z_target)
print(f"Tốc độ góc tính toán [u1, u2, u3] (rad/s): {u_wheels}")

# ==========================================
# 4. CHUYỂN ĐỔI BƯỚC RAD/S SANG LỆNH SERVO
# ==========================================
# Đối với dòng STS/SCS trong chế độ vị trí Position Mode:
# Bạn có thể quy đổi rad/s ra góc quay mong muốn trong khoảng thời gian T_RUN.

T_RUN = 3.0  # Thời gian chạy (giây)
acc = 50

print("Đang gửi lệnh đi thẳng...")

for i, servo_id in enumerate(MOTOR_IDS):
    u_rad_s = u_wheels[i]  # Tốc độ góc rad/s

    # 1. Tính tổng góc quay (rad) = u * t
    delta_angle_rad = u_rad_s * T_RUN

    # 2. Quy đổi rad sang xung vị trí Servo (4096 xung = 2*pi rad)
    # PositionDelta = (delta_angle_rad / (2 * pi)) * 4095
    position_delta = int((delta_angle_rad / (2 * np.pi)) * 4095)

    # 3. Quy đổi tốc độ rad/s sang đơn vị Speed của Feetech (1 Step/s = 0.088 deg/s ~= 0.001536 rad/s)
    # Hoặc tính sơ bộ: Speed (steps/s) = abs(rad/s) * 4096 / (2*pi)
    speed_steps = int(abs(u_rad_s) * 4095 / (2 * np.pi))

    # Đảm bảo tốc độ tối thiểu để động cơ không bị dời lệnh
    speed = max(speed_steps, 100)

    # Vị trí mục tiêu (giả định vị trí hiện tại là 0 hoặc offset góc tương đối)
    target_position = position_delta
    if target_position < 0:
        target_position = 4095 + (target_position % 4095)
    else:
        target_position = target_position % 4095

    # Gửi lệnh
    comm_result, error = packetHandler.WritePosEx(
        servo_id, target_position, speed, acc
    )

    if comm_result != COMM_SUCCESS:
        print(
            f"Lỗi Servo {servo_id}: {packetHandler.getTxRxResult(comm_result)}"
        )
    else:
        print(
            f"Servo {servo_id} -> Position: {target_position}, Speed: {speed}"
        )

# ==========================================
# 5. ĐỜI HOÀN THÀNH VÀ ĐÓNG CỔNG
# ==========================================
time.sleep(T_RUN)
portHandler.closePort()
print("Đã hoàn thành chuyển động!")