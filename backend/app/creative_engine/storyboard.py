from __future__ import annotations


def generate_storyboard(script: dict) -> list[dict]:
    storyboard = []
    emotions = ["curiosity", "frustration", "surprise", "satisfaction", "decision"]
    overlays = ["Wait for it...", "This was the annoying part", "Tiny fix", "Before / after", "Worth testing?"]
    for index, scene in enumerate(script["scenes"]):
        storyboard.append(
            {
                "scene": scene["scene"],
                "duration": scene["time"],
                "camera": scene["camera"],
                "action": scene["action"],
                "emotion": emotions[index],
                "text_overlay": overlays[index],
            }
        )
    return storyboard
