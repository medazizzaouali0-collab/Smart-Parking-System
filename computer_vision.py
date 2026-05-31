import cv2
import numpy as np
import time
import json
import os

# CONFIGURATION - UNE SEULE CAMÉRA
CAMERA_INDEX = 1

# PARAMÈTRES DE DÉTECTION
OCCUPANCY_THRESHOLD = 0.12
MOTION_SENSITIVITY  = 20
BLUR_SIZE           = 21

RANGEE_1_Y = 230  # Hauteur de la rangée du bas  (9 places)
RANGEE_2_Y = 230  # Hauteur de la rangée du haut (6 places)
RAYON      = 8    # Rayon des cercles

ALL_SPOTS = [
    # ── Rangée 1 : 9 places (bas) ──
    {"id":  1, "center": (28, RANGEE_1_Y), "radius": RAYON, "rangee": 1},
    {"id":  2, "center": (62, RANGEE_1_Y), "radius": RAYON, "rangee": 1},
    {"id":  3, "center": (94, RANGEE_1_Y), "radius": RAYON, "rangee": 1},
    {"id":  4, "center": (135, RANGEE_1_Y), "radius": RAYON, "rangee": 1},
    {"id":  5, "center": (169, RANGEE_1_Y), "radius": RAYON, "rangee": 1},
    {"id":  6, "center": (201, RANGEE_1_Y), "radius": RAYON, "rangee": 1},
    {"id":  7, "center": (232, RANGEE_1_Y), "radius": RAYON, "rangee": 1},
    {"id":  8, "center": (264, RANGEE_1_Y), "radius": RAYON, "rangee": 1},
    {"id":  9, "center": (297, RANGEE_1_Y), "radius": RAYON, "rangee": 1},
    # ── Rangée 2 : 6 places (haut) ── 
    {"id": 10, "center": (432, RANGEE_2_Y), "radius": RAYON, "rangee": 2},
    {"id": 11, "center": (464, RANGEE_2_Y), "radius": RAYON, "rangee": 2},
    {"id": 12, "center": (494, RANGEE_2_Y), "radius": RAYON, "rangee": 2},
    {"id": 13, "center": (523, RANGEE_2_Y), "radius": RAYON, "rangee": 2},
    {"id": 14, "center": (552, RANGEE_2_Y), "radius": RAYON, "rangee": 2},
    {"id": 15, "center": (583, RANGEE_2_Y), "radius": RAYON, "rangee": 2},
]

# FONCTIONS DE SAUVEGARDE (LIAISON WEB)
def export_config():
    dossier_actuel = os.path.dirname(os.path.abspath(__file__))
    fichier_config = os.path.join(dossier_actuel, 'parking_config.json')
    config = {"spots": ALL_SPOTS}
    with open(fichier_config, 'w') as f:
        json.dump(config, f)
    print(f"📁 Fichier de configuration créé : {fichier_config}")

def export_status(status_dict):
    import os
    import time
    import json
    
    dossier_actuel = os.path.dirname(os.path.abspath(__file__))
    fichier_temp = os.path.join(dossier_actuel, 'parking_status_temp.json')
    fichier_final = os.path.join(dossier_actuel, 'parking_status.json')

    data = {
        "timestamp": time.time(),
        "status": {str(k): bool(v) for k, v in status_dict.items()}
    }
    
    with open(fichier_temp, 'w') as f:
        json.dump(data, f)
        
    try:
        os.replace(fichier_temp, fichier_final)
    except PermissionError:
        pass

# OUVERTURE CAMÉRA & DÉTECTION
def open_camera(source, name, retries=3):
    for i in range(retries):
        print(f"   Tentative {i+1}/{retries} pour {name}...")
        cap = cv2.VideoCapture(source)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"   ✅ {name} connectée !")
                return cap
        time.sleep(1)
    print(f"   ❌ {name} non trouvée")
    return None

def check_spot(frame, background, spot):
    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray  = cv2.GaussianBlur(gray, (BLUR_SIZE, BLUR_SIZE), 0)
    diff  = cv2.absdiff(background, gray)
    _, thresh = cv2.threshold(diff, MOTION_SENSITIVITY, 255, cv2.THRESH_BINARY)

    mask = np.zeros(thresh.shape, dtype=np.uint8)
    cv2.circle(mask, spot["center"], spot["radius"], 255, -1)
    region  = cv2.bitwise_and(thresh, thresh, mask=mask)

    changed = np.sum(region == 255)
    total   = np.sum(mask   == 255)
    ratio   = changed / total if total > 0 else 0
    return ratio > OCCUPANCY_THRESHOLD

click_log = []
def mouse_cb(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        click_log.append((x, y))
        print(f"   [CALIB] ({x}, {y})")

# PROGRAMME PRINCIPAL
def main():
    print("=" * 60)
    print("🚗 SMART PARKING - 15 PLACES (2 rangées)")
    print("=" * 60)

    export_config()

    cap = open_camera(CAMERA_INDEX, "Caméra parking")
    if cap is None:
        print("\n❌ Caméra non disponible.")
        return

    print("\n📌 INSTRUCTIONS:")
    print("   1. VIDEZ toutes les places")
    print("   2. Appuyez sur [ESPACE] pour capturer l'arrière-plan")
    print("   3. Placez des véhicules → détection automatique")
    print("   [C] Calibration   [R] Recapturer fond   [Q] Quitter")
    print("=" * 60)

    WIN = "Smart Parking - 15 places"
    cv2.namedWindow(WIN, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(WIN, mouse_cb)

    background       = None
    bg_captured      = False
    spots_status     = {s["id"]: False for s in ALL_SPOTS}
    calibration_mode = False
    frame_count      = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame_count += 1
        display = frame.copy()

        if not bg_captured:
            cv2.putText(display, "Videz toutes les places -> appuyez ESPACE",
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            for s in ALL_SPOTS:
                cv2.circle(display, s["center"], s["radius"], (128, 128, 128), 2)
                cv2.putText(display, f"P{s['id']}",
                            (s["center"][0] - 8, s["center"][1] - s["radius"] - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.32, (200, 200, 200), 1)
        else:
            if background is not None and frame_count % 3 == 0:
                for s in ALL_SPOTS:
                    spots_status[s["id"]] = check_spot(frame, background, s)
                
                export_status(spots_status)

            free1 = sum(1 for s in ALL_SPOTS if s["rangee"] == 1 and not spots_status[s["id"]])
            free2 = sum(1 for s in ALL_SPOTS if s["rangee"] == 2 and not spots_status[s["id"]])
            free_total = free1 + free2

            for s in ALL_SPOTS:
                cx, cy = s["center"]
                r      = s["radius"]
                occ    = spots_status[s["id"]]
                color  = (0, 0, 255) if occ else (0, 220, 0)
                label  = "O" if occ else "L"

                cv2.circle(display, (cx, cy), r, color, 2)
                cv2.circle(display, (cx, cy), 3, color, -1)
                cv2.rectangle(display, (cx - r - 2, cy - r - 13), (cx + r + 2, cy - r - 4), color, 1)
                cv2.putText(display, f"P{s['id']}", (cx - 8, cy - r - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (255, 255, 255), 1)
                cv2.putText(display, label, (cx - 4, cy + r + 11), cv2.FONT_HERSHEY_SIMPLEX, 0.32, color, 1)

            cv2.rectangle(display, (0, 0), (display.shape[1], 26), (20, 20, 20), -1)
            cv2.putText(display,
                        f"Rangee 1 (P1-P9): Libres {free1}/9  |  "
                        f"Rangee 2 (P10-P15): Libres {free2}/6  |  "
                        f"TOTAL: {free_total}/15 libres",
                        (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

        if calibration_mode:
            cv2.putText(display, f"CALIBRATION ({len(click_log)} clics) - cliquez P1->P15 dans l'ordre",
                        (5, display.shape[0] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

        cv2.imshow(WIN, display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord(' ') or key == ord('r'):
            print("\n📸 Capture de l'arrière-plan...")
            g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            background  = cv2.GaussianBlur(g, (BLUR_SIZE, BLUR_SIZE), 0)
            bg_captured = True
            print("✅ Arrière-plan capturé ! Détections lancées et synchronisées.")

        elif key == ord('c'):
            calibration_mode = not calibration_mode
            if calibration_mode:
                click_log.clear()
                print("\n[CALIBRATION] ACTIVÉ — cliquez sur P1 à P15 dans l'ordre")
            else:
                print("[CALIBRATION] DÉSACTIVÉ")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()