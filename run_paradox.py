from umcp.tau_r_star import compute_R_min

print("R_min calculation at target tau = 1.0 :")
print(compute_R_min(0.31, 0.2, 1.0))
print(compute_R_min(0.10, 0.2, 1.0))
print(compute_R_min(0.99, 0.2, 1.0))
