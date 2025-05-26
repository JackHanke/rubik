import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# Load the image
img = cv2.imread("test_vids/clip.png")

# # # Resize for consistency
# height, width = img.shape[:2]
# max_dim = 600
# scale = max_dim / max(height, width)
# img = cv2.resize(img, (int(width * scale), int(height * scale)))

# # blurred = cv2.GaussianBlur(img, (5, 5), 0)
# edges = cv2.Canny(img, 50, 150)
# contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# # Make a copy for drawing
# labeled_img = img.copy()

# i = 0
# # Loop through each contour and label it
# for contour in contours:
#     area = cv2.contourArea(contour)
#     if area < 25:
#         continue
#     i += 1

#     print(i, area)

#     # Draw the contour
#     cv2.drawContours(labeled_img, [contour], -1, (0, 255, 0), 2)

#     # Compute the center of the contour
#     M = cv2.moments(contour)
#     if M["m00"] != 0:
#         cx = int(M["m10"] / M["m00"])
#         cy = int(M["m01"] / M["m00"])
#     else:
#         continue  # skip contours with zero area (just in case)

#     # Put the index number at the center
#     cv2.putText(labeled_img, str(i), (cx - 10, cy + 5), 
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

# # Show the labeled image
# cv2.imshow("Labeled Contours", labeled_img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

resized = cv2.resize(img, (600, 600))  # Optional: resize for consistency

# Step 1: Convert to HSV and create masks
hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)

# Mask for colored stickers
color_mask = cv2.inRange(hsv, (0, 100, 100), (180, 255, 255))

# Mask for white stickers (low saturation, high brightness)
# Wider range to include dim white as well
lower_white = (0, 0, 120)   # Lower value to include dimmer white
upper_white = (180, 70, 255)  # Still restrict saturation to low values (white-like)
white_mask = cv2.inRange(hsv, lower_white, upper_white)

kernel = np.ones((5, 5), np.uint8)
white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel, iterations=1)
white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel, iterations=1)


# Combine both masks
combined_mask = cv2.bitwise_or(color_mask, white_mask)

# Apply the combined mask
masked_img = cv2.bitwise_and(resized, resized, mask=combined_mask)

# Step 2: Preprocess masked image for edge detection
gray = cv2.cvtColor(masked_img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blurred, 50, 150)

# Step 3: Find contours on edge map
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Step 4: Draw contours and label them
contour_img = resized.copy()
for i, contour in enumerate(contours):
    area = cv2.contourArea(contour)
    if area < 500:
        continue  # Skip small contours

    # Draw contour
    cv2.drawContours(contour_img, [contour], -1, (0, 255, 0), 2)

    # Compute centroid and label it
    M = cv2.moments(contour)
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        cv2.putText(contour_img, str(i), (cx - 10, cy + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)  # Purple text

# Step 5: Detect and draw Hough lines (optional grid overlay)
lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=250, minLineLength=30, maxLineGap=10)
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(contour_img, (x1, y1), (x2, y2), (255, 0, 255), 1)  # Purple lines

# Step 6: Show results
cv2.imshow("Masked Image (HSV)", combined_mask)
cv2.imshow("Contours + Hough Lines", contour_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

