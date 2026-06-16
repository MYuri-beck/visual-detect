import torch

print("=" * 60)
print("🔍 VERIFICANDO INSTALAÇÃO CUDA")
print("=" * 60)

cuda_available = torch.cuda.is_available()
print(f"✅ CUDA disponível: {cuda_available}")

if cuda_available:
    print(f"✅ GPU detectada: {torch.cuda.get_device_name(0)}")
    print(f"✅ Compute Capability: {torch.cuda.get_device_capability(0)}")
    print(f"✅ Total de GPUs: {torch.cuda.device_count()}")
else:
    print("❌ CUDA não detectado!")

print("=" * 60)
