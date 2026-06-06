import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from pathlib import Path

CONFETTI_COLORS = ["#ff595e", "#ffca3a", "#6a4c93", "#1982c4", "#8ac926", "#ff6b9d", "#ffffff"]

BG_COLOR   = "#1a1a2e"
GOLD_COLOR = "#e0c040"


def _draw_confetti(ax, n=260, xlim=(-1, 3.6), ylim=(0, 2)):
    xs = [random.uniform(*xlim) for _ in range(n)]
    ys = [random.uniform(*ylim) for _ in range(n)]
    colors = [random.choice(CONFETTI_COLORS) for _ in range(n)]
    sizes  = [random.uniform(10, 60) for _ in range(n)]
    markers = ["*", "o", "s", "D", "^"]
    for x, y, c, s in zip(xs, ys, colors, sizes):
        ax.scatter(x, y, c=c, s=s,
                   marker=random.choice(markers),
                   alpha=random.uniform(0.5, 1.0), zorder=0)


def _draw_medal(ax, x, y, place, color):
    """Draw a colored circle with place number — no emoji, no font issues."""
    ax.add_patch(patches.Circle(
        (x, y), 0.09, facecolor=color, edgecolor="white", linewidth=1.5, zorder=2
    ))
    ax.text(x, y, str(place), ha="center", va="center",
            fontsize=13, fontweight="bold", color="white", zorder=3)


def _draw_robot_img(ax, cx, base_y, img_name):
    script_dir = Path(__file__).resolve().parent
    img_path = script_dir / "bot_imgs" / img_name
    if not img_path.exists():
        print(f"Warning: image not found at {img_path}, using default.")
        img_path = script_dir / "bot_imgs" / "default_bot.png"
    botImg = Image.open(img_path).convert("RGBA")
    orig_w, orig_h = botImg.size
    zoom = min(100 / orig_w, 100 / orig_h)
    im = OffsetImage(botImg, zoom=zoom)
    ab = AnnotationBbox(im, (cx, base_y), xycoords='data',
                        box_alignment=(0.5, 0.0), frameon=False)
    ax.add_artist(ab)
    return base_y + 0.42


def _draw_robot(ax, cx, base_y, bot_name, bot_images):
    """
    bot_images: dict mapping player_name -> image filename in bot_imgs/.
    Falls back to default_bot.png for any name not in the dict.
    """
    img = bot_images.get(bot_name, "default_bot.png")
    return _draw_robot_img(ax, cx, base_y, img)


def draw_podium(standings, output_file="podium.png", bot_images=None):
    """
    standings:  list of (player_name, gold) sorted by gold descending.
    bot_images: dict mapping player_name -> image filename in bot_imgs/.
                Teams not in the dict get the default robot image.
                Example: {"GoldDigger-Bot-Basic": "GoldDiggerBot.png",
                           "NonRandom": "dice.png"}
    """
    if bot_images is None:
        bot_images = {}

    top3 = list(standings[:3])
    while len(top3) < 3:
        top3.append(("—", 0))

    extras = standings[3:]
    n_extras = len(extras)
    right_bound = max(3.6, 2.5 + n_extras * 0.85)

    # Display order: 2nd left, 1st center, 3rd right
    display = [
        (0, top3[1], 0.6, "#a0a0b0", 2),
        (1, top3[0], 1.0, "#c8a822", 1),
        (2, top3[2], 0.4, "#a0634a", 3),
    ]

    fig, ax = plt.subplots(figsize=(10 + n_extras, 6))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(-1, right_bound + 0.3)
    ax.set_ylim(0, 2.0)
    ax.axis("off")
    ax.set_title("Final Results", fontsize=35, fontweight="bold",
                 pad=16, color="#f0f0f0")

    _draw_confetti(ax, xlim=(-1, right_bound + 0.3))

    bar_width = 0.75

    for x, (name, gold), h, color, place in display:
        ax.add_patch(patches.FancyBboxPatch(
            (x - bar_width / 2, 0), bar_width, h,
            boxstyle="round,pad=0.02",
            facecolor=color, edgecolor="white", linewidth=3.5, zorder=1,
        ))
        _draw_medal(ax, x, h / 2.2, place, color)
        robot_top = _draw_robot(ax, x, h, name, bot_images)
        name_size = max(9, 20 - int((len(name) - 6) * 1.4))
        ax.text(x, robot_top - 0.5, name, ha="center", va="center",
                fontsize=name_size, fontweight="bold", color=BG_COLOR, zorder=3)
        ax.text(x, robot_top + 0.15, f"{gold} gold", ha="center", va="center",
                fontsize=10, color=GOLD_COLOR, zorder=3,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=BG_COLOR,
                          edgecolor=GOLD_COLOR, linewidth=1.5))

    # All players beyond 3rd placed dynamically on the floor
    for i, (name, gold) in enumerate(extras):
        x4 = 2.5 + i * 0.85
        robot_top4 = _draw_robot(ax, x4, 0, name, bot_images)
        name_size = max(9, 20 - int((len(name) - 6) * 1.4)) - 2
        ax.text(x4, robot_top4 + 0.12, name, ha="center", va="center",
                fontsize=name_size, fontweight="bold", color="white", zorder=3,
                bbox=dict(boxstyle="round,pad=0.17", facecolor=BG_COLOR,
                          edgecolor="white", linewidth=1.5))
        ax.text(x4, robot_top4 + 0.25, f"{gold} gold", ha="center", va="center",
                fontsize=10, color=GOLD_COLOR, zorder=3,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=BG_COLOR,
                          edgecolor=GOLD_COLOR, linewidth=1.5))

    if extras:
        ax.text(right_bound + 0.2, 0.1, "still showed up", ha="right", va="bottom",
                fontsize=16, color="white", zorder=3,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=BG_COLOR,
                          edgecolor="white", linewidth=1.5))

    plt.tight_layout()
    plt.savefig(output_file, dpi=120, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.show()
    plt.close()
    print(f"Podium saved to {output_file}")


def draw_podium_from_game_info(game, output_file="podium.png", bot_images=None):
    """Draw podium from a single completed Simulator instance."""
    standings = sorted(
        [(p.player_name, game._status[i].gold) for i, p in enumerate(game._players)],
        key=lambda x: x[1], reverse=True
    )
    draw_podium(standings, output_file=output_file, bot_images=bot_images)


def draw_podium_from_multi_round(games, output_file="podium.png", bot_images=None):
    """
    Aggregate gold across multiple Simulator instances and draw a combined podium.
    games: list of completed Simulator instances.
    """
    totals = {}
    for game in games:
        for i, p in enumerate(game._players):
            name = p.player_name
            totals[name] = totals.get(name, 0) + game._status[i].gold
    standings = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    draw_podium(standings, output_file=output_file, bot_images=bot_images)
