import cv2
import mediapipe as mp
import pyautogui
import os
import time
import math
import subprocess

def initialize_detector():
    """Configura el detector de manos para ejecución en segundo plano."""
    try:
        mp_hands = mp.solutions.hands
        return mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
    except Exception:
        return None

def check_gesture_v(hand_landmarks):
    """Gesto V: Índice y Corazón extendidos."""
    try:
        extended = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y and \
                   hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
        closed = hand_landmarks.landmark[16].y > hand_landmarks.landmark[14].y and \
                 hand_landmarks.landmark[20].y > hand_landmarks.landmark[18].y
        return extended and closed
    except Exception: return False

def check_gesture_l(hand_landmarks):
    """Gesto L: Pulgar e Índice formando 90 grados."""
    try:
        index_up = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
        thumb_out = abs(hand_landmarks.landmark[4].x - hand_landmarks.landmark[2].x) > 0.05
        others_closed = all(hand_landmarks.landmark[i].y > hand_landmarks.landmark[i-2].y for i in [12, 16, 20])
        return index_up and thumb_out and others_closed
    except Exception: return False

def check_gesture_rock(hand_landmarks):
    """Gesto Rock: Índice y Meñique extendidos."""
    try:
        extended = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y and \
                   hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y
        closed = hand_landmarks.landmark[12].y > hand_landmarks.landmark[10].y and \
                 hand_landmarks.landmark[16].y > hand_landmarks.landmark[14].y
        return extended and closed
    except Exception: return False

def check_gesture_fist(hand_landmarks):
    """Puño: Todos los dedos por debajo de sus nudillos. Revisado para bloqueo."""
    try:
        # Verificamos que las 4 puntas estén claramente bajo los nudillos medios
        return all(hand_landmarks.landmark[i].y > hand_landmarks.landmark[i-2].y for i in [8, 12, 16, 20])
    except Exception: return False

def check_gesture_palm(hand_landmarks):
    """Gesto Palma: Mano abierta."""
    try:
        return hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y and \
               hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
    except Exception: return False

def detect_screenshot_gesture(hand_landmarks):
    """Gesto Círculo (Mano Izquierda): Captura de pantalla."""
    try:
        thumb_tip, index_tip = hand_landmarks.landmark[4], hand_landmarks.landmark[8]
        distance = math.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)
        others_extended = all(hand_landmarks.landmark[i].y < hand_landmarks.landmark[i-2].y for i in [12, 16, 20])
        return distance < 0.05 and others_extended
    except Exception: return False

def process_gestures(hand_landmarks, last_time, cooldown, hand_label):
    """Ejecuta comandos de forma asíncrona para evitar bloqueos del servicio."""
    now = time.time()
    if now - last_time < cooldown:
        return last_time

    try:
        # Gesto Rock -> Spotify (Uso de Popen para evitar el efecto 'buturut')
        if check_gesture_rock(hand_landmarks):
            # DETACHED_PROCESS garantiza que Spotify viva aunque el script muera
            subprocess.Popen(["spotify"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return now
        
        # Gesto V -> Terminal
        elif check_gesture_v(hand_landmarks):
            subprocess.Popen(["gnome-terminal"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return now
            
        # Gesto L -> Navegador
        elif check_gesture_l(hand_landmarks):
            subprocess.Popen(["xdg-open", "https://www.google.com"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return now

        # Círculo -> Capturador (Solo Izquierda)
        elif hand_label == "Left" and detect_screenshot_gesture(hand_landmarks):
            pyautogui.press('printscreen')
            return now

        # Puño -> Bloqueo (Este es rápido, os.system suele bastar, pero mejor unificamos)
        elif check_gesture_fist(hand_landmarks):
            os.system("xdg-screensaver lock &")
            return now

        # Palma -> Cambio de escritorio
        elif check_gesture_palm(hand_landmarks):
            palm_x = hand_landmarks.landmark[9].x
            if palm_x < 0.35:
                pyautogui.hotkey('ctrl', 'alt', 'left')
                return now
            elif palm_x > 0.65:
                pyautogui.hotkey('ctrl', 'alt', 'right')
                return now
                
    except Exception as e:
        # Evitamos que un error de comando rompa el bucle de la cámara
        pass
    
    return last_time

def run_service():
    """Bucle optimizado para ejecución como proceso de fondo."""
    detector = initialize_detector()
    cap = cv2.VideoCapture(0)
    
    # Reducimos resolución para eficiencia energética
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    last_action_time = 0
    cooldown_period = 1.5 # Cooldown ligeramente mayor para estabilidad
    
    if not cap.isOpened() or detector is None:
        return

    pyautogui.FAILSAFE = False 

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = detector.process(rgb_frame)
            
            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    hand_label = handedness.classification[0].label
                    last_action_time = process_gestures(
                        hand_landmarks, last_action_time, cooldown_period, hand_label
                    )
            
            # 30 FPS aprox. para no saturar
            time.sleep(0.03)
            
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_service()