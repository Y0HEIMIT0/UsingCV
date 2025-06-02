# count.py

def count_fingers(landmarks, handedness_label):
    """
    Cuenta cuántos dedos están levantados en una mano.
    
    Para dedos índice, medio, anular y meñique:
      - Si la y del tip (landmark[i*4 + 4]) está por encima (menor en coordenada) 
        que la y del pip (landmark[i*4 + 2]), el dedo se considera levantado.
    
    Para pulgar:
      - Si es mano Derecha: comparamos x de TIP (landmark[4]) con x de IP (landmark[3]).
        Si x_tip > x_ip  → pulgar levantado.
      - Si es mano Izquierda: si x_tip < x_ip → pulgar levantado.
    
    landmarks: lista de 21 objetos tipo landmark (cada uno con .x y .y normalizados).
    handedness_label: cadena "Right" o "Left".
    
    Devuelve el número entero de dedos levantados (0–5).
    """
    count = 0
    
    # 1) Pulgar
    # landmark[4] = THUMB_TIP, landmark[3] = THUMB_IP
    if handedness_label == "Right":
        if landmarks[4].x > landmarks[3].x:
            count += 1
    else:  # Left
        if landmarks[4].x < landmarks[3].x:
            count += 1
    
    # 2) Índice, Medio, Anular, Meñique
    # Para cada uno: tip = landmark[idx_tip], pip = landmark[idx_pip]
    fingers_indices = {
        "index":  (8, 6),
        "middle": (12, 10),
        "ring":   (16, 14),
        "pinky":  (20, 18)
    }
    
    for tip_idx, pip_idx in fingers_indices.values():
        if landmarks[tip_idx].y < landmarks[pip_idx].y:
            count += 1
    
    return count
