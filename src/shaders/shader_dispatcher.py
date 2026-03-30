from src.shaders.phong import shade_phong

def shade(material_cfg, **kwargs):
    model = material_cfg["model"]

    if model == "phong":
        return shade_phong(mat_cfg=material_cfg, **kwargs)
    
    raise ValueError(f"Unknown material config or Illumination model:{model}")