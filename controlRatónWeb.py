import cv2
import mediapipe as mp
import pyautogui
import math

def initialize_tracker():
    """Configura el detector de manos de MediaPipe."""
    try:
        mp_hands = mp.solutions.hands
        return mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
    except Exception as e:
        print(f"Error al inicializar MediaPipe: {e}")
        return None

def get_finger_coords(frame, hand_landmarks, finger_index):
    """Extrae las coordenadas X, Y de un dedo específico."""
    try:
        h, w, _ = frame.shape
        landmark = hand_landmarks.landmark[finger_index]
        return int(landmark.x * w), int(landmark.y * h)
    except IndexError:
        return None
    
def map_range(value, in_min, in_max, out_min, out_max):
    """Mapea un valor de un rango de entrada a un rango de salida."""
    try:
        # Evitar división por cero
        if in_max == in_min:
            return out_min
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    except Exception as e:
        print(f"Error en mapeo de rango: {e}")
        return 0

def control_cursor(coords, cam_res, screen_res):
    """
    Mueve el cursor escalando las coordenadas.
    coords: (x, y) del dedo
    cam_res: (w, h) de la captura
    screen_res: (w, h) del monitor
    """
    try:
        x, y = coords
        cam_w, cam_h = cam_res
        scr_w, scr_h = screen_res

        # Mapeo de X e Y
        target_x = map_range(x, 0, cam_w, 0, scr_w)
        target_y = map_range(y, 0, cam_h, 0, scr_h)

        pyautogui.moveTo(target_x, target_y, _pause=False)
    except Exception as e:
        print(f"Error al mover cursor: {e}")

def detect_click(thumb, index, threshold=30):
    """Ejecuta un clic si la distancia entre pulgar e índice es mínima."""
    try:
        distance = math.hypot(index[0] - thumb[0], index[1] - thumb[1])
        if distance < threshold:
            pyautogui.click()
            return True
        return False
    except Exception:
        return False

def run_virtual_mouse():
    """Bucle principal de captura y procesamiento del ratón virtual."""
    detector = initialize_tracker()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: No se pudo acceder a la webcam.")
        return

    screen_res = pyautogui.size()
    pyautogui.FAILSAFE = False 

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            # Definimos la resolución de la cámara para el mapeo
            cam_res = (frame.shape[1], frame.shape[0])
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = detector.process(rgb_frame)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # 8 = Punta índice, 4 = Punta pulgar
                    index_pos = get_finger_coords(frame, hand_landmarks, 8)
                    thumb_pos = get_finger_coords(frame, hand_landmarks, 4)

                    if index_pos:
                        # Uso de la nueva función con paso de tuplas
                        control_cursor(index_pos, cam_res, screen_res)                                        
                    
                    if index_pos and thumb_pos:
                        detect_click(thumb_pos, index_pos)

            cv2.imshow('Mouse Virtual', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()

run_virtual_mouse()
