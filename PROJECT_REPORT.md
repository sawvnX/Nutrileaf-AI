# NutriLeaf AI — Biology Project Report

**Project title:** AI-Based Plant Nutrient Deficiency Screening System  
**Developer:** Sawan Kumar  
**Year:** 2026

## Abstract

NutriLeaf AI is an educational web application that explores the use of computer vision for screening visible plant nutrient-stress symptoms. A user provides a leaf photograph through image upload or browser camera capture. A FastAPI backend validates the image and, when a trained model is installed, passes it to a MobileNetV2 transfer-learning classifier. The application presents the model's leading class candidates, confidence scores, relevant nutrient information, and cautious next-step guidance. Scan records are stored locally in SQLite and can be reviewed or exported.

The application is not a laboratory diagnostic system. Visual symptoms are affected by crop species, cultivar, plant age, environmental conditions, pests, pathogens, water stress, and soil chemistry. Model output must be treated as a screening clue and confirmed using appropriate soil or plant-tissue analysis.

## 1. Introduction

Plants require essential mineral elements for growth, metabolism, photosynthesis, enzyme activity, and development. When a nutrient is unavailable in sufficient quantity, plants may show visible symptoms such as chlorosis, necrosis, stunted growth, leaf deformation, or unusual pigmentation. Early recognition can help guide further investigation.

Traditional diagnosis relies on visual observation, agronomic knowledge, and laboratory testing. Computer vision can help organize visual patterns, but it cannot independently measure nutrient concentration. NutriLeaf AI demonstrates how an image-classification workflow can be integrated into a practical biology learning tool.

## 2. Objectives

1. Explain common visible symptoms associated with selected nutrient deficiencies.
2. Build a web interface for leaf image capture and upload.
3. Develop a backend API for image validation and model inference.
4. Train and evaluate a transfer-learning image classifier using labelled data.
5. Store scan history and present model metadata transparently.
6. Communicate limitations and encourage confirmatory testing.

## 3. Biological background

Nitrogen is required for amino acids, proteins, nucleic acids, and chlorophyll-associated growth. Phosphorus participates in energy transfer and nucleic acid structures. Potassium supports osmotic regulation and enzyme activation. Magnesium is central to the chlorophyll molecule and many enzyme systems. Calcium contributes to cell-wall structure and signalling. Iron is involved in electron transport and chlorophyll formation indirectly. Sulphur is a component of certain amino acids and coenzymes. Deficiency symptoms depend on nutrient mobility, crop species, developmental stage, and environmental context.

## 4. System architecture

**Frontend:** HTML, CSS, JavaScript.  
**Backend:** Python and FastAPI.  
**Image handling:** Pillow and browser camera APIs.  
**AI model:** TensorFlow/Keras MobileNetV2 transfer learning.  
**Data storage:** SQLite.

Workflow: User image → browser upload/camera → FastAPI validation → image resize and normalization in model graph → trained classifier → top candidate classes → nutrient reference content → SQLite history → dashboard/report.

## 5. Machine-learning methodology

The training pipeline expects labelled class folders. MobileNetV2 initialized with ImageNet weights acts as a feature extractor. A classification head is trained first; then the final backbone layers are selectively fine-tuned using a lower learning rate. Random horizontal flipping, rotation, and zoom augmentation improve robustness to modest image variation. Early stopping and best-checkpoint saving reduce overfitting risk.

Data is separated into training, validation, and test sets. The test set is used only for final evaluation. For research validity, images from the same plant or capture session should not be distributed across different splits. The included automatic splitter is file-level and therefore requires careful manual grouping when related images exist.

## 6. Application modules

- Overview dashboard: total scans, healthy predictions, possible deficiencies, and recent activity.
- AI scanner: crop selection, drag-and-drop, file upload, camera capture, and model-based analysis.
- Scan history: saved results, deletion, and CSV export.
- Analytics: class distribution and model evaluation status.
- Nutrient library: symptom and cause reference for seven nutrients.
- Care guide: cautious investigation steps and confirmation advice.
- About: project workflow and developer credit.

## 7. Evaluation plan

Report test accuracy, class-wise precision, recall, and F1-score, along with a confusion matrix. Discuss class imbalance, sample size, label quality, lighting variation, crop-specific generalization, and possible data leakage. Insert actual values only after training the model on the selected dataset. Do not invent performance results.

**Actual experiment fields to complete:** Dataset source/licence: __________  
Crop and classes: __________  
Number of images per class: __________  
Independent test-set design: __________  
Test accuracy: __________  
Macro precision / recall / F1: __________  
Most confused classes: __________

## 8. Limitations

A leaf photograph does not directly measure nutrient concentration. Several deficiencies and non-nutritional stresses produce similar symptoms. Results depend on the training dataset and may not generalize to other crops, cultivars, cameras, or field conditions. Softmax confidence is not necessarily calibrated. The current prototype should not be used as the sole basis for fertilizer application.

## 9. Future scope

Future research may include group-based data splitting, larger multi-location datasets, calibrated uncertainty estimates, out-of-distribution detection, disease/pest screening as a separate task, local-language guidance, and integration with laboratory soil/tissue results.

## 10. Conclusion

NutriLeaf AI connects plant nutrition concepts with computer vision and web development. It provides an end-to-end educational workflow for image capture, model inference, record keeping, and transparent reporting. Its scientific value depends on verified labels, independent evaluation, and responsible interpretation of predictions.

## References to document in final submission

Add the exact dataset paper/page, dataset licence, MobileNetV2 paper, TensorFlow/Keras documentation, FastAPI documentation, and authoritative agricultural extension sources actually consulted. Include access dates and follow your institution's citation style.
