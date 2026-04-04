#!/usr/bin/env python3
"""Demo script for avatar poses"""
from app.models.avatar_pose import (
    AVATAR_POSES,
    PoseEmotion,
    get_pose_by_id,
    get_poses_by_emotion,
    get_pose_by_emotion_and_intensity,
    list_poses_by_emotion,
)


def print_header(title):
    """Print formatted header"""
    print(f"\n{'=' * 70}")
    print(f"  {title.upper()}")
    print(f"{'=' * 70}\n")


def demo_all_poses():
    """Display all 20 poses"""
    print_header("All Avatar Poses (20 total)")
    
    for i, pose in enumerate(AVATAR_POSES, 1):
        emotion_emoji = {
            "risa": "😄",
            "sorpresa": "😲",
            "sarcasmo": "😏",
            "enojo": "😠",
            "tristeza": "😢",
            "confusión": "😕",
            "neutral": "😐",
            "pensativo": "🤔",
        }.get(pose.emotion, "😶")
        
        print(f"{i:2}. {emotion_emoji} {pose.id:10} | {pose.name:20} | "
              f"Intensity: {pose.intensity:.2f} | {pose.image_path}")


def demo_organized_list():
    """Display poses organized by emotion"""
    print_header("Poses Organized by Emotion")
    list_poses_by_emotion()


def demo_get_by_id():
    """Demo getting a pose by ID"""
    print_header("Get Pose by ID")
    
    test_ids = ["pose_001", "pose_009", "pose_015"]
    
    for pose_id in test_ids:
        pose = get_pose_by_id(pose_id)
        if pose:
            print(f"ID: {pose_id}")
            print(f"  Name: {pose.name}")
            print(f"  Emotion: {pose.emotion}")
            print(f"  Intensity: {pose.intensity}")
            print(f"  Image: {pose.image_path}")
            print()


def demo_get_by_emotion():
    """Demo getting poses by emotion"""
    print_header("Get Poses by Emotion")
    
    emotions = ["risa", "enojo", "tristeza"]
    
    for emotion in emotions:
        poses = get_poses_by_emotion(emotion)
        print(f"{emotion.upper()}: {len(poses)} pose(s)")
        for pose in poses:
            print(f"  - {pose.id}: {pose.name} (intensity: {pose.intensity})")
        print()


def demo_find_by_emotion_intensity():
    """Demo finding pose by emotion and intensity"""
    print_header("Find Pose by Emotion and Intensity")
    
    test_cases = [
        ("risa", 0.3),
        ("risa", 0.8),
        ("enojo", 0.5),
        ("tristeza", 0.9),
        ("confusión", 0.6),
    ]
    
    for emotion, intensity in test_cases:
        pose = get_pose_by_emotion_and_intensity(emotion, intensity)
        if pose:
            print(f"Emotion: {emotion}, Requested Intensity: {intensity}")
            print(f"  → Found: {pose.id} ({pose.name})")
            print(f"  → Actual Intensity: {pose.intensity}")
        else:
            print(f"No pose found for {emotion} with intensity {intensity}")
        print()


def demo_convert_to_dict():
    """Demo converting pose to dictionary"""
    print_header("Convert Pose to Dictionary")
    
    pose = get_pose_by_id("pose_003")
    if pose:
        print("Original object:")
        print(f"  {pose}")
        print("\nAs dictionary:")
        import json
        print(json.dumps(pose.to_dict(), indent=2))


def demo_data_structure():
    """Show data structure info"""
    print_header("Data Structure Information")
    
    print(f"Total poses: {len(AVATAR_POSES)}")
    
    # Count by emotion
    emotion_counts = {}
    for pose in AVATAR_POSES:
        emotion_counts[pose.emotion] = emotion_counts.get(pose.emotion, 0) + 1
    
    print("\nBreakdown by emotion:")
    for emotion in sorted(emotion_counts.keys()):
        count = emotion_counts[emotion]
        print(f"  • {emotion:15} : {count} pose(s)")
    
    print("\nIntensity range:")
    intensities = [pose.intensity for pose in AVATAR_POSES]
    print(f"  • Min: {min(intensities)}")
    print(f"  • Max: {max(intensities)}")
    print(f"  • Average: {sum(intensities) / len(intensities):.2f}")


def main():
    """Run demo"""
    print("\n" + "=" * 70)
    print("  AVATAR POSES - DEMO")
    print("=" * 70)
    
    demo_data_structure()
    demo_all_poses()
    demo_organized_list()
    demo_get_by_id()
    demo_get_by_emotion()
    demo_find_by_emotion_intensity()
    demo_convert_to_dict()
    
    print("\n" + "=" * 70)
    print("  USAGE EXAMPLES")
    print("=" * 70)
    
    print("""
from app.models.avatar_pose import (
    AVATAR_POSES,
    get_pose_by_id,
    get_poses_by_emotion,
    get_pose_by_emotion_and_intensity,
)

# Get all poses
all_poses = AVATAR_POSES
print(len(all_poses))  # 20

# Get specific pose
pose = get_pose_by_id("pose_001")
print(pose.name)  # "Sonrisa suave"

# Get poses for an emotion
funny_poses = get_poses_by_emotion("risa")
print(len(funny_poses))  # 3

# Find best pose for emotion + intensity
best_pose = get_pose_by_emotion_and_intensity("enojo", 0.5)
print(best_pose.image_path)  # "/avatars/poses/enojo_medio.png"

# Convert to dict
pose_dict = pose.to_dict()
print(pose_dict["emotion"])  # "risa"
    """)
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
