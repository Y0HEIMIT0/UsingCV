# main.py

import cv2
import mediapipe as mp
from count import count_fingers

# ---------------------- FLAG DE ENTRADA ----------------------
USE_WEBCAM = True   # True → abrir la cámara; False → abrir un archivo de video
VIDEO_PATH = "video1.mp4"
# --------------------------------------------------------------

# Inicializo la captura según la bandera
if USE_WEBCAM:
    cap = cv2.VideoCapture(0)
else:
    cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("Error: no se puede abrir la fuente de video.")
    exit()

mp_hands   = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
fps    = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter("salida_procesada.mp4", fourcc, fps, (width, height))

# Defino dos paletas de colores (derecha vs. izquierda)
# Para mano DERECHA
COL_RIGHT = {
    "wrist":  (200, 200, 200),
    "thumb":  (0,   200, 200),
    "index":  (0,   255,   0),
    "middle": (200,  0,  200),
    "ring":   (0,    0,  255),
    "pinky":  (255, 100,   0)
}

# Para mano IZQUIERDA
COL_LEFT = {
    "wrist":  (200, 200, 200),
    "thumb":  (0,   150, 150),
    "index":  (0,   200,   0),
    "middle": (150,  0,  150),
    "ring":   (0,    0,  200),
    "pinky":  (200,  80,   0)
}

# Índices de MediaPipe para cada dedo
FINGERS = {
    "thumb":  [1,  2,  3,  4],
    "index":  [5,  6,  7,  8],
    "middle": [9, 10, 11, 12],
    "ring":   [13, 14, 15, 16],
    "pinky":  [17, 18, 19, 20]
}

def dibujar_bounding_box(landmarks, img, color=(255, 255, 255), grosor=2):
    """
    Dibuja un rectángulo (bbox) alrededor de la mano.
    Devuelve (x_min, y_min) de la esquina superior izquierda.
    """
    h, w, _ = img.shape
    xs = [int(lm.x * w) for lm in landmarks]
    ys = [int(lm.y * h) for lm in landmarks]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    cv2.rectangle(img, (x_min, y_min), (x_max, y_max), color, grosor)
    return x_min, y_min

def dibujar_dedos_coloreados(landmarks, img, palette):
    """
    Dibuja cada articulación y conecta las falanges con líneas, usando
    el diccionario 'palette' que debe llevar claves:
    "wrist", "thumb", "index", "middle", "ring", "pinky".
    """
    h, w, _ = img.shape

    # 1) Muñeca (landmark 0)
    x0 = int(landmarks[0].x * w)
    y0 = int(landmarks[0].y * h)
    cv2.circle(img, (x0, y0), 5, palette["wrist"], -1)

    # 2) Cada dedo por separado
    for dedo, indices in FINGERS.items():
        c = palette[dedo]
        pts = []
        for idx in indices:
            x = int(landmarks[idx].x * w)
            y = int(landmarks[idx].y * h)
            pts.append((x, y))
            cv2.circle(img, (x, y), 5, c, -1)
        for i in range(len(pts) - 1):
            cv2.line(img, pts[i], pts[i+1], c, 2)

with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1) Corregir espejado: invertimos horizontalmente
        frame_flipped = cv2.flip(frame, 1)

        # 2) Procesamiento MediaPipe
        img_rgb = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2RGB)
        img_rgb.flags.writeable = False
        results = hands.process(img_rgb)

        img_rgb.flags.writeable = True
        img_out = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

        # 3) Si detecta manos, iteramos por landmarks + handedness
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                  results.multi_handedness):
                label = handedness.classification[0].label  # "Left" o "Right"
                score = handedness.classification[0].score  # confianza (float)

                # Elijo paleta y texto según la mano
                if label == "Right":
                    palette = COL_RIGHT
                    text_label = "Mano Derecha"
                else:
                    palette = COL_LEFT
                    text_label = "Mano Izquierda"

                # 4) Calcular bounding box y coordenada para el texto
                x_min, y_min = dibujar_bounding_box(hand_landmarks.landmark,
                                                    img_out,
                                                    color=palette["index"],
                                                    grosor=2)

                # 5) Contar dedos levantados
                dedos_levantados = count_fingers(hand_landmarks.landmark, label)
                texto_a_mostrar = f"{text_label}: {dedos_levantados}"

                # 6) Dibujar el texto encima del bbox
                cv2.putText(
                    img_out,
                    texto_a_mostrar,
                    (x_min, y_min - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    palette["index"],
                    2,
                    cv2.LINE_AA
                )

                # 7) Dibujar dedos coloreados
                dibujar_dedos_coloreados(hand_landmarks.landmark, img_out, palette)

        # 8) Mostrar en pantalla
        cv2.imshow("Procesando video", img_out)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
            break

        # 9) Guardar frame procesado en el archivo de salida
        out.write(img_out)

    cap.release()
    out.release()
    cv2.destroyAllWindows()
