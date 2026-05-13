import os
import logging
import warnings


def _configure_ml_logging():
  # Must be set before DeepFace imports TensorFlow.
  os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
  os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

  logging.getLogger("tensorflow").setLevel(logging.ERROR)
  logging.getLogger("absl").setLevel(logging.ERROR)
  warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"tensorflow|tf_keras")


_configure_ml_logging()


def _env_bool(name: str, default: bool) -> bool:
  raw = os.environ.get(name)
  if raw is None:
    return default
  return str(raw).strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_float(name: str, default: float) -> float:
  raw = os.environ.get(name)
  if raw is None:
    return default
  try:
    return float(raw)
  except Exception:
    return default


def _env_int(name: str, default: int) -> int:
  raw = os.environ.get(name)
  if raw is None:
    return default
  try:
    return int(raw)
  except Exception:
    return default


def _env_str(name: str, default: str | None = None) -> str | None:
  raw = os.environ.get(name)
  if raw is None:
    return default
  s = str(raw)
  return s


def represent_faces(
  image_path: str,
  *,
  model_name: str = "Facenet",
  enforce_detection: bool | None = None,
  detector_backend: str | None = None,
  align: bool = True,
):
  """Return DeepFace representations as a list of dicts.

  Key defaults are chosen to avoid storing embeddings for non-faces:
  - enforce_detection defaults to env `DEEPFACE_ENFORCE_DETECTION` (default: true)
  - detector_backend can be set with env `DEEPFACE_DETECTOR_BACKEND`
  """

  if enforce_detection is None:
    enforce_detection = _env_bool("DEEPFACE_ENFORCE_DETECTION", True)

  # Default to Facenet for speed; allow override via env.
  model_name = (os.environ.get("DEEPFACE_MODEL_NAME") or model_name).strip() or model_name

  if detector_backend is None:
    detector_backend = os.environ.get("DEEPFACE_DETECTOR_BACKEND") or None

  # If not specified, prefer RetinaFace (more robust alignment) when available.
  if not detector_backend:
    detector_backend = "retinaface"

  verbose_logs = _env_bool("DEEPFACE_VERBOSE_LOGS", False)

  try:
    try:
      from deepface import DeepFace
    except Exception as imp_exc:
      if verbose_logs:
        print("DeepFace import error:", imp_exc)
      return []

    def _call(detector: str | None):
      kwargs = {}
      if detector:
        kwargs["detector_backend"] = detector
      return DeepFace.represent(
        img_path=image_path,
        model_name=model_name,
        enforce_detection=enforce_detection,
        align=align,
        **kwargs,
      )

    try:
      result = _call(detector_backend)
    except Exception as exc:
      # If the preferred detector isn't installed/available, fall back to DeepFace defaults.
      # This keeps the app working across environments.
      msg = str(exc) if exc is not None else ""
      if verbose_logs:
        print("DeepFace detector backend failed; retrying with default backend:", detector_backend, msg)
      result = _call(None)

    # DeepFace may return a dict for single-face; normalize to list.
    if isinstance(result, dict):
      return [result]
    return result or []
  except Exception as e:
    # Common case: no face detected when enforce_detection=True.
    # Don't spam logs for this; treat it as a normal "0 faces" outcome.
    msg = str(e) if e is not None else ""
    if "Face could not be detected" in msg:
      return []

    if verbose_logs:
      print("DeepFace.represent error:", e)
    return []


def _get_face_box_wh(rep: dict) -> tuple[int | None, int | None]:
  area = rep.get("facial_area") if isinstance(rep, dict) else None
  if not isinstance(area, dict):
    return (None, None)

  w = area.get("w")
  h = area.get("h")
  if w is None:
    w = area.get("width")
  if h is None:
    h = area.get("height")

  try:
    w = int(w) if w is not None else None
  except Exception:
    w = None
  try:
    h = int(h) if h is not None else None
  except Exception:
    h = None
  return (w, h)


def filter_face_representations(
  representations,
  *,
  min_confidence: float | None = None,
  min_box_size: int | None = None,
):
  """Filter weak detections.

  Defaults are env-driven so you can tune without code changes:
  - FACE_MIN_CONFIDENCE (default 0.90)  (set <=0 to disable)
  - FACE_MIN_BOX_SIZE (default 40)      (set <=0 to disable)
  """
  if min_confidence is None:
    min_confidence = _env_float("FACE_MIN_CONFIDENCE", 0.90)
  if min_box_size is None:
    min_box_size = _env_int("FACE_MIN_BOX_SIZE", 40)

  try:
    min_confidence = float(min_confidence)
  except Exception:
    min_confidence = 0.0
  try:
    min_box_size = int(min_box_size)
  except Exception:
    min_box_size = 0

  reps = representations or []
  if isinstance(reps, dict):
    reps = [reps]

  out = []
  for r in reps:
    if not isinstance(r, dict):
      continue
    emb = r.get("embedding")
    if emb is None:
      continue

    # Confidence filter (if confidence is present)
    conf = r.get("confidence")
    if conf is not None and min_confidence > 0:
      try:
        if float(conf) < min_confidence:
          continue
      except Exception:
        pass

    # Bounding-box size filter (if facial_area is present)
    if min_box_size > 0:
      w, h = _get_face_box_wh(r)
      if w is not None and h is not None:
        if w < min_box_size or h < min_box_size:
          continue

    out.append(r)

  return out


def extract_embeddings_and_meta_from_representations(
  representations,
  *,
  min_confidence: float | None = None,
  min_box_size: int | None = None,
):
  reps = filter_face_representations(
    representations,
    min_confidence=min_confidence,
    min_box_size=min_box_size,
  )
  embeddings = [r.get("embedding") for r in reps if r.get("embedding") is not None]
  face_meta = [
    {
      "confidence": r.get("confidence"),
      "facial_area": r.get("facial_area"),
    }
    for r in reps
  ]
  return embeddings, face_meta


def get_face_embeddings(image_path: str):
  faces = represent_faces(image_path)
  embeddings, _ = extract_embeddings_and_meta_from_representations(faces)
  return embeddings


def get_best_face_embedding(image_path: str):
  """Return a single embedding for the most likely face in the image."""
  faces = represent_faces(image_path)
  reps = filter_face_representations(faces)
  if not reps:
    return None

  # Prefer highest-confidence detection, otherwise keep first.
  def _score(rep: dict) -> float:
    c = rep.get("confidence")
    try:
      return float(c) if c is not None else -1.0
    except Exception:
      return -1.0

  best = max(reps, key=_score)
  return best.get("embedding")

