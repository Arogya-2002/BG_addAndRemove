from dataclasses import dataclass

@dataclass
class RemoveBgArtifact:
    rmbg_img_path:str

@dataclass
class ChangeBgArtifact:
    ch_bg_img_path: str
