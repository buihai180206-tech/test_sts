import numpy as np
v_x = float(input("Gia tri cua vx: "))
v_y = float(input("Gia tri cua vy: "))
w_z = float(input("Gia tri cua wz: "))
def inverse_kinematics(v_x, v_y, w_z):
    d = 0.15 
    r = 0.05 
    
    v = np.array([v_x, v_y, w_z])
    H = np.array([
        [1.0,  0.0,         -d],
        [-0.5, -np.sqrt(3)/2, -d],
        [-0.5,  np.sqrt(3)/2, -d]
    ])
    u = (1.0 / r) * np.dot(H, v)
    return u

u_wheels = inverse_kinematics(v_x, v_y, w_z)
print("[u1, u2, u3] (rad/s):", u_wheels)