import pygame
import pandas as pd
import sys
from pygame.locals import *
from shapely.geometry import Point, Polygon

image_path = "selected_frames/ingame_screenshot.jpg"
csv_path = "tracked_touch.csv"

data = pd.read_csv(csv_path)
if "class" not in data.columns:
    data["class"] = ""

class_list = [
    "Joystick", "Summon command", "Recall", "Regen", "Spell (Battle Spell)",
    "Status effect 1", "Status effect 2", "Status effect 3", "Status effect 4",
    "Skill 1", "Skill 2", "Skill 3",
    "Upgrade skill 1", "Upgrade skill 2", "Upgrade skill 3",
    "Lock enemy 1", "Lock enemy 2", "Lock enemy 3", "Lock enemy 4", "Lock enemy 5",
    "Basic attack", "Creep attack", "Tower attack", "Unique item", "Cancelation",
    "Attack command", "Retreat command", "Gather command", "Text command",
    "Shop", "KDA", "Time score", "Configuration", "On mic team", "On mic global",
    "Pin mini map", "Mini map"
]

classified_indices = set()

pygame.init()
screen = pygame.display.set_mode((1680, 720))
pygame.display.set_caption("Point Classifier with Polygon Selection")
font = pygame.font.SysFont(None, 24)

bg_image = pygame.image.load(image_path)

def draw_text(surface, text, pos, color=(255, 255, 255)):
    img = font.render(text, True, color)
    surface.blit(img, pos)

for class_name in class_list:
    remaining = data[~data.index.isin(classified_indices)]
    if remaining.empty:
        print("All points classified.")
        break

    selecting = True
    polygon_points = []

    while selecting:
        screen.blit(bg_image, (0, 0))

        for i, row in remaining.iterrows():
            pygame.draw.circle(screen, (255, 0, 0), (int(row['x']), int(row['y'])), 4)

        if len(polygon_points) > 1:
            pygame.draw.lines(screen, (0, 255, 0), False, polygon_points, 2)

        draw_text(screen, f"Class: {class_name} | Left Click = draw, Right Click = finish", (10, 10))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click = add point
                    polygon_points.append(event.pos)

                elif event.button == 3 and len(polygon_points) >= 3:  # Right click = finish
                    selecting = False

    # classify selected points
    selected_polygon = Polygon(polygon_points)
    selected_indices = []

    for i, row in remaining.iterrows():
        point = Point(row['x'], row['y'])
        if selected_polygon.contains(point):
            selected_indices.append(i)

    if selected_indices:
        data.loc[selected_indices, "class"] = class_name
        classified_indices.update(selected_indices)
        print(f"{len(selected_indices)} points labeled as '{class_name}'")

if __name__ == "__main__":
    data.to_csv(csv_path, index=False)
    print(f"\nClassification saved to: {csv_path}")
    pygame.quit()