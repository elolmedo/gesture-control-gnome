import cv2
from func_controlCamara import *

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