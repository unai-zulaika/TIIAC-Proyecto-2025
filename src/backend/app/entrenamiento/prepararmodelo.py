import torch
from torch import optim
from autoencoder import Autoencoder

def preparar_modelo(emb_dim=256, lr=1e-4, weight_decay=1e-5):
    """
    Crea el modelo autoencoder + optimizer listos para entrenar.
    Devuelve (model, optimizer).
    """
    model = Autoencoder(emb_dim=emb_dim)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    return model, optimizer
