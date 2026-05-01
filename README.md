# 📸 AI Photo Organizer

An AI-powered backend system that automatically organizes photos by detecting faces and grouping images of the same person using deep learning and clustering.

---

## 🚀 Overview

Managing large collections of photos is difficult and time-consuming. This project provides an intelligent solution that:

* Detects faces in uploaded images
* Generates facial embeddings using deep learning
* Groups similar faces automatically
* Organizes photos by person without manual tagging

---

## 🎯 Features

* 📤 Upload images (single / multiple / ZIP)
* 🧠 Face detection and embedding generation
* 🗂️ Automatic clustering of faces (group by person)
* ☁️ Cloud storage using Supabase
* 🧾 Room-based image organization
* 🔍 Retrieve grouped images via API

---

## 🏗️ System Architecture

```text
User → Django API → Supabase Storage → DeepFace (FaceNet)
     → Embeddings → HDBSCAN Clustering → Grouped Results
```

---

## ⚙️ Tech Stack

### Backend

* Django
* Django REST Framework

### AI / Machine Learning

* DeepFace (FaceNet)
* HDBSCAN

### Storage & Database

* Supabase Storage
* PostgreSQL / Supabase DB

### Deployment

* Render

---

## 📂 Project Structure

```bash
photo_ai/
│── photo_ai/
│   ├── settings.py
│   ├── urls.py
│
│── photos/
│   ├── views.py          # API endpoints
│   ├── models.py         # DB models
│   ├── face_utils.py     # Face embedding logic
│   ├── face_cluster.py   # Clustering logic
│   ├── supabase_client.py
│
│── manage.py
│── requirements.txt
```

---

## 🔄 Workflow

1. User uploads images with a room code
2. Images are stored in Supabase
3. Images are temporarily downloaded for processing
4. Face embeddings are generated using DeepFace
5. Embeddings are stored in the database
6. HDBSCAN clusters similar faces
7. Images are grouped by person and returned

---

## 🧪 API Endpoints

### 📤 Upload Images

```http
POST /upload/
```

**Form Data:**

* `images` (file)
* `room_code` (string)

---

### 🧠 Cluster Faces

```http
GET /cluster/?room_code=XYZ
```

**Response:**

```json
{
  "clusters": {
    "0": ["url1", "url2"],
    "1": ["url3", "url4"]
  }
}
```

---

## 📊 Results

* Automatically groups photos of the same person
* Handles multiple faces per image
* Identifies noise (unknown faces) using clustering

---

## ⚠️ Challenges

* Dependency conflicts (DeepFace, TensorFlow)
* Handling large image files
* Choosing optimal clustering algorithm
* Managing temporary files efficiently

---

## 🚀 Future Improvements

* Add authentication system
* Search photos by uploading a face
* Improve clustering accuracy
* Build frontend interface
* Optimize performance using async processing

---

## 🏁 Conclusion

This project demonstrates how AI and backend systems can be combined to solve real-world problems like photo organization. It provides a scalable and automated approach to managing large image datasets.

---

## 👤 Author

**Tanuj Pinninti**

---

