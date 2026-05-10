import cv2
import mediapipe as mp
import pyautogui
import os
import time
import math

def initialize_detector():
    """Configura el detector de manos de MediaPipe con salida visual."""
    try:
        mp_hands = mp.solutions.hands
        return mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
    except Exception:
        return None

def check_gesture_v(hand_landmarks):
    """Gesto V: Índice y Corazón extendidos, Anular y Meñique cerrados."""
    try:
        # Extendidos: 8 y 12 | Cerrados: 16 y 20
        extended = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y and \
                   hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
        closed = hand_landmarks.landmark[16].y > hand_landmarks.landmark[14].y and \
                 hand_landmarks.landmark[20].y > hand_landmarks.landmark[18].y
        return extended and closed
    except Exception: return False

def check_gesture_l(hand_landmarks):
    """Gesto L: Pulgar e Índice extendidos (formando 90 grados), resto cerrados."""
    try:
        # Índice hacia arriba, Pulgar hacia un lado, resto hacia abajo
        index_up = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
        thumb_out = abs(hand_landmarks.landmark[4].x - hand_landmarks.landmark[2].x) > 0.05
        others_closed = all(hand_landmarks.landmark[i].y > hand_landmarks.landmark[i-2].y for i in [12, 16, 20])
        return index_up and thumb_out and others_closed
    except Exception: return False

def check_gesture_rock(hand_landmarks):
    try:
        extended = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y and \
                   hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y
        closed = hand_landmarks.landmark[12].y > hand_landmarks.landmark[10].y and \
                 hand_landmarks.landmark[16].y > hand_landmarks.landmark[14].y
        return extended and closed
    except Exception: return False

def check_gesture_fist(hand_landmarks):
    try:
        tips, mips = [8, 12, 16, 20], [6, 10, 14, 18]
        return all(hand_landmarks.landmark[t].y > hand_landmarks.landmark[m].y for t, m in zip(tips, mips))
    except Exception: return False

def check_gesture_palm(hand_landmarks):
    try:
        return hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y and \
               hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
    except Exception: return False

def detect_screenshot_gesture(hand_landmarks):
    try:
        thumb_tip, index_tip = hand_landmarks.landmark[4], hand_landmarks.landmark[8]
        distance = math.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)
        others_extended = all(hand_landmarks.landmark[i].y < hand_landmarks.landmark[i-2].y for i in [12, 16, 20])
        return distance < 0.05 and others_extended
    except Exception: return False

def process_gestures(hand_landmarks, last_time, cooldown, hand_label):
    """Identifica el gesto y devuelve el nombre para mostrarlo en pantalla."""
    now = time.time()
    gesture_name = "Ninguno"
    
    try:
        if check_gesture_rock(hand_landmarks):
            gesture_name = "ROCK (Spotify)"
            # os.system("/snap/bin/spotify &")
        
        elif check_gesture_v(hand_landmarks):
            gesture_name = "V (Victoria)"
            
        elif check_gesture_l(hand_landmarks):
            gesture_name = "L (L-Shape)"

        elif hand_label == "Left" and detect_screenshot_gesture(hand_landmarks):
            gesture_name = "Screenshot"
            # pyautogui.press('printscreen')

        elif check_gesture_fist(hand_landmarks):
            gesture_name = "FIST (Lock)"
            # os.system("xdg-screensaver lock")

        elif check_gesture_palm(hand_landmarks):
            palm_x = hand_landmarks.landmark[9].x
            if palm_x < 0.35: gesture_name = "Palm Left (Escritorio)"
            elif palm_x > 0.65: gesture_name = "Palm Right (Escritorio)"
            else: gesture_name = "PALM (Centro)"
            
    except Exception: pass
    return gesture_name

def run_service():
    detector = initialize_detector()
    mp_draw = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened() or detector is None:
        print("Error al iniciar cámara o detector.")
        return

    print("Iniciando modo depuración visual. Presiona 'q' para salir.")

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = detector.process(rgb_frame)
            
            current_gesture = "Buscando mano..."

            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    hand_label = handedness.classification[0].label
                    
                    # Dibujar esqueleto de la mano
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
                    
                    # Detectar gesto
                    current_gesture = f"[{hand_label}] {process_gestures(hand_landmarks, 0, 0, hand_label)}"

            # Mostrar info en pantalla
            cv2.putText(frame, current_gesture, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Debug de Gestos', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
    finally:
        print("Cerrando recursos...")
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_service()