from src.shaders.phong import shade_phong
from src.shaders.blinn_phong import shade_blinn_phong

def shade(material_cfg, **kwargs):
    model = material_cfg["model"]

    if model == "phong":
        return shade_phong(mat_cfg=material_cfg, **kwargs)
    
    if model == "blinn_phong":
        return shade_blinn_phong(mat_cfg=material_cfg, **kwargs)
    
    raise ValueError(f"Unknown material config or Illumination model:{model}")