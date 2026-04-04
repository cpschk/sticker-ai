#!/usr/bin/env python3
"""Demo script for avatar pose selection service"""
from app.services.avatar_service import (
    AvatarPoseSelectionService,
    select_best_pose,
)
from app.models.avatar_pose import AVATAR_POSES, get_poses_by_emotion


def print_header(title):
    """Print formatted header"""
    print(f"\n{'=' * 70}")
    print(f"  {title.upper()}")
    print(f"{'=' * 70}\n")


def demo_basic_selection():
    """Demo basic pose selection"""
    print_header("Basic Pose Selection by Emotion")
    
    emotions = ["risa", "enojo", "tristeza", "sorpresa", "confusión", "sarcasmo"]
    
    for emotion in emotions:
        # Select 5 random poses for the same emotion
        print(f"\nEmotion: {emotion.upper()}")
        print("Selecting 5 random poses:")
        
        for i in range(5):
            pose = select_best_pose(emotion)
            if pose:
                print(f"  {i+1}. {pose.id:10} | {pose.name:20} | intensity: {pose.intensity:.2f}")
            else:
                print(f"  ❌ No pose found for {emotion}")


def demo_intensity_preference():
    """Demo selecting poses with intensity preference"""
    print_header("Pose Selection with Intensity Preference")
    
    test_cases = [
        ("risa", 0.3, "Low intensity laugh"),
        ("risa", 0.6, "Medium intensity laugh"),
        ("risa", 0.9, "High intensity laugh"),
        ("enojo", 0.2, "Slight annoyance"),
        ("enojo", 0.7, "Moderate anger"),
        ("enojo", 1.0, "Extreme fury"),
        ("tristeza", 0.4, "Melancholy"),
        ("tristeza", 0.8, "Deep sadness"),
    ]
    
    for emotion, preferred_intensity, description in test_cases:
        pose = select_best_pose(emotion, prefer_intensity=preferred_intensity)
        
        if pose:
            print(f"\n{description}")
            print(f"  Requested intensity: {preferred_intensity:.2f}")
            print(f"  Selected pose: {pose.id} - {pose.name}")
            print(f"  Actual intensity: {pose.intensity:.2f}")
            print(f"  Delta: {abs(pose.intensity - preferred_intensity):.2f}")
        else:
            print(f"\n❌ No pose found for {emotion}")


def demo_weighted_selection():
    """Demo weighted selection (prefers medium intensity)"""
    print_header("Weighted Pose Selection (Medium Intensity Preferred)")
    
    emotions = ["risa", "enojo", "tristeza"]
    
    for emotion in emotions:
        print(f"\n{emotion.upper()} - Selecting 10 poses (medium intensity preferred)")
        
        intensity_count = {"low": 0, "medium": 0, "high": 0}
        
        for _ in range(10):
            pose = AvatarPoseSelectionService.select_best_pose_weighted(emotion)
            
            if pose:
                if 0.4 <= pose.intensity <= 0.7:
                    intensity_count["medium"] += 1
                elif pose.intensity < 0.4:
                    intensity_count["low"] += 1
                else:
                    intensity_count["high"] += 1
        
        print(f"  Results:")
        print(f"    • Low intensity (0.0-0.39): {intensity_count['low']} times")
        print(f"    • Medium intensity (0.4-0.7): {intensity_count['medium']} times ✓ (preferred)")
        print(f"    • High intensity (0.71-1.0): {intensity_count['high']} times")


def demo_intensity_range():
    """Demo selecting poses within intensity range"""
    print_header("Pose Selection by Intensity Range")
    
    test_cases = [
        ("risa", 0.0, 0.5, "Calm laugh poses"),
        ("risa", 0.5, 1.0, "Intense laugh poses"),
        ("enojo", 0.0, 0.4, "Calm anger poses"),
        ("enojo", 0.6, 1.0, "Intense anger poses"),
        ("tristeza", 0.0, 0.5, "Mild sadness poses"),
        ("tristeza", 0.5, 1.0, "Deep sadness poses"),
    ]
    
    for emotion, min_int, max_int, description in test_cases:
        print(f"\n{description}")
        print(f"  Emotion: {emotion}, Intensity range: {min_int}-{max_int}")
        
        # Select multiple times to show variety
        poses = []
        for _ in range(3):
            pose = AvatarPoseSelectionService.select_pose_by_intensity_range(
                emotion,
                min_intensity=min_int,
                max_intensity=max_int
            )
            if pose:
                poses.append(pose)
        
        if poses:
            for pose in poses:
                print(f"    • {pose.id}: {pose.name} (intensity: {pose.intensity:.2f})")
        else:
            print(f"    ❌ No poses in this range")


def demo_animation_sequence():
    """Demo selecting pose sequences for animation"""
    print_header("Animation Sequence Selection")
    
    emotions = ["risa", "enojo", "sorpresa"]
    
    for emotion in emotions:
        print(f"\n{emotion.upper()} animation sequence:")
        
        sequence = AvatarPoseSelectionService.select_pose_sequence(emotion, count=3)
        
        if sequence:
            print(f"  Frame sequence (3 poses):")
            for i, pose in enumerate(sequence[:3], 1):
                print(f"    Frame {i}: {pose.id} - {pose.name}")
                print(f"      Image: {pose.image_path}")


def demo_with_emotion_detection():
    """Demo integration with emotion detection"""
    print_header("Integration with Emotion Detection")
    
    # Simulate emotion detection
    test_texts = [
        ("jajaja esto es hilariante!!!", "expected: high intensity risa"),
        ("no puede ser...", "expected: medium intensity sorpresa"),
        ("¡¡¡estoy furioso!!!", "expected: high intensity enojo"),
        ("me siento mal...", "expected: medium intensity tristeza"),
    ]
    
    from app.services.emotion_detector import detect_emotion
    
    for text, expectation in test_texts:
        print(f"\nText: {text!r}")
        print(f"Note: {expectation}")
        
        # Detect emotion
        emotion_result = detect_emotion(text)
        
        if emotion_result["emotion"]:
            print(f"Detected emotion: {emotion_result['emotion']}")
            print(f"Detected intensity: {emotion_result['intensity']:.2f}")
            
            # Select pose based on detected emotion and intensity
            pose = select_best_pose(
                emotion_result["emotion"],
                prefer_intensity=emotion_result["intensity"]
            )
            
            if pose:
                print(f"\n✅ Selected Pose:")
                print(f"   ID: {pose.id}")
                print(f"   Name: {pose.name}")
                print(f"   Intensity: {pose.intensity:.2f}")
                print(f"   Image: {pose.image_path}")
        else:
            print("No emotion detected")


def demo_available_poses():
    """Show available poses per emotion"""
    print_header("Available Poses per Emotion")
    
    from app.models.avatar_pose import PoseEmotion
    
    for emotion in PoseEmotion:
        poses = get_poses_by_emotion(emotion.value)
        print(f"\n{emotion.value.upper()}: {len(poses)} pose(s)")
        
        for pose in sorted(poses, key=lambda p: p.intensity):
            print(f"  • {pose.id}: {pose.name:20} (intensity: {pose.intensity:.2f})")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  AVATAR POSE SELECTION SERVICE - DEMO")
    print("=" * 70)
    
    demo_available_poses()
    demo_basic_selection()
    demo_intensity_preference()
    demo_weighted_selection()
    demo_intensity_range()
    demo_animation_sequence()
    demo_with_emotion_detection()
    
    print("\n" + "=" * 70)
    print("  USAGE EXAMPLES")
    print("=" * 70)
    
    print("""
# Import
from app.services.avatar_service import select_best_pose, AvatarPoseSelectionService

# Basic usage - select random pose for emotion
pose = select_best_pose("risa")
print(pose.image_path)  # /avatars/poses/risa_media.png

# With intensity preference
pose = select_best_pose("enojo", prefer_intensity=0.5)
print(pose.name)  # "Enojo moderado"

# Weighted selection (prefers medium intensity)
pose = AvatarPoseSelectionService.select_best_pose_weighted("tristeza")
print(pose.intensity)  # Usually between 0.3-0.7

# Select by intensity range
pose = AvatarPoseSelectionService.select_pose_by_intensity_range(
    "risa",
    min_intensity=0.5,
    max_intensity=1.0
)
print(pose.name)  # High intensity laugh

# Create animation sequence
sequence = AvatarPoseSelectionService.select_pose_sequence("sorpresa", count=3)
for pose in sequence:
    render_frame(pose.image_path)

# Integration with emotion detection
from app.services.emotion_detector import detect_emotion

emotion_result = detect_emotion("jajaja no puede ser!!!")
pose = select_best_pose(
    emotion_result["emotion"],
    prefer_intensity=emotion_result["intensity"]
)
print(f"Selected: {pose.image_path}")
    """)
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
