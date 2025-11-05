import torch
from tqdm import tqdm
from autoencoder import training_step

def train_one_epoch(model,
                    train_loader,
                    optimizer,
                    device,
                    alpha=1.0,
                    beta=0.5,
                    desc="Training"):
    """
    Entrena 1 epoch completo sobre train_loader.
    Devuelve (avg_total_loss, avg_recon_loss, avg_contrastive_loss).
    """
    model.train()
    total_loss = 0.0
    total_recon = 0.0
    total_contr = 0.0

    for batch in tqdm(train_loader, desc=desc):
        # batch viene de ImageFolder con ContrastiveTransform:
        # batch = ((x1, x2), label)
        (x1, x2), _ = batch
        x1 = x1.to(device)
        x2 = x2.to(device)

        loss, loss_recon, loss_contr = training_step(
            model,
            (x1, x2),
            optimizer,
            alpha,
            beta
        )

        total_loss += loss
        total_recon += loss_recon
        total_contr += loss_contr

    n = len(train_loader)
    return total_loss / n, total_recon / n, total_contr / n
