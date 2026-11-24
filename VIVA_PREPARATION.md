# NutriLeaf AI — Viva / Demonstration Preparation

## 60-second explanation

“My project is NutriLeaf AI, an educational plant nutrient-deficiency screening application. The user uploads or captures a leaf image. The frontend sends it to a Python FastAPI backend, which validates the image and passes it to a trained MobileNetV2 image classifier. The model returns ranked class predictions. The application displays the result with nutrient symptoms and cautious investigation guidance, and stores scan history in SQLite. The project connects plant mineral nutrition, chlorosis and other visible symptoms with machine learning and web development. It is a screening aid, not a replacement for soil or tissue testing.”

## Common viva questions

**1. What is the main aim?**  
To demonstrate how computer vision can screen leaf images for visual patterns associated with nutrient stress.

**2. Why use MobileNetV2?**  
It is a compact convolutional neural network designed for efficient image recognition and is suitable for transfer learning on a student project.

**3. What is transfer learning?**  
Using a model pretrained on a large image dataset as a starting feature extractor, then adapting it to the target classes.

**4. Why do plants need nitrogen?**  
Nitrogen is essential for amino acids, proteins, nucleic acids, and normal vegetative growth.

**5. What is chlorosis?**  
Yellowing of normally green plant tissue, commonly associated with reduced chlorophyll; it has multiple possible causes.

**6. Why can iron deficiency affect young leaves?**  
Iron is relatively immobile in many plants, so deficiency symptoms often appear in younger developing leaves, frequently as interveinal chlorosis.

**7. Why include a healthy class?**  
It gives the classifier a reference category for images labelled as healthy within the training dataset.

**8. What is a confusion matrix?**  
A table comparing actual and predicted classes, showing which categories are correctly or incorrectly classified.

**9. Why is accuracy not enough?**  
A model can achieve high overall accuracy while performing poorly on minority classes. Precision, recall, F1-score, class balance, and independent testing are also important.

**10. What is data leakage?**  
When information from the test set or closely related images influences training, causing an overly optimistic evaluation.

**11. Can a photo prove nutrient deficiency?**  
No. Visual symptoms overlap with diseases, pests, water stress, pH issues, and other deficiencies. Confirmatory soil or tissue tests are needed.

**12. What is the role of SQLite?**  
It stores scan metadata locally so the user can view history and generate summaries.

**13. What is FastAPI used for?**  
It provides API endpoints between the web interface, image-processing logic, model, and database.

**14. What happens if no trained model exists?**  
The app reports that the model is unavailable instead of generating a fabricated prediction.

**15. What are the next improvements?**  
Collect larger verified datasets, split by plant/field/session, evaluate each crop separately, calibrate uncertainty, and validate results with agronomic experts.
