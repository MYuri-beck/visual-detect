import os
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from pytorch_grad_cam import GradCAM
from ultralytics import YOLO

MODEL_PATH = r"C:\Users\yurim\Desktop\Software Visual Detect\VisualDetect\trainings\runs\detect\treio_yolov8m_fenecit2\weights\best.pt"
INPUT_FOLDER = r"C:\Users\yurim\Desktop\Software Visual Detect\VisualDetect\Main\capturas_voluntarios_analisar"
OUTPUT_FOLDER = r"C:\Users\yurim\Desktop\Software Visual Detect\VisualDetect\Main\GRAD_CAM_VOLUNTARIOS"
IMG_SIZE = 640
CONF_THRESHOLD = 0.25
OVERLAY_ALPHA = 0.45


def render_cam_overlay(img_bgr, grayscale_cam):
    cam_norm = np.clip(grayscale_cam, 0.0, 1.0)
    heat_uint8 = np.uint8(cam_norm * 255.0)
    heat_bgr = cv2.applyColorMap(heat_uint8, cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(img_bgr, 1.0 - OVERLAY_ALPHA, heat_bgr, OVERLAY_ALPHA, 0)
    return overlay, heat_bgr


def draw_label(img_bgr, text, color):
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.75
    thickness = 2
    (text_w, text_h), _ = cv2.getTextSize(text, font, scale, thickness)

    x = 12
    y = 20
    pad = 8

    cv2.rectangle(
        img_bgr,
        (x - pad, y - pad),
        (x + text_w + pad, y + text_h + pad),
        (20, 20, 20),
        -1,
    )
    cv2.putText(img_bgr, text, (x, y + text_h), font, scale, color, thickness, cv2.LINE_AA)


class YoloCamWrapper(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, x):
        # Clone na entrada e saida para evitar Inference Tensor no backward do Grad-CAM.
        x = x.clone()
        with torch.enable_grad():
            out = self.model(x)

        if isinstance(out, (list, tuple)):
            return out[0].clone()
        return out.clone()


class YoloClassTarget:
    def __init__(self, class_id):
        self.class_id = int(class_id)

    def __call__(self, model_output):
        out = model_output.clone()

        # YOLOv8 geralmente retorna [B, C, N], com classes iniciando apos box channels.
        if out.ndim == 3 and out.shape[1] >= 5:
            cls_channel = min(4 + self.class_id, out.shape[1] - 1)
            return out[0, cls_channel, :].max()

        # Fallback para layout [B, N, C].
        if out.ndim == 3 and out.shape[2] >= 5:
            cls_channel = min(4 + self.class_id, out.shape[2] - 1)
            return out[0, :, cls_channel].max()

        return out.max()


class YoloMaxTarget:
    def __call__(self, model_output):
        # Garante um escalar para backward, mesmo sem deteccao.
        out = model_output.clone()
        return out.max()


def find_last_conv_layer(model):
    for module in reversed(list(model.modules())):
        if isinstance(module, torch.nn.Conv2d):
            return module
    raise RuntimeError("Nao foi possivel encontrar camada convolucional para o Grad-CAM.")


def main():
    if not os.path.isfile(MODEL_PATH):
        raise FileNotFoundError(f"Modelo nao encontrado: {MODEL_PATH}")
    if not os.path.isdir(INPUT_FOLDER):
        raise FileNotFoundError(f"Pasta de imagens nao encontrada: {INPUT_FOLDER}")

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Dispositivo: {device}")

    # Usa dois objetos distintos para evitar contaminar o caminho do autograd
    # com tensores criados no fluxo de inferencia do predict().
    yolo_pred = YOLO(MODEL_PATH)
    yolo_cam = YOLO(MODEL_PATH)

    inner_model = yolo_cam.model.to(device)
    inner_model.train()

    for module in inner_model.modules():
        if hasattr(module, "training"):
            module.training = True

    cam_model = YoloCamWrapper(inner_model)
    target_layers = [find_last_conv_layer(inner_model)]
    cam = GradCAM(model=cam_model, target_layers=target_layers)

    output_subfolder = os.path.join(OUTPUT_FOLDER, Path(MODEL_PATH).stem)
    os.makedirs(output_subfolder, exist_ok=True)

    image_files = [
        f
        for f in sorted(os.listdir(INPUT_FOLDER))
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if not image_files:
        raise RuntimeError(f"Nenhuma imagem encontrada em: {INPUT_FOLDER}")

    total = 0
    ok = 0
    fail = 0

    for img_name in image_files:
        total += 1
        img_path = os.path.join(INPUT_FOLDER, img_name)

        try:
            img_bgr = cv2.imread(img_path)
            if img_bgr is None:
                raise RuntimeError("Falha ao ler imagem com OpenCV.")

            img_bgr = cv2.resize(img_bgr, (IMG_SIZE, IMG_SIZE))
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

            input_tensor = torch.from_numpy(img_rgb).permute(2, 0, 1).unsqueeze(0).to(device)
            input_tensor = input_tensor.clone().detach().requires_grad_(True)

            with torch.no_grad():
                pred = yolo_pred.predict(img_bgr, conf=CONF_THRESHOLD, verbose=False)[0]
            if len(pred.boxes) > 0:
                class_id = int(pred.boxes[0].cls[0])
                conf = float(pred.boxes[0].conf[0])
                label = str(yolo_pred.names[class_id]).upper()
                targets = [YoloClassTarget(class_id)]
                draw_text = f"{label} ({conf * 100:.1f}%)"
                suffix = label.lower().replace(" ", "_")
                color = (0, 255, 0)
            else:
                targets = [YoloMaxTarget()]
                draw_text = "SEM DETECCAO"
                suffix = "sem_deteccao"
                color = (0, 0, 255)

            grayscale_cam = cam(input_tensor=input_tensor, targets=targets)[0]
            cam_img_bgr, heatmap_bgr = render_cam_overlay(img_bgr, grayscale_cam)
            draw_label(cam_img_bgr, draw_text, color)

            out_name = f"{Path(MODEL_PATH).stem}_{suffix}_{Path(img_name).stem}.jpg"
            out_path = os.path.join(output_subfolder, out_name)
            if not cv2.imwrite(out_path, cam_img_bgr):
                raise RuntimeError("Falha ao salvar arquivo de saida.")

            heat_name = f"{Path(MODEL_PATH).stem}_{suffix}_{Path(img_name).stem}_heatmap.jpg"
            heat_path = os.path.join(output_subfolder, heat_name)
            if not cv2.imwrite(heat_path, heatmap_bgr):
                raise RuntimeError("Falha ao salvar heatmap puro.")

            ok += 1
            print(f"OK: {out_name}")

        except Exception as exc:
            fail += 1
            print(f"ERRO: {img_name} -> {exc}")

    print("\nResumo")
    print(f"Total de imagens: {total}")
    print(f"Processadas com sucesso: {ok}")
    print(f"Com erro: {fail}")
    print(f"Saida: {output_subfolder}")

    if ok == 0:
        raise RuntimeError("Nenhuma imagem foi processada com sucesso.")

    if fail > 0:
        raise RuntimeError("Processamento finalizado com erros. Revise as linhas 'ERRO:' acima.")

    print("Nenhum erro encontrado. Grad-CAM concluido com sucesso.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FALHA FINAL: {e}")
        sys.exit(1)
