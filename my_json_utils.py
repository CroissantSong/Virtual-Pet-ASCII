import json
import os

def create_pet_ascii_art_json(filename="pet_ascii_art.json"):
    """
    Creates a JSON file with predefined ASCII art for pets.
    """
    ascii_art_data = {
      "Dog": {
        "idle": [
          "  ^^      _",
          "o'')}____//",
          " `_/      )",
          " (_(_/-(_/ "
        ],
        "feeding": [
          "   @\\/@  🦴",
          "  /`-' )",
          "o'')}___/",
          " `_/--(_",
          " (_(_(_ )"
        ],
        "playing": [
          "  ^^      _ ^",
          "o'')}____//\\ 🎾",
          " `_/      )_) ",
          " (_(_/-(_/  Woof!"
        ],
        "cleaning": [
          "  ^^      _ ",
          "o'')}____// ✨",
          " `_/      ) ",
          " (_(_/-(_/  Sparkle!"
        ],
        "resting": [
          "   .--~~,__",
          " Zzz...' ) )",
          "  `·..--~ /",
          "      //",
          "     ((",
          "      `'"
        ]
      },
      "Cat": {
        "idle": [
          " /\\_/\\",
          "( o.o )",
          " > ^ <",
          " `---'"
        ],
        "feeding": [
          " /\\_/\\",
          "( o.o ) ~ 🐟",
          " > ^ <",
          "  `U'"
        ],
        "playing": [
          " /\\_/\\",
          "( >w< )🐾",
          "o_) (_o--\"~🧶",
          "  `---'"
        ],
        "cleaning": [
          "  /\\_/\\",
          "~( o◡o )~ lick",
          " (> ^ <)ノ",
          "  `---'"
        ],
        "resting": [
          "  .--~~,__",
          ":'- __,'  ~ .zZ",
          "   _.oO",
          "  (_,-)~",
          "    `-"
        ]
      },
      "Bird": {
        "idle": [
          "   _  ",
          " <(o )___",
          "  ( ._> /",
          "   `---' "
        ],
        "feeding": [
          "     _  ",
          " <(o )=--∴",
          "  ( ._> )",
          "   `---' "
        ],
        "playing": [
          "   chirp!",
          "\\\\( ^o^)/",
          "  ( ._> /",
          "   `---' "
        ],
        "cleaning": [
          "     _    ✨",
          " <(~o )~~~",
          "  ( ._> /",
          "   `---' "
        ],
        "resting": [
          "    .--.",
          " Z <(u_u)>",
          " z  (   )/",
          "     `---'"
        ]
      },
      "_default_": {
        "idle": [
          "¯\\_(ツ)_/¯",
          " (No Art)"
        ],
        "feeding": [
          " (...) Yum",
          " (No Art)"
        ],
        "playing": [
          "\\(^_^)/",
          " (No Art)"
        ],
        "cleaning": [
          "✨✨✨",
          " (No Art)"
        ],
        "resting": [
          "Zzz...",
          " (No Art)"
        ]
      }
    }

    try:
        # 获取脚本所在的目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(ascii_art_data, f, ensure_ascii=False, indent=2) # indent=2 for pretty printing
        print(f"Successfully created '{file_path}'")
    except Exception as e:
        print(f"Error creating JSON file '{filename}': {e}")

if __name__ == "__main__":
    create_pet_ascii_art_json()
    # 如果你想指定不同的文件名或路径，可以这样调用：
    # create_pet_ascii_art_json("custom_ascii_pets.json")