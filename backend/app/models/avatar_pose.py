"""Avatar pose models"""
from dataclasses import dataclass
from typing import List
from enum import Enum


class PoseEmotion(str, Enum):
    """Available emotions for poses"""
    RISA = "risa"
    SORPRESA = "sorpresa"
    SARCASMO = "sarcasmo"
    ENOJO = "enojo"
    TRISTEZA = "tristeza"
    CONFUSIÓN = "confusión"
    NEUTRAL = "neutral"
    PENSATIVO = "pensativo"


@dataclass
class AvatarPose:
    """Represents an avatar pose"""
    id: str
    emotion: str
    intensity: float
    image_path: str
    name: str = ""
    description: str = ""
    
    def __post_init__(self):
        """Validate intensity is between 0 and 1"""
        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError(f"Intensity must be between 0.0 and 1.0, got {self.intensity}")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "emotion": self.emotion,
            "intensity": self.intensity,
            "image_path": self.image_path,
            "name": self.name,
            "description": self.description,
        }


# Mock data: 20 avatar poses with different emotions
AVATAR_POSES: List[AvatarPose] = [
    # RISA (Laughter) - 3 poses
    AvatarPose(
        id="pose_001",
        emotion=PoseEmotion.RISA,
        intensity=0.5,
        image_path="/avatars/poses/risa_baja.png",
        name="Sonrisa suave",
        description="Avatar with a gentle smile"
    ),
    AvatarPose(
        id="pose_002",
        emotion=PoseEmotion.RISA,
        intensity=0.75,
        image_path="/avatars/poses/risa_media.png",
        name="Risa media",
        description="Avatar laughing moderately"
    ),
    AvatarPose(
        id="pose_003",
        emotion=PoseEmotion.RISA,
        intensity=1.0,
        image_path="/avatars/poses/risa_alta.png",
        name="Risa carcajada",
        description="Avatar laughing hard"
    ),
    
    # SORPRESA (Surprise) - 3 poses
    AvatarPose(
        id="pose_004",
        emotion=PoseEmotion.SORPRESA,
        intensity=0.4,
        image_path="/avatars/poses/sorpresa_baja.png",
        name="Sorpresa ligera",
        description="Avatar mildly surprised"
    ),
    AvatarPose(
        id="pose_005",
        emotion=PoseEmotion.SORPRESA,
        intensity=0.7,
        image_path="/avatars/poses/sorpresa_media.png",
        name="Sorpresa moderada",
        description="Avatar moderately surprised"
    ),
    AvatarPose(
        id="pose_006",
        emotion=PoseEmotion.SORPRESA,
        intensity=1.0,
        image_path="/avatars/poses/sorpresa_alta.png",
        name="Sorpresa extrema",
        description="Avatar shocked"
    ),
    
    # ENOJO (Anger) - 3 poses
    AvatarPose(
        id="pose_007",
        emotion=PoseEmotion.ENOJO,
        intensity=0.3,
        image_path="/avatars/poses/enojo_bajo.png",
        name="Ligero fastidio",
        description="Avatar slightly annoyed"
    ),
    AvatarPose(
        id="pose_008",
        emotion=PoseEmotion.ENOJO,
        intensity=0.65,
        image_path="/avatars/poses/enojo_medio.png",
        name="Enojo moderado",
        description="Avatar moderately angry"
    ),
    AvatarPose(
        id="pose_009",
        emotion=PoseEmotion.ENOJO,
        intensity=1.0,
        image_path="/avatars/poses/enojo_alto.png",
        name="Furia extrema",
        description="Avatar furious"
    ),
    
    # TRISTEZA (Sadness) - 3 poses
    AvatarPose(
        id="pose_010",
        emotion=PoseEmotion.TRISTEZA,
        intensity=0.35,
        image_path="/avatars/poses/tristeza_baja.png",
        name="Melancolía",
        description="Avatar wistful"
    ),
    AvatarPose(
        id="pose_011",
        emotion=PoseEmotion.TRISTEZA,
        intensity=0.7,
        image_path="/avatars/poses/tristeza_media.png",
        name="Tristeza moderada",
        description="Avatar sad"
    ),
    AvatarPose(
        id="pose_012",
        emotion=PoseEmotion.TRISTEZA,
        intensity=1.0,
        image_path="/avatars/poses/tristeza_alta.png",
        name="Dolor profundo",
        description="Avatar devastated"
    ),
    
    # CONFUSIÓN (Confusion) - 2 poses
    AvatarPose(
        id="pose_013",
        emotion=PoseEmotion.CONFUSIÓN,
        intensity=0.45,
        image_path="/avatars/poses/confusion_baja.png",
        name="Duda ligera",
        description="Avatar slightly confused"
    ),
    AvatarPose(
        id="pose_014",
        emotion=PoseEmotion.CONFUSIÓN,
        intensity=0.85,
        image_path="/avatars/poses/confusion_alta.png",
        name="Confusión total",
        description="Avatar very confused"
    ),
    
    # SARCASMO (Sarcasm) - 2 poses
    AvatarPose(
        id="pose_015",
        emotion=PoseEmotion.SARCASMO,
        intensity=0.5,
        image_path="/avatars/poses/sarcasmo_bajo.png",
        name="Ironía sutil",
        description="Avatar with subtle sarcasm"
    ),
    AvatarPose(
        id="pose_016",
        emotion=PoseEmotion.SARCASMO,
        intensity=0.9,
        image_path="/avatars/poses/sarcasmo_alto.png",
        name="Sarcasmo obvio",
        description="Avatar dripping with sarcasm"
    ),
    
    # NEUTRAL (Neutral) - 2 poses
    AvatarPose(
        id="pose_017",
        emotion=PoseEmotion.NEUTRAL,
        intensity=0.0,
        image_path="/avatars/poses/neutral_serio.png",
        name="Expresión seria",
        description="Avatar with serious expression"
    ),
    AvatarPose(
        id="pose_018",
        emotion=PoseEmotion.NEUTRAL,
        intensity=0.2,
        image_path="/avatars/poses/neutral_relajado.png",
        name="Expresión relajada",
        description="Avatar relaxed"
    ),
    
    # PENSATIVO (Thoughtful) - 2 poses
    AvatarPose(
        id="pose_019",
        emotion=PoseEmotion.PENSATIVO,
        intensity=0.4,
        image_path="/avatars/poses/pensativo_ligero.png",
        name="Pensamiento leve",
        description="Avatar in light thought"
    ),
    AvatarPose(
        id="pose_020",
        emotion=PoseEmotion.PENSATIVO,
        intensity=0.8,
        image_path="/avatars/poses/pensativo_profundo.png",
        name="Reflexión profunda",
        description="Avatar in deep thought"
    ),
]


def get_pose_by_id(pose_id: str) -> AvatarPose | None:
    """Get a pose by its ID"""
    for pose in AVATAR_POSES:
        if pose.id == pose_id:
            return pose
    return None


def get_poses_by_emotion(emotion: str) -> List[AvatarPose]:
    """Get all poses for a specific emotion"""
    return [pose for pose in AVATAR_POSES if pose.emotion == emotion]


def get_pose_by_emotion_and_intensity(emotion: str, intensity: float) -> AvatarPose | None:
    """Get closest pose for emotion and intensity"""
    poses = get_poses_by_emotion(emotion)
    if not poses:
        return None
    
    # Find pose with closest intensity
    return min(poses, key=lambda p: abs(p.intensity - intensity))


def get_random_pose() -> AvatarPose:
    """Get a random pose"""
    import random
    return random.choice(AVATAR_POSES)


def list_poses_by_emotion():
    """Print organized list of poses by emotion"""
    emotions_dict = {}
    
    for pose in AVATAR_POSES:
        if pose.emotion not in emotions_dict:
            emotions_dict[pose.emotion] = []
        emotions_dict[pose.emotion].append(pose)
    
    for emotion, poses in sorted(emotions_dict.items()):
        print(f"\n{emotion.upper()}:")
        for pose in poses:
            print(f"  - {pose.id}: {pose.name} (intensity: {pose.intensity})")
