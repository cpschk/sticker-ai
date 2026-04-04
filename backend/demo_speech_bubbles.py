#!/usr/bin/env python3
"""Demo script for speech bubble image manipulation"""
from PIL import Image, ImageDraw
import os
from app.services.image_manipulation import (
    add_speech_bubble,
    ImageWithSpeechBubble,
    SpeechBubbleStyle
)


def print_header(title):
    """Print formatted header"""
    print(f"\n{'=' * 80}")
    print(f"  {title.upper()}")
    print(f"{'=' * 80}\n")


def create_test_image(filename: str, width: int = 400, height: int = 400):
    """Create a simple test avatar image"""
    # Create a simple avatar (circle with gradient)
    image = Image.new("RGB", (width, height), color=(200, 200, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    
    # Draw a simple avatar face
    # Head
    draw.ellipse(
        [(width//2 - 80, height//2 - 100), (width//2 + 80, height//2 - 20)],
        fill=(255, 200, 150),
        outline=(0, 0, 0),
        width=2
    )
    
    # Eyes
    draw.ellipse(
        [(width//2 - 40, height//2 - 60), (width//2 - 20, height//2 - 40)],
        fill=(0, 0, 0)
    )
    draw.ellipse(
        [(width//2 + 20, height//2 - 60), (width//2 + 40, height//2 - 40)],
        fill=(0, 0, 0)
    )
    
    # Smile
    draw.arc(
        [(width//2 - 30, height//2 - 30), (width//2 + 30, height//2 - 10)],
        0, 180,
        fill=(0, 0, 0),
        width=3
    )
    
    # Body
    draw.rectangle(
        [(width//2 - 50, height//2 + 20), (width//2 + 50, height//2 + 150)],
        fill=(100, 100, 200),
        outline=(0, 0, 0),
        width=2
    )
    
    image.save(filename)
    print(f"✓ Test image created: {filename}")
    return filename


def demo_basic_speech_bubble():
    """Demo basic speech bubble"""
    print_header("Demo 1: Basic Speech Bubble")
    
    # Create test image
    test_image = "test_avatar.png"
    if not os.path.exists(test_image):
        create_test_image(test_image)
    
    # Add speech bubble
    output = "output_basic_bubble.png"
    img = add_speech_bubble(
        test_image,
        "¡Hola! ¿Cómo estás?",
        output_path=output,
        bubble_position="top"
    )
    
    print(f"✓ Basic speech bubble created")
    print(f"  Input: {test_image}")
    print(f"  Output: {output}")
    print(f"  Size: {img.size}")


def demo_custom_style():
    """Demo speech bubble with custom style"""
    print_header("Demo 2: Custom Style Speech Bubble")
    
    test_image = "test_avatar.png"
    if not os.path.exists(test_image):
        create_test_image(test_image)
    
    # Define custom style
    style = SpeechBubbleStyle(
        bubble_color=(255, 220, 100),      # Yellow bubble
        text_color=(0, 0, 0),               # Black text
        border_color=(255, 100, 0),         # Orange border
        border_width=3,
        padding=20,
        corner_radius=20,
        tail_size=20,
        tail_position="bottom-left"
    )
    
    # Add speech bubble with custom style
    output = "output_custom_style.png"
    img = ImageWithSpeechBubble.add_speech_bubble(
        test_image,
        "Este es un globo\ncon estilo personalizado",
        output_path=output,
        style=style,
        bubble_position="top"
    )
    
    print(f"✓ Custom style speech bubble created")
    print(f"  Bubble color: RGB{style.bubble_color}")
    print(f"  Border color: RGB{style.border_color}")
    print(f"  Border width: {style.border_width}px")


def demo_bottom_position():
    """Demo speech bubble at bottom"""
    print_header("Demo 3: Bottom Positioned Bubble")
    
    test_image = "test_avatar.png"
    if not os.path.exists(test_image):
        create_test_image(test_image)
    
    output = "output_bottom_bubble.png"
    img = add_speech_bubble(
        test_image,
        "¡Estoy en la parte inferior!",
        output_path=output,
        bubble_position="bottom"
    )
    
    print(f"✓ Bottom positioned speech bubble created")
    print(f"  Output: {output}")


def demo_different_styles():
    """Demo different speech bubble styles"""
    print_header("Demo 4: Multiple Different Styles")
    
    test_image = "test_avatar.png"
    if not os.path.exists(test_image):
        create_test_image(test_image)
    
    styles_config = [
        {
            "name": "Happy (Yellow)",
            "style": SpeechBubbleStyle(
                bubble_color=(255, 255, 100),
                text_color=(0, 0, 0),
                border_color=(200, 150, 0),
                border_width=2
            ),
            "output": "output_happy_bubble.png"
        },
        {
            "name": "Angry (Red)",
            "style": SpeechBubbleStyle(
                bubble_color=(255, 150, 150),
                text_color=(139, 0, 0),
                border_color=(200, 0, 0),
                border_width=3
            ),
            "output": "output_angry_bubble.png"
        },
        {
            "name": "Sad (Blue)",
            "style": SpeechBubbleStyle(
                bubble_color=(150, 200, 255),
                text_color=(0, 0, 100),
                border_color=(0, 0, 200),
                border_width=2
            ),
            "output": "output_sad_bubble.png"
        },
        {
            "name": "Calm (Green)",
            "style": SpeechBubbleStyle(
                bubble_color=(150, 255, 150),
                text_color=(0, 100, 0),
                border_color=(0, 150, 0),
                border_width=2
            ),
            "output": "output_calm_bubble.png"
        }
    ]
    
    for config in styles_config:
        texts = {
            "Happy (Yellow)": "¡Estoy muy feliz!",
            "Angry (Red)": "¡Estoy furioso!",
            "Sad (Blue)": "Estoy triste...",
            "Calm (Green)": "Me siento tranquilo"
        }
        
        img = ImageWithSpeechBubble.add_speech_bubble(
            test_image,
            texts[config["name"]],
            output_path=config["output"],
            style=config["style"],
            bubble_position="top"
        )
        
        print(f"  ✓ {config['name']:20} → {config['output']}")


def demo_long_text():
    """Demo speech bubble with long text (auto-wrap)"""
    print_header("Demo 5: Long Text Auto-Wrap")
    
    test_image = "test_avatar.png"
    if not os.path.exists(test_image):
        create_test_image(test_image)
    
    long_text = """Este es un texto más largo que se envolverá automáticamente 
en múltiples líneas para caber dentro del globo de diálogo. 
¡Funciona perfectamente!"""
    
    output = "output_long_text.png"
    img = add_speech_bubble(
        test_image,
        long_text,
        output_path=output,
        bubble_position="top"
    )
    
    print(f"✓ Long text speech bubble created")
    print(f"  Text length: {len(long_text)} chars")
    print(f"  Lines: {len(long_text.split(chr(10)))}")


def demo_different_font_sizes():
    """Demo speech bubbles with different font sizes"""
    print_header("Demo 6: Different Font Sizes")
    
    test_image = "test_avatar.png"
    if not os.path.exists(test_image):
        create_test_image(test_image)
    
    font_sizes = [12, 16, 20, 24, 28]
    
    for size in font_sizes:
        output = f"output_fontsize_{size}.png"
        img = add_speech_bubble(
            test_image,
            f"Tamaño {size}",
            output_path=output,
            bubble_position="top",
            font_size=size
        )
        print(f"  ✓ Font size {size}px → {output}")


def demo_integration_with_emotion():
    """Demo: Speech bubble based on emotion"""
    print_header("Demo 7: Integration with Emotion Detection")
    
    from app.services.emotion_detector import detect_emotion
    from app.services.avatar_service import select_best_pose
    
    test_image = "test_avatar.png"
    if not os.path.exists(test_image):
        create_test_image(test_image)
    
    # Examples with different emotions
    test_cases = [
        ("jajaja esto es hilariante!!!", "happy"),
        ("¡¡¡estoy muy enojado!!!", "angry"),
        ("me siento triste", "sad"),
        ("no puede ser increíble!", "surprised"),
    ]
    
    emotion_styles = {
        "happy": SpeechBubbleStyle(
            bubble_color=(255, 255, 100),
            text_color=(0, 0, 0),
            border_color=(200, 150, 0),
            border_width=2
        ),
        "angry": SpeechBubbleStyle(
            bubble_color=(255, 150, 150),
            text_color=(139, 0, 0),
            border_color=(200, 0, 0),
            border_width=3
        ),
        "sad": SpeechBubbleStyle(
            bubble_color=(150, 200, 255),
            text_color=(0, 0, 100),
            border_color=(0, 0, 200),
            border_width=2
        ),
        "surprised": SpeechBubbleStyle(
            bubble_color=(255, 180, 255),
            text_color=(100, 0, 100),
            border_color=(150, 0, 150),
            border_width=2
        )
    }
    
    for text, emotion_label in test_cases:
        # Detect emotion
        emotion_result = detect_emotion(text)
        emotion = emotion_result.get("emotion", emotion_label)
        
        # Get appropriate style
        style = emotion_styles.get(emotion_label, emotion_styles["happy"])
        
        # Create output
        output = f"output_emotion_{emotion_label}.png"
        img = ImageWithSpeechBubble.add_speech_bubble(
            test_image,
            text,
            output_path=output,
            style=style,
            bubble_position="top"
        )
        
        print(f"  ✓ Emotion: {emotion_label:10} → {output}")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("  IMAGE MANIPULATION - SPEECH BUBBLES DEMO")
    print("=" * 80)
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Run demos
    demo_basic_speech_bubble()
    demo_custom_style()
    demo_bottom_position()
    demo_different_styles()
    demo_long_text()
    demo_different_font_sizes()
    
    try:
        demo_integration_with_emotion()
    except Exception as e:
        print(f"⚠️  Emotion demo skipped: {e}")
    
    # Summary
    print_header("Summary")
    
    print("""
✅ Features Demonstrated:
   • Basic speech bubble creation
   • Custom colors and styles
   • Top/bottom positioning
   • Multiple style variations
   • Automatic text wrapping
   • Different font sizes
   • Integration with emotion detection

💾 Generated Files:
   • output_basic_bubble.png
   • output_custom_style.png
   • output_bottom_bubble.png
   • output_happy/angry/sad/calm_bubble.png
   • output_long_text.png
   • output_fontsize_*.png
   • output_emotion_*.png

🎨 Usage Example:
   
   from app.services.image_manipulation import add_speech_bubble
   
   # Simple usage
   img = add_speech_bubble("avatar.png", "Hola!")
   img.save("avatar_speaking.png")
   
   # With custom style
   from app.services.image_manipulation import SpeechBubbleStyle
   
   style = SpeechBubbleStyle(
       bubble_color=(255, 200, 100),
       border_color=(200, 100, 0),
       border_width=3
   )
   
   img = add_speech_bubble(
       "avatar.png",
       "Texto personalizado",
       style=style
   )
    """)
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
