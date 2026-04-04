"""Avatar pose selection service"""
import random
from typing import List, Optional
from app.models.avatar_pose import AvatarPose, AVATAR_POSES


class AvatarPoseSelectionService:
    """Service for selecting avatar poses based on emotions"""
    
    @staticmethod
    def select_best_pose(
        emotion: str,
        poses: Optional[List[AvatarPose]] = None,
        prefer_intensity: Optional[float] = None
    ) -> Optional[AvatarPose]:
        """
        Select the best pose for a detected emotion
        
        Args:
            emotion: Detected emotion (e.g., "risa", "enojo")
            poses: List of available poses (uses AVATAR_POSES mock data if None)
            prefer_intensity: Optional preferred intensity (0.0-1.0)
                            If provided, selects pose closest to this intensity
        
        Returns:
            Selected AvatarPose or None if no matching pose found
            
        Example:
            >>> emotion_result = detect_emotion("jajaja!")
            >>> pose = select_best_pose(emotion_result["emotion"])
            >>> print(pose.image_path)  # /avatars/poses/risa_alta.png
        """
        if poses is None:
            poses = AVATAR_POSES
        
        # Filter poses by emotion
        matching_poses = [pose for pose in poses if pose.emotion == emotion]
        
        if not matching_poses:
            return None
        
        # If no intensity preference, return random pose
        if prefer_intensity is None:
            return random.choice(matching_poses)
        
        # Find pose closest to preferred intensity
        closest_pose = min(
            matching_poses,
            key=lambda p: abs(p.intensity - prefer_intensity)
        )
        
        return closest_pose
    
    @staticmethod
    def select_best_pose_weighted(
        emotion: str,
        poses: Optional[List[AvatarPose]] = None
    ) -> Optional[AvatarPose]:
        """
        Select pose with weighted probability favoring medium intensity
        
        Medium intensity poses (0.4-0.7) are more likely to be selected
        for more balanced expressions.
        
        Args:
            emotion: Detected emotion
            poses: List of available poses
            
        Returns:
            Selected AvatarPose with weighted distribution
        """
        if poses is None:
            poses = AVATAR_POSES
        
        matching_poses = [pose for pose in poses if pose.emotion == emotion]
        
        if not matching_poses:
            return None
        
        if len(matching_poses) == 1:
            return matching_poses[0]
        
        # Calculate weights based on intensity
        weights = []
        for pose in matching_poses:
            if 0.4 <= pose.intensity <= 0.7:
                # Medium intensity: double weight
                weight = 2.0
            else:
                # Low or high intensity: normal weight
                weight = 1.0
            weights.append(weight)
        
        # Select with weighted probabilities
        return random.choices(matching_poses, weights=weights, k=1)[0]
    
    @staticmethod
    def select_pose_by_intensity_range(
        emotion: str,
        min_intensity: float = 0.0,
        max_intensity: float = 1.0,
        poses: Optional[List[AvatarPose]] = None
    ) -> Optional[AvatarPose]:
        """
        Select random pose within an intensity range
        
        Args:
            emotion: Detected emotion
            min_intensity: Minimum intensity (0.0-1.0)
            max_intensity: Maximum intensity (0.0-1.0)
            poses: List of available poses
            
        Returns:
            Selected AvatarPose within intensity range or None
            
        Example:
            # Select a "calm" sadness pose
            pose = select_pose_by_intensity_range(
                "tristeza",
                min_intensity=0.0,
                max_intensity=0.5
            )
        """
        if poses is None:
            poses = AVATAR_POSES
        
        matching_poses = [
            pose for pose in poses
            if pose.emotion == emotion
            and min_intensity <= pose.intensity <= max_intensity
        ]
        
        if not matching_poses:
            return None
        
        return random.choice(matching_poses)
    
    @staticmethod
    def select_pose_sequence(
        emotion: str,
        count: int = 3,
        poses: Optional[List[AvatarPose]] = None
    ) -> List[AvatarPose]:
        """
        Select a sequence of different poses for animation
        
        Useful for creating animations with pose transitions
        
        Args:
            emotion: Detected emotion
            count: Number of poses to select (max is available poses)
            poses: List of available poses
            
        Returns:
            List of selected AvatarPoses
            
        Example:
            # Create animation sequence
            sequence = select_pose_sequence("risa", count=3)
            for pose in sequence:
                render_frame(pose.image_path)
        """
        if poses is None:
            poses = AVATAR_POSES
        
        matching_poses = [pose for pose in poses if pose.emotion == emotion]
        
        if not matching_poses:
            return []
        
        # Return unique poses if possible, otherwise repeat
        return random.sample(
            matching_poses,
            k=min(count, len(matching_poses))
        ) * (count // len(matching_poses) + 1)


def select_best_pose(
    emotion: str,
    poses: Optional[List[AvatarPose]] = None,
    prefer_intensity: Optional[float] = None
) -> Optional[AvatarPose]:
    """
    Convenience function to select the best pose for an emotion
    
    Args:
        emotion: Detected emotion
        poses: List of available poses (optional)
        prefer_intensity: Preferred intensity level (optional)
    
    Returns:
        Selected AvatarPose or None
        
    Example:
        >>> from app.services.avatar_service import select_best_pose
        >>> pose = select_best_pose("risa")
        >>> print(pose.name)
    """
    return AvatarPoseSelectionService.select_best_pose(emotion, poses, prefer_intensity)
