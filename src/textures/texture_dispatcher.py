def apply_texture(material_cfg, **kwargs):
    texture = material_cfg.get("texture")

    if texture == "checkerboard":
        from src.textures.checkerboard import checkerboard_texture
        material_cfg["diffuse_color"] = checkerboard_texture(mat_cfg=material_cfg, **kwargs)
    
    elif texture == "bricks":
        from src.textures.brick import brick_texture
        material_cfg["diffuse_color"] = brick_texture(mat_cfg=material_cfg, **kwargs)

    return material_cfg