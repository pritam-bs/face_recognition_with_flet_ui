from dataclasses import dataclass
from typing import List
import numpy as np
from typing import Optional


@dataclass
class Person:
    name: str
    frame_list: Optional[List[np.ndarray]]
    face_image_list: Optional[List[np.ndarray]]
    bbs_list: Optional[List[np.ndarray]]
    embeddings: Optional[List[np.ndarray]]
    clusters: Optional[np.ndarray]

    def __init__(self, name, frame_list, face_image_list=None, bbs_list=None, embeddings=None, clusters=None):
        self.name = name
        self.frame_list = frame_list if frame_list is not None else []
        self.face_image_list = face_image_list if face_image_list is not None else []
        self.bbs_list = bbs_list if bbs_list is not None else []
        self.embeddings = embeddings if embeddings is not None else []
        self.clusters = clusters if clusters is not None else None
