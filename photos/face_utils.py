from deepface import DeepFace

def represent_faces(image_path):
  """Return DeepFace per-face results (embedding + metadata).

  Note: `enforce_detection=False` means it will return an empty list when no face is found
  rather than raising.
  """
  try:
    result = DeepFace.represent(
      img_path=image_path,
      model_name="Facenet",
      enforce_detection=False,
    )
    return result or []
  except Exception as e:
    print("Error: ", e)
    return []

def get_face_embeddings(image_path):
  faces = represent_faces(image_path)
  return [r.get("embedding") for r in faces if isinstance(r, dict) and r.get("embedding") is not None]