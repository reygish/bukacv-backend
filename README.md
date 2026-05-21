# BukaCV Document Scanner

Small Flask API for image preprocessing (grayscale, contour detection, warp, lighten) and PDF export.

## Endpoints
- `POST /grayscale` - returns grayscale PNG
- `POST /contours` - returns PNG with detected contour
- `POST /warp` - returns warped (scanned) PNG
- `POST /lighten` - returns lightened PNG
- `POST /pdf` - returns PDF


## How the Document Scanning works
```mermaid
flowchart TD
  A[Upload image] --> B[Decode bytes into image]
  B --> C[Resize to standard height]
  C --> D[Grayscale + blur]
  D --> E[Otsu + Binary Threshold + Morphology]
  E --> F[Find contours]
  F --> G{4-point contour found?}
  G -- Yes --> H[Perspective transform]
  G -- No --> I[Fallback to image bounds]
  I --> H
  H --> J[Adaptive threshold]
  J --> K[Warped / scanned output]
```

All endpoints expect `multipart/form-data` with a file field named `image`.
