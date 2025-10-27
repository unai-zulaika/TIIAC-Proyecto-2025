from torchvision import transforms

# Normalización estándar de ImageNet (para ResNet18 pre-entrenada)
normalize = transforms.Normalize(
    mean=[0.485, 0.456, 0.406],
    std=[0.229, 0.224, 0.225],
)

# Transform “normal”: 1 vista, para validación / reconstrucción
base_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    normalize,
])

# Transform para entrenamiento contrastivo: devuelve dos vistas augmentadas
class ContrastiveTransform:
    def __init__(self):
        self.augment = transforms.Compose([
            transforms.RandomResizedCrop(224, scale=(0.5, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(0.4, 0.4, 0.4, 0.1),
            transforms.RandomGrayscale(p=0.1),
            transforms.ToTensor(),
            normalize,
        ])

    def __call__(self, x):
        # devuelve (vista1, vista2)
        return self.augment(x), self.augment(x)
