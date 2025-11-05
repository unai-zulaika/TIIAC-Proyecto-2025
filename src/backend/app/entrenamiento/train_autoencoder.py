import os
from typing import Set

import torch
from torch.utils.data import DataLoader
from torchvision import datasets
from tqdm import tqdm

# --- módulos propios ---
from autoencoder import Autoencoder, training_step
from prepararmodelo import preparar_modelo
from normalization import ContrastiveTransform, base_transform
if __name__ == "__main__":
    # ---------------- Config ----------------
    DATA_DIR = "data/train"      # Directorio raíz de imágenes de entrenamiento
    VAL_DIR = "data/val"         # Directorio raíz de imágenes de validación
    BATCH_SIZE = 32
    EPOCHS = 10
    EMB_DIM = 256
    LR = 1e-4
    ALPHA, BETA = 1.0, 0.5       # pesos: recon / contrastive
    NUM_WORKERS = 4
    SAVE_DIR = "checkpoints"
    os.makedirs(SAVE_DIR, exist_ok=True)

    # ------------- Cargar datasets -------------
    train_dataset = datasets.ImageFolder(DATA_DIR, transform=ContrastiveTransform())
    val_dataset = datasets.ImageFolder(VAL_DIR, transform=base_transform)

    print(f"[INFO] Clases (carpetas) totales: {len(train_dataset.classes)}")
    print(f"[INFO] Imágenes train: {len(train_dataset.samples)}")
    print(f"[INFO] Imágenes val: {len(val_dataset.samples)}")

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=True,
        persistent_workers=NUM_WORKERS > 0,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=max(1, NUM_WORKERS // 2),
        pin_memory=True,
        persistent_workers=NUM_WORKERS > 0,
    )

    # ------------- Modelo ----------------
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, optimizer = preparar_modelo(emb_dim=EMB_DIM, lr=LR)
    model.to(device)

    # ------------- Validación (reconstrucción) -------------
    @torch.no_grad()
    def evaluate_recon(model: Autoencoder, loader: DataLoader) -> float:
        model.eval()
        import torch.nn.functional as F
        total, count = 0.0, 0
        for x in loader:
            if isinstance(x, (list, tuple)):
                x = x[0]
            x = x.to(device)
            _, x_rec = model(x)
            loss = F.mse_loss(x_rec, x, reduction="sum")
            total += loss.item()
            count += x.size(0)
        return total / count if count > 0 else float("nan")

    # ------------- Entrenamiento ----------------
    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss = total_recon = total_contr = 0.0

        for batch in tqdm(train_loader, desc=f"Epoch {epoch}/{EPOCHS}"):
            x1, x2 = batch[0] if isinstance(batch, (list, tuple)) else batch
            x1, x2 = x1.to(device), x2.to(device)
            loss, l_rec, l_con = training_step(model, (x1, x2), optimizer, ALPHA, BETA)
            total_loss += loss
            total_recon += l_rec
            total_contr += l_con

        n = len(train_loader)
        train_loss = total_loss / n
        train_rec = total_recon / n
        train_con = total_contr / n

        val_rec = evaluate_recon(model, val_loader)

        print(f"→ Epoch {epoch:02d} | train(total)={train_loss:.4f} "
              f"recon={train_rec:.4f} contr={train_con:.4f} | val_recon={val_rec:.4f}")

        torch.save(model.state_dict(), os.path.join(SAVE_DIR, f"autoencoder_epoch{epoch}.pth"))

    print("\n✅ Entrenamiento finalizado.")
    torch.save(model.encoder.state_dict(), os.path.join(SAVE_DIR, "encoder_final.pth"))
