# This was heavily vibe coded with ChatGPT
# This script handles the display for setting landmarks

import cv2

points = []
image = None
display = None

def mouse_callback(event, x, y, flags, param):
    global points, display

    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        redraw()

def redraw():
    global display, image, points

    display = image.copy()

    for i, (x, y) in enumerate(points):
        cv2.circle(display, (x, y), 4, (0, 255, 0), -1)
        cv2.putText(
            display,
            str(i),
            (x + 5, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
            cv2.LINE_AA
        )

    cv2.imshow("Landmark Picker", display)

def main(image_path):
    global image, display, points

    points = []  # reset for each image

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Could not load image")

    display = image.copy()

    cv2.namedWindow("Landmark Picker")
    cv2.setMouseCallback("Landmark Picker", mouse_callback)

    print("\nInstructions:")
    print(" - Left click: add landmark")
    print(" - u: undo last point")
    print(" - r: reset all points")
    print(" - s: save & continue")
    print(" - q: quit without saving\n")

    while True:
        cv2.imshow("Landmark Picker", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("u") and points:
            points.pop()
            redraw()

        elif key == ord("r"):
            points = []
            redraw()

        elif key == ord("s"):
            break

        elif key == ord("q"):
            points = []
            break

    cv2.destroyAllWindows()
    return points

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python pick_landmarks.py <image_path>")
        sys.exit(1)

    main(sys.argv[1])
