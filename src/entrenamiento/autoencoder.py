import torch, torch.nn as nn, torch.nn.functional as F
from torchvision import models

# --- Encoder: ResNet18 backbone + projector ---
class Encoder(nn.Module):
    def __init__(self, emb_dim=256):
        super().__init__()
        base = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        self.feature_extractor = nn.Sequential(*(list(base.children())[:-1]))  # hasta avgpool
        self.proj = nn.Sequential(
            nn.Linear(512, 512),
            nn.ReLU(inplace=True),
            nn.Linear(512, emb_dim)
        )

    def forward(self, x):
        h = self.feature_extractor(x)       # [B, 512, 1, 1]
        h = h.view(h.size(0), -1)           # [B, 512]
        z = self.proj(h)                    # [B, emb_dim]
        z = F.normalize(z, dim=1)           # L2 normalize (para coseno)
        return z

# --- Decoder: convtranspose (simple) ---
class Decoder(nn.Module):
    def __init__(self, emb_dim=256, base_ch=256, out_ch=3):
        super().__init__()
        # map emb -> small spatial seed (e.g., 256 x 7 x 7)
        self.fc = nn.Sequential(
            nn.Linear(emb_dim, base_ch * 7 * 7),
            nn.ReLU(True)
        )
        self.deconv = nn.Sequential(
            nn.ConvTranspose2d(base_ch, 128, 4, stride=2, padding=1), nn.ReLU(True),  # 14x14
            nn.ConvTranspose2d(128, 64, 4, stride=2, padding=1), nn.ReLU(True),       # 28x28
            nn.ConvTranspose2d(64, 64, 4, stride=2, padding=1), nn.ReLU(True),        # 56x56
            nn.ConvTranspose2d(64, 32, 4, stride=2, padding=1), nn.ReLU(True),        # 112x112
            nn.ConvTranspose2d(32, out_ch, 4, stride=2, padding=1), nn.Sigmoid()      # 224x224
        )

    def forward(self, z):
        h = self.fc(z)                           # [B, base_ch*7*7]
        h = h.view(h.size(0), -1, 7, 7)         # [B, base_ch, 7, 7]
        x_rec = self.deconv(h)                  # [B, 3, 224, 224] in [0,1]
        return x_rec

class Autoencoder(nn.Module):
    def __init__(self, emb_dim=256):
        super().__init__()
        self.encoder = Encoder(emb_dim)
        self.decoder = Decoder(emb_dim)

    def forward(self, x):
        z = self.encoder(x)
        x_rec = self.decoder(z)
        return z, x_rec

# --- Losses ---
def recon_loss(x, x_rec):  # píxel MSE; añade SSIM/perceptual si quieres
    return F.mse_loss(x_rec, x)

def contrastive_ntxent(z1, z2, temperature=0.1):
    # z1,z2: [B, D], L2-normalized
    B = z1.size(0)
    z = torch.cat([z1, z2], dim=0)                 # [2B, D]
    sim = torch.matmul(z, z.t()) / temperature     # cos sim / T
    mask = torch.eye(2*B, dtype=torch.bool, device=z.device)
    sim.masked_fill_(mask, -1e9)

    targets = torch.arange(B, device=z.device)
    targets = torch.cat([targets + B, targets], dim=0)  # positives

    loss = F.cross_entropy(sim, targets)
    return loss

# --- Training step (mix recon + contrastive) ---
def training_step(model, batch, optimizer, alpha=1.0, beta=0.5):
    """
    alpha: peso recon, beta: peso contrastive
    batch: (x1, x2) si haces contrastive con 2 views; si no, usa (x, x).
    """
    model.train()
    x1, x2 = batch  # dos augmentaciones de la misma imagen
    z1, x1_rec = model(x1)
    z2, x2_rec = model(x2)

    loss_recon = recon_loss(x1, x1_rec) + recon_loss(x2, x2_rec)
    loss_contr = contrastive_ntxent(z1, z2)
    loss = alpha * loss_recon + beta * loss_contr

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return loss.item(), loss_recon.item(), loss_contr.item()
