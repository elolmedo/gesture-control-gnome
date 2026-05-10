# 🖐️ Gesture Control for GNOME (Debian/Ubuntu)

Este proyecto es un controlador gestual ligero diseñado para optimizar el flujo de trabajo en entornos **GNOME**. Utiliza visión artificial para mapear movimientos de la mano y traducirlos en comandos de sistema, automatizando tareas diarias como el bloqueo de sesión, navegación y control multimedia.

## 🚀 Características
- **Zero-Touch Interface**: Controla tu PC sin tocar el teclado.
- **GNOME Native**: Comandos optimizados para `xdg-screensaver`, `gnome-screenshot` y gestión de escritorios virtuales.
- **Bajo Consumo**: Procesamiento optimizado con MediaPipe y resolución de captura ajustada.

---

## 🛠️ Requisitos del Sistema
- **SO**: Debian, Ubuntu o derivados con GNOME.
- **Hardware**: Cámara web estándar (RGB).
- **Python**: 3.10+
- **Dependencias**:
  - `mediapipe`: Para el tracking de la mano.
  - `opencv-python`: Procesamiento de imagen.
  - `pyautogui`: Simulación de entradas de teclado.

---

## 🎮 Diccionario de Gestos

| Gesto | Representación | Acción en el Sistema |
| :--- | :--- | :--- |
| **Puño Cerrado** | ✊ | Bloqueo de pantalla inmediato. |
| **Palma Abierta** | ✋ | Cambio de escritorio (Mover a los lados). |
| **Signo del Rock** | 🤘 | Abrir Spotify. |
| **Letra V** | ✌️ | Abrir la Terminal (gnome-terminal). |
| **Letra L** | ☝️+👍 | Abrir el Navegador (Google). |
| **Círculo (Mano Izq)** | 👌 | Abrir capturador de pantalla interactivo. |

---

## ⚙️ Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/gesture-control-gnome.git](https://github.com/tu-usuario/gesture-control-gnome.git)
   cd gesture-control-gnome
